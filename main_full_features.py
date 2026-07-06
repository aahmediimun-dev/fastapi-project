#!/usr/bin/env python3
"""
Enhanced FastAPI Application with Full Features
- User Authentication (JWT)
- Database (SQLAlchemy)
- File Upload
- Email Notifications
- Payment Processing (Stripe)
- E-commerce, Blog, Tasks, Social Features
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import stripe
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Configuration ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_key")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-password")

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== Database Setup ====================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== Database Models ====================

class User(Base):
    """User model"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    """Product model for e-commerce"""
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer)
    image_url = Column(String, nullable=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    total_price = Column(Float)
    stripe_payment_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class BlogPost(Base):
    """Blog post model"""
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class BlogComment(Base):
    """Blog comment model"""
    __tablename__ = "blog_comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("blog_posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    """Task/To-do model"""
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Follow(Base):
    """User following model"""
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# ==================== Pydantic Models ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class ProductResponse(ProductCreate):
    id: int
    seller_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=20)


class BlogPostResponse(BlogPostCreate):
    id: int
    author_id: int
    views: int
    created_at: datetime

    class Config:
        from_attributes = True


class BlogCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class BlogCommentResponse(BlogCommentCreate):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None


class TaskResponse(TaskCreate):
    id: int
    user_id: int
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Lifespan ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application with all features...")
    yield
    logger.info("Shutting down application...")


# ==================== FastAPI App ====================

app = FastAPI(
    title="Complete FastAPI Project",
    description="Full-featured FastAPI with Auth, DB, Upload, Email, Payments",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# ==================== Database Dependency ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Authentication ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ==================== Email Service ====================

async def send_email(to_email: str, subject: str, body: str):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT) as smtp:
            await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            await smtp.send_message(msg)
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


# ==================== Payment Service ====================

def create_payment(user_id: int, product_id: int, quantity: int, amount: float, db: Session) -> dict:
    """Create Stripe payment"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            metadata={"user_id": user_id, "product_id": product_id, "quantity": quantity}
        )
        
        order = Order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_price=amount,
            stripe_payment_id=intent.id,
            status="pending"
        )
        db.add(order)
        db.commit()
        
        return {
            "client_secret": intent.client_secret,
            "order_id": order.id,
            "amount": amount
        }
    except Exception as e:
        logger.error(f"Payment creation failed: {e}")
        raise HTTPException(status_code=400, detail="Payment failed")


# ==================== Authentication Endpoints ====================

@app.post("/auth/register", response_model=UserResponse, tags=["Auth"])
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send welcome email
    await send_email(
        new_user.email,
        "Welcome!",
        f"<h1>Welcome {new_user.full_name}!</h1><p>Your account has been created successfully.</p>"
    )
    
    return new_user


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/auth/me", response_model=UserResponse, tags=["Auth"])
async def get_current_user_endpoint(
    token: str = None,
    db: Session = Depends(get_db)
):
    """Get current user"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return get_current_user(token, db)


# ==================== E-Commerce Endpoints ====================

@app.post("/products", response_model=ProductResponse, tags=["E-Commerce"])
async def create_product(
    product: ProductCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Create product"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        seller_id=user.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=List[ProductResponse], tags=["E-Commerce"])
async def list_products(db: Session = Depends(get_db)):
    """List all products"""
    return db.query(Product).all()


@app.post("/orders/checkout", tags=["E-Commerce"])
async def checkout(
    order: OrderCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Create payment for order"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    product = db.query(Product).filter(Product.id == order.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    total_price = product.price * order.quantity
    
    payment_info = create_payment(user.id, product.id, order.quantity, total_price, db)
    
    return {
        "message": "Payment intent created",
        "client_secret": payment_info["client_secret"],
        "order_id": payment_info["order_id"],
        "amount": payment_info["amount"]
    }


# ==================== Blog Endpoints ====================

@app.post("/blog/posts", response_model=BlogPostResponse, tags=["Blog"])
async def create_blog_post(
    post: BlogPostCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Create blog post"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    
    new_post = BlogPost(
        title=post.title,
        content=post.content,
        author_id=user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/blog/posts", response_model=List[BlogPostResponse], tags=["Blog"])
async def list_blog_posts(db: Session = Depends(get_db)):
    """List all blog posts"""
    return db.query(BlogPost).all()


@app.post("/blog/posts/{post_id}/comments", response_model=BlogCommentResponse, tags=["Blog"])
async def add_comment(
    post_id: int,
    comment: BlogCommentCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Add comment to blog post"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = BlogComment(
        post_id=post_id,
        author_id=user.id,
        content=comment.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# ==================== Task Endpoints ====================

@app.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(
    task: TaskCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Create task"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    
    new_task = Task(
        user_id=user.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(
    token: str = None,
    db: Session = Depends(get_db)
):
    """Get user's tasks"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    return db.query(Task).filter(Task.user_id == user.id).all()


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_id: int,
    task_update: TaskCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Update task"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = task_update.title
    task.description = task_update.description
    task.priority = task_update.priority
    task.due_date = task_update.due_date
    db.commit()
    db.refresh(task)
    return task


@app.patch("/tasks/{task_id}/complete", tags=["Tasks"])
async def complete_task(
    task_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Mark task as complete"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(token, db)
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.completed = True
    db.commit()
    return {"message": "Task completed"}


# ==================== Social Endpoints ====================

@app.post("/users/{user_id}/follow", tags=["Social"])
async def follow_user(
    user_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    current_user = get_current_user(token, db)
    
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following
    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already following")
    
    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()
    
    return {"message": "User followed"}


@app.get("/users/{user_id}/followers", tags=["Social"])
async def get_followers(user_id: int, db: Session = Depends(get_db)):
    """Get user's followers"""
    followers = db.query(Follow).filter(Follow.following_id == user_id).all()
    return {"count": len(followers), "followers": followers}


# ==================== File Upload ====================

@app.post("/upload", tags=["Files"])
async def upload_file(
    file: UploadFile = File(...),
    token: str = None,
    db: Session = Depends(get_db)
):
    """Upload file"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    get_current_user(token, db)
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)
    
    return {
        "filename": file.filename,
        "path": file_path,
        "size": len(contents)
    }


# ==================== Health & Status ====================

@app.get("/health", tags=["Status"])
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "Authentication",
            "Database",
            "File Upload",
            "Email Notifications",
            "Payment Processing",
            "E-commerce",
            "Blog",
            "Tasks",
            "Social Features"
        ]
    }


@app.get("/", tags=["Status"])
async def root():
    """Root endpoint"""
    return {
        "message": "Complete FastAPI Project v2.0.0",
        "docs": "/docs",
        "features": "Auth, DB, Upload, Email, Payments, E-commerce, Blog, Tasks, Social"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
