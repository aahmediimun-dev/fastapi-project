from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from pydantic import BaseModel
import os
import shutil
from dotenv import load_dotenv

from database import engine, get_db, Base
from models import User, Invoice
from auth import hash_password, verify_password, create_access_token, verify_token

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Invoice Dashboard API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads folder
os.makedirs("uploads", exist_ok=True)

# ==================== Pydantic Models ====================
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    company_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class InvoiceResponse(BaseModel):
    id: int
    filename: str
    amount: float
    invoice_date: str
    status: str
    uploaded_at: str

# ==================== Auth Routes ====================
@app.post("/api/auth/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    hashed_pwd = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pwd,
        company_name=user.company_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "company_name": new_user.company_name
    }

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    access_token = create_access_token(data={"sub": db_user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username
    }

# ==================== Invoice Routes ====================
@app.post("/api/invoices/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    amount: float = Form(...),
    invoice_date: str = Form(...),
    user_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Upload an invoice file"""
    try:
        # Create user folder
        user_folder = f"uploads/{user_id}"
        os.makedirs(user_folder, exist_ok=True)
        
        # Save file
        file_path = f"{user_folder}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create invoice record
        invoice = Invoice(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            amount=amount,
            invoice_date=invoice_date,
            status="pending"
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        return {
            "id": invoice.id,
            "filename": invoice.filename,
            "amount": invoice.amount,
            "invoice_date": invoice.invoice_date.isoformat(),
            "status": invoice.status,
            "uploaded_at": invoice.uploaded_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/invoices")
def get_invoices(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    """Get all invoices for logged-in user"""
    invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
    return [
        {
            "id": inv.id,
            "filename": inv.filename,
            "amount": inv.amount,
            "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
            "status": inv.status,
            "uploaded_at": inv.uploaded_at.isoformat()
        }
        for inv in invoices
    ]

@app.delete("/api/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    user_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete an invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete file
    try:
        if os.path.exists(invoice.file_path):
            os.remove(invoice.file_path)
    except:
        pass
    
    db.delete(invoice)
    db.commit()
    
    return {"detail": "Invoice deleted"}

@app.put("/api/invoices/{invoice_id}")
def update_invoice(
    invoice_id: int,
    status: str,
    user_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Update invoice status"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if status not in ["pending", "paid", "overdue"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    invoice.status = status
    db.commit()
    
    return {"id": invoice.id, "status": invoice.status}

# ==================== Dashboard Routes ====================
@app.get("/api/dashboard/stats")
def dashboard_stats(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
    
    total_amount = sum(inv.amount for inv in invoices if inv.amount)
    pending_count = sum(1 for inv in invoices if inv.status == "pending")
    paid_count = sum(1 for inv in invoices if inv.status == "paid")
    overdue_count = sum(1 for inv in invoices if inv.status == "overdue")
    
    return {
        "total_invoices": len(invoices),
        "total_amount": total_amount,
        "pending": pending_count,
        "paid": paid_count,
        "overdue": overdue_count,
        "invoices": [
            {
                "id": inv.id,
                "filename": inv.filename,
                "amount": inv.amount,
                "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else None,
                "status": inv.status,
                "uploaded_at": inv.uploaded_at.isoformat()
            }
            for inv in invoices
        ]
    }

@app.get("/api/user/profile")
def get_profile(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    """Get user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "company_name": user.company_name,
        "created_at": user.created_at.isoformat()
    }

# ==================== Health Check ====================
@app.get("/api/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Invoice App is running"}

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Invoice Dashboard API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
