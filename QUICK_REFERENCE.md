# Quick Reference Guide

## 🚀 Starting the App

### Quick Start (All-in-One)
```bash
# Windows
run.bat

# macOS/Linux
./run.sh
```

### Manual Start
```bash
# Activate virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Start backend
python app.py

# In another terminal, serve frontend
python -m http.server 8001
```

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Frontend | `http://localhost:8001` or open `index.html` directly |
| Backend API | `http://localhost:8000` |
| API Documentation | `http://localhost:8000/docs` |
| API Health | `http://localhost:8000/api/health` |

---

## 📦 Dependencies Installation

```bash
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install requirements
pip install -r requirements.txt

# Update/Upgrade a package
pip install --upgrade fastapi
```

---

## 🧪 Testing with cURL

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "company_name": "ACME Corp",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123"
  }'
```

**Save the token from response:**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR..."
```

### Get Dashboard Stats
```bash
curl -X GET http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"
```

### Get Invoices
```bash
curl -X GET http://localhost:8000/api/invoices \
  -H "Authorization: Bearer $TOKEN"
```

### Upload Invoice
```bash
curl -X POST http://localhost:8000/api/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@invoice.pdf" \
  -F "amount=1500.00" \
  -F "invoice_date=2024-01-15"
```

### Delete Invoice
```bash
curl -X DELETE http://localhost:8000/api/invoices/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Update Invoice Status
```bash
curl -X PUT http://localhost:8000/api/invoices/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "paid"}'
```

---

## 💾 Database Management

### SQLite (Default)
```bash
# View database
sqlite3 invoice_app.db

# List tables
.tables

# View data
SELECT * FROM users;

# Reset database (delete file)
rm invoice_app.db
```

### PostgreSQL
```bash
# Connect to database
psql -U postgres -d invoice_db

# Create database
createdb invoice_db

# Backup database
pg_dump -U postgres invoice_db > backup.sql

# Restore database
psql -U postgres invoice_db < backup.sql
```

### MySQL
```bash
# Connect to database
mysql -u root -p invoice_db

# Create database
CREATE DATABASE invoice_db;

# Backup database
mysqldump -u root -p invoice_db > backup.sql

# Restore database
mysql -u root -p invoice_db < backup.sql
```

---

## 🔐 Environment Variables

```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy output to .env:
SECRET_KEY=your-output-here
```

---

## 🐳 Docker Commands

### Build Image
```bash
docker build -t invoice-app .
```

### Run Container
```bash
docker run -p 8000:8000 invoice-app
```

### Using Docker Compose
```bash
# Start all services (backend + database)
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend
```

---

## 🛠️ Development Commands

### Run Backend in Development Mode
```bash
# With auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest test_example.py -v

# Run with coverage
pip install pytest-cov
pytest test_example.py --cov=app
```

### Format Code
```bash
# Install formatter
pip install black

# Format all Python files
black .
```

### Check Code Quality
```bash
# Install linter
pip install flake8

# Check code
flake8 .
```

---

## 📝 File Locations

| What | Where |
|------|-------|
| Backend code | `app.py`, `models.py`, `database.py`, `auth.py` |
| Frontend | `index.html`, `app.js`, `styles.css` |
| Configuration | `.env` |
| Database (SQLite) | `invoice_app.db` |
| Uploaded files | `uploads/` folder |
| Dependencies | `requirements.txt` |

---

## 🔍 Debugging

### Check if Backend is Running
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"ok","message":"Invoice App is running"}
```

### Check if Frontend is Running
```bash
# Open in browser
http://localhost:8001
# Or open index.html directly
```

### View Backend Logs
```bash
# Logs appear in terminal where you ran: python app.py
```

### View Frontend Errors
```bash
# Open browser Developer Tools: F12 or Ctrl+Shift+I
# Check Console tab for JavaScript errors
# Check Network tab for API calls
```

### Clear Browser Cache
```bash
# Most browsers: Ctrl+Shift+Del (or Cmd+Shift+Del on Mac)
# Then select "Cached images and files"
```

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Edit `app.py` change port to 9000, or kill process using port |
| Module not found | Make sure venv is activated with `source venv/bin/activate` |
| CORS error | Backend and frontend must be on different ports |
| Database error | Make sure database is running and .env has correct credentials |
| Token expired | Login again to get new token |
| Frontend blank | Open browser console (F12) to see errors |
| File upload fails | Check file size limit (default 10MB) in .env |

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Invoices Table
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL FOREIGN KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    amount DECIMAL(12, 2),
    invoice_date DATE,
    status VARCHAR(50) DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔗 Useful Links

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy ORM**: https://www.sqlalchemy.org
- **Chart.js Documentation**: https://www.chartjs.org
- **REST API Best Practices**: https://restfulapi.net
- **JWT Tokens**: https://jwt.io
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html

---

## 💡 Tips & Tricks

### Auto-format on Save (VS Code)
Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

### Ignore Python Cache Files
Create `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
*.db
uploads/
```

### Quick Database Reset
```bash
# Delete database file (SQLite only)
rm invoice_app.db

# Restart app - new database will be created
python app.py
```

### Test User Isolation
- Create 2 accounts
- Login as User A, upload invoices
- Login as User B - should NOT see User A's invoices
- This is important for security!

---

## 🎓 Learning Path

1. **Understand the structure**: Read `README.md` first
2. **Run the app**: Use `run.sh` or `run.bat`
3. **Create account**: Use the UI to sign up
4. **Test with API**: Use cURL commands to understand the flow
5. **Read the code**: Start with `app.py` to understand FastAPI
6. **Customize**: Modify `styles.css` to change colors
7. **Add features**: Look at `app.js` to understand frontend
8. **Deploy**: Follow `SETUP_GUIDE.md` for production

---

Happy coding! 🚀

Need help? Check README.md or run the app and open http://localhost:8000/docs for API documentation.
