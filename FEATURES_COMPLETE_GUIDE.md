# 🚀 COMPLETE FASTAPI FEATURES GUIDE

## Overview of All Features

This FastAPI project includes ALL of the following:

1. ✅ **User Authentication** - JWT-based login/register
2. ✅ **Database** - SQLAlchemy ORM with SQLite/PostgreSQL
3. ✅ **File Upload** - Upload images, documents, etc.
4. ✅ **Email Notifications** - Send emails via SMTP
5. ✅ **Payment Processing** - Stripe integration
6. ✅ **E-Commerce** - Products, orders, checkout
7. ✅ **Blog** - Posts and comments
8. ✅ **Task Manager** - To-do lists with priorities
9. ✅ **Social Features** - Follow users, interactions

---

## 📁 FILES TO USE

Use THESE new files for the complete version:

```
✓ main_full_features.py      → Replace main.py
✓ index_full_features.html   → Replace index.html
✓ requirements_full.txt      → Replace requirements.txt
✓ .env_full.example          → Copy to .env
```

---

## 🔧 SETUP INSTRUCTIONS

### Step 1: Replace Files
```bash
# Backup original files (optional)
mv main.py main_backup.py
mv index.html index_backup.html

# Use the new files
cp main_full_features.py main.py
cp index_full_features.html index.html
cp requirements_full.txt requirements.txt
cp .env_full.example .env
```

### Step 2: Update Environment Variables
```bash
# Edit .env file with your settings:

# Email Configuration
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_key

# Secret Key (change this!)
SECRET_KEY=your-new-secret-key-12345
```

### Step 3: Install New Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
# Windows
startup_windows.bat

# Mac/Linux
./startup_macos_linux.sh
```

---

## 🔐 AUTHENTICATION FEATURE

### How It Works:
- Users register with username, email, password
- Login returns JWT token
- All protected endpoints need token in header

### API Examples:

#### Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "SecurePass123"
  }'

Response:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-10T10:30:00"
}
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Using Token in Headers
```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Get Current User
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 💾 DATABASE FEATURE

### Models Included:
- **User** - User accounts
- **Product** - E-commerce products
- **Order** - Customer orders
- **BlogPost** - Blog articles
- **BlogComment** - Comments on posts
- **Task** - To-do items
- **Follow** - User relationships

### Database Queries (Python):
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User, Product, Task

# Connect to database
engine = create_engine("sqlite:///./app.db")
Session = sessionmaker(bind=engine)
session = Session()

# Get all users
all_users = session.query(User).all()

# Get specific user
user = session.query(User).filter(User.username == "john_doe").first()

# Get user's tasks
user_tasks = session.query(Task).filter(Task.user_id == user.id).all()

# Create new product
new_product = Product(
    name="Laptop",
    description="High-end laptop",
    price=1299.99,
    stock=5,
    seller_id=user.id
)
session.add(new_product)
session.commit()
```

### Switch to PostgreSQL (Production):
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db

# The code will automatically use PostgreSQL
```

---

## 📧 EMAIL NOTIFICATIONS FEATURE

### Configuration (Gmail Example):

1. Enable 2-Factor Authentication on Gmail
2. Create App Password: https://myaccount.google.com/apppasswords
3. Update .env:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### How It Works:
- Sends welcome email on registration
- Can send notifications for orders, messages, etc.

### Python Code to Send Custom Email:
```python
from main import send_email

# Send email
await send_email(
    to_email="user@example.com",
    subject="Your Order Confirmation",
    body="<h1>Order Confirmed!</h1><p>Your order #12345 has been confirmed.</p>"
)
```

### Supported Email Providers:
- Gmail
- Office 365
- SendGrid
- Custom SMTP servers

---

## 💳 PAYMENT PROCESSING (STRIPE)

### Setup:

1. Create Stripe account: https://stripe.com
2. Get API keys from dashboard
3. Update .env:
```
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_PUBLIC_KEY=pk_test_your_public_key
```

### API Examples:

#### Create Payment Intent
```bash
curl -X POST "http://localhost:8000/orders/checkout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

Response:
{
  "message": "Payment intent created",
  "client_secret": "pi_1A2B3C4D5E6F_secret_xyz...",
  "order_id": 42,
  "amount": 2599.98
}
```

### Frontend JavaScript (Stripe Elements):
```html
<script src="https://js.stripe.com/v3/"></script>

<div id="card-element"></div>
<button onclick="submitPayment()">Pay Now</button>

<script>
const stripe = Stripe('pk_test_your_public_key');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');

async function submitPayment() {
  // Get client secret from server
  const clientSecret = "pi_1A2B3C_secret_xyz";
  
  const result = await stripe.confirmCardPayment(clientSecret, {
    payment_method: {
      card: cardElement
    }
  });

  if (result.paymentIntent.status === 'succeeded') {
    alert('Payment successful!');
  }
}
</script>
```

---

## 🛍️ E-COMMERCE FEATURE

### Create Product
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 10
  }'
```

### List Products
```bash
curl "http://localhost:8000/products"
```

### Place Order
```bash
curl -X POST "http://localhost:8000/orders/checkout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

---

## 📝 BLOG FEATURE

### Create Blog Post
```bash
curl -X POST "http://localhost:8000/blog/posts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my blog post..."
  }'
```

### List Posts
```bash
curl "http://localhost:8000/blog/posts"
```

### Add Comment
```bash
curl -X POST "http://localhost:8000/blog/posts/1/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "Great post!"
  }'
```

---

## ✅ TASK MANAGER FEATURE

### Create Task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "high",
    "due_date": "2024-01-15T18:00:00"
  }'
```

### Get Your Tasks
```bash
curl "http://localhost:8000/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Buy groceries",
    "priority": "medium",
    "description": "Updated list"
  }'
```

### Mark Task Complete
```bash
curl -X PATCH "http://localhost:8000/tasks/1/complete" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 👥 SOCIAL FEATURES

### Follow User
```bash
curl -X POST "http://localhost:8000/users/2/follow" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get User's Followers
```bash
curl "http://localhost:8000/users/1/followers"
```

---

## 📤 FILE UPLOAD

### Upload File
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/file.pdf"

Response:
{
  "filename": "file.pdf",
  "path": "uploads/file.pdf",
  "size": 102400
}
```

---

## 🌐 FRONTEND DASHBOARD

The HTML dashboard (`index_full_features.html`) includes:

### Tabs:
1. **Dashboard** - Overview with user info
2. **Auth** - Login/Register
3. **E-Commerce** - Create products
4. **Blog** - Write posts, view comments
5. **Tasks** - Create and manage tasks
6. **Social** - Follow users

### Usage:
1. Open `http://localhost:8000` in browser
2. Click "Auth" tab
3. Register a new account
4. Login
5. Explore other tabs with your token

---

## 🧪 TESTING FEATURES

### Test with Postman:

1. Download Postman: https://postman.com
2. Create new collection
3. Import endpoints
4. Add Authorization header: `Bearer YOUR_TOKEN`
5. Test each endpoint

### Python Testing:
```python
import requests

BASE_URL = "http://localhost:8000"

# Register
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "TestPass123"
    }
)

# Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "testuser",
        "password": "TestPass123"
    }
)

token = login_response.json()["access_token"]

# Create task
tasks_response = requests.post(
    f"{BASE_URL}/tasks",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "title": "Test Task",
        "priority": "high"
    }
)

print(tasks_response.json())
```

---

## 🚀 DEPLOYMENT

### Deploy to Heroku:
```bash
# Create Heroku app
heroku login
heroku create my-fastapi-app

# Push code
git push heroku main

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set STRIPE_SECRET_KEY=sk_test_xxx

# View logs
heroku logs --tail
```

### Deploy to AWS:
```bash
# Use Docker (already configured)
docker build -t my-fastapi .
docker run -p 8000:8000 my-fastapi

# Or use docker-compose
docker-compose up -d
```

---

## 📊 API DOCUMENTATION

### Interactive Docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Try Endpoints:
1. Open http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"
5. See the response

---

## 🔒 SECURITY BEST PRACTICES

```python
# In production .env:
DEBUG=False
SECRET_KEY=use-strong-random-key-here-not-this-one
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## 📞 TROUBLESHOOTING

### "Email failed to send"
- Check SMTP credentials in .env
- Enable "Less secure apps" (Gmail)
- Try app-specific password

### "Stripe payment failed"
- Verify STRIPE_SECRET_KEY in .env
- Check Stripe account has test mode enabled
- Use Stripe test card: 4242 4242 4242 4242

### "Authentication failed"
- Ensure token is in Authorization header
- Token format: `Bearer YOUR_TOKEN_HERE`
- Token expires after 30 minutes (default)

---

## 🎯 NEXT STEPS

1. ✅ Update .env with real credentials
2. ✅ Test each feature on dashboard
3. ✅ Customize for your use case
4. ✅ Deploy to production
5. ✅ Monitor with logs/alerts

---

Happy coding! 🚀
