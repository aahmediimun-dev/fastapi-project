# Invoice Dashboard Application

A complete multi-user web application where businesses can upload invoices, view dashboards, and manage accounts with JWT authentication.

## ✨ Features

✅ **User Authentication** - Secure login/registration with JWT tokens  
✅ **Invoice Management** - Upload, view, delete, and manage invoices  
✅ **Dashboard** - Real-time statistics and visual charts  
✅ **Multi-user** - Each user only sees their own invoices  
✅ **Responsive Design** - Works on desktop and mobile  
✅ **File Upload** - Support for PDF, DOC, XLSX files  
✅ **Status Tracking** - Mark invoices as Pending, Paid, or Overdue  
✅ **Database** - Uses SQLite (default), PostgreSQL, or MySQL  

## 🚀 Quick Start (30 seconds)

### Windows
```bash
run.bat
```

### macOS / Linux
```bash
chmod +x run.sh
./run.sh
```

Then open `index.html` in your web browser.

---

## 📋 Manual Setup (if run.sh doesn't work)

### 1. Prerequisites
- Python 3.9 or higher
- Git (optional)

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Run Backend
```bash
# Make sure venv is activated
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### 4. Run Frontend
In a new terminal, open the project folder and double-click `index.html` OR:

```bash
# Using Python's built-in server
cd path/to/project
python -m http.server 8001
```

Then open: `http://localhost:8001`

---

## 🧪 Test the Application

### 1. Create Account
- Click "Sign Up"
- Fill in:
  - Username: `testuser`
  - Email: `test@example.com`
  - Company: `Test Corp`
  - Password: `password123`
- Click "Sign Up"

### 2. Login
- Username: `testuser`
- Password: `password123`
- Click "Login"

### 3. Upload Invoice
- Click "Upload New Invoice"
- Select a file (any file works for testing)
- Amount: `1500.00`
- Date: Today
- Click "Upload"

### 4. View Dashboard
- See stats update
- View invoice in table
- Chart shows invoice status distribution

---

## 📁 Project Structure

```
invoice-app/
├── app.py              # Main FastAPI application
├── models.py           # SQLAlchemy models (User, Invoice)
├── database.py         # Database configuration
├── auth.py             # JWT authentication
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── index.html          # Frontend HTML
├── app.js              # Frontend JavaScript
├── styles.css          # Frontend CSS
├── run.sh              # Quick start (macOS/Linux)
├── run.bat             # Quick start (Windows)
├── uploads/            # Uploaded files (auto-created)
└── README.md           # This file
```

---

## 🔧 Configuration

### Using SQLite (Default - No setup needed!)
The app uses SQLite by default, which creates a local database file automatically.

### Using PostgreSQL
```bash
# Install PostgreSQL, then update .env:
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=invoice_db
```

### Using MySQL
```bash
# Install MySQL, then update .env:
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=invoice_db
```

---

## 🔐 Security

### Change Secret Key
⚠️ **IMPORTANT**: Before deploying, change the SECRET_KEY in `.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and update `.env`:
```
SECRET_KEY=your-new-secret-key
```

---

## 📊 API Endpoints

All endpoints require JWT token in header (except auth endpoints):
```
Authorization: Bearer {token}
```

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login and get token

### Invoices
- `POST /api/invoices/upload` - Upload invoice
- `GET /api/invoices` - List user's invoices
- `DELETE /api/invoices/{id}` - Delete invoice
- `PUT /api/invoices/{id}` - Update invoice status

### Dashboard
- `GET /api/dashboard/stats` - Get statistics

### Other
- `GET /api/health` - Health check
- `GET /api/user/profile` - Get user profile

**API Documentation** (when backend is running):
```
http://localhost:8000/docs
```

---

## 🐛 Troubleshooting

### "Port 8000 already in use"
Another app is using port 8000. Either:
- Close the other app, or
- Edit `app.py` line: `port=8000` to `port=9000`

### "Module not found"
Make sure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### "Database error"
If using PostgreSQL/MySQL, make sure:
1. Database server is running
2. Credentials in `.env` are correct
3. Database exists (create it first)

### "CORS error" in browser
Backend and frontend must be on different ports:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8001` or open `index.html` directly

### "Cannot find index.html"
Make sure you:
1. Open `index.html` from the project folder
2. OR run Python http server: `python -m http.server 8001`
3. NOT from the root directory with no file server

---

## 🚀 Production Deployment

### Option 1: Heroku (Easiest)
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
heroku login
heroku create invoice-app
git push heroku main
```

### Option 2: DigitalOcean, AWS, GCP
See `SETUP_GUIDE.md` for detailed instructions.

### Option 3: Docker
```bash
docker build -t invoice-app .
docker run -p 8000:8000 invoice-app
```

---

## 📞 Support

### Common Issues

**Q: Why is the frontend not connecting to backend?**
A: Make sure backend is running on `http://localhost:8000` and the API URL in `app.js` matches.

**Q: How do I reset all data?**
A: Delete `invoice_app.db` file and restart the app.

**Q: Can I use a different database?**
A: Yes! See Configuration section above.

**Q: How do I add more users?**
A: Each user can register from the Sign Up form.

---

## 📚 File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Main FastAPI backend - handles all routes |
| `models.py` | Database models (User, Invoice tables) |
| `database.py` | Database connection setup |
| `auth.py` | JWT authentication & password hashing |
| `index.html` | Single-page app frontend |
| `app.js` | All frontend logic (auth, upload, dashboard) |
| `styles.css` | Complete styling & responsive design |
| `requirements.txt` | Python package dependencies |
| `.env` | Configuration (database, secret key, etc.) |

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://www.sqlalchemy.org
- **JWT Tutorial**: https://jwt.io
- **HTML/CSS/JS**: https://developer.mozilla.org

---

## 📝 License

This project is open source and available for educational and commercial use.

---

## 🎉 Congratulations!

You now have a fully functional invoice management application!

**Next steps:**
1. Test uploading invoices
2. Customize the UI in `styles.css`
3. Add more features (export to PDF, email notifications, etc.)
4. Deploy to production

Happy coding! 🚀
