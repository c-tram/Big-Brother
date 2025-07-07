# MLB Analytics Mobile App - Default Login Information

## 🔐 Default User Accounts

Your MLB Analytics app comes with two pre-created accounts for testing:

### **Admin Account (Superuser)**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@mlbanalytics.com`
- **Privileges**: Full admin access

### **Test Account (Regular User)**
- **Username**: `testuser`
- **Password**: `test123`
- **Email**: `test@mlbanalytics.com`
- **Privileges**: Regular user access

## 📱 How to Login

1. **Open your MLB Analytics app** on your iPhone via Expo Go
2. **Navigate to the Login screen**
3. **Enter one of the credentials above**:
   - You can use either **username** OR **email** in the email field
   - Examples:
     - Email field: `testuser` or `test@mlbanalytics.com`
     - Password field: `test123`
4. **Tap Login**

## ✅ **Authentication Fixed!**

The authentication endpoints have been updated to match the React Native app format. You should now be able to login successfully with:

- **Username**: `testuser` **Password**: `test123` 
- **Username**: `admin` **Password**: `admin123`
- **Email**: `test@mlbanalytics.com` **Password**: `test123`
- **Email**: `admin@mlbanalytics.com` **Password**: `admin123`

## 🌐 Django Admin Access

You can also access the Django admin interface in your browser:

- **URL**: `http://10.0.0.22:8000/admin/`
- **Use the admin credentials**: `admin` / `admin123`

## 🛠 Creating New Users

### Via Django Admin
1. Go to `http://10.0.0.22:8000/admin/`
2. Login with admin credentials
3. Click "Users" → "Add User"

### Via Django Shell
```bash
cd /Users/coletrammell/Documents/GitHub/Big-Brother/mlb-analytics-backend/src
source venv/bin/activate
python manage.py shell
```

```python
from django.contrib.auth.models import User
User.objects.create_user('newuser', 'email@example.com', 'password123')
```

## 🔄 Auto-Setup

The `start-mlb-app.sh` script automatically:
- ✅ Runs database migrations
- ✅ Creates default users if they don't exist
- ✅ Sets up the complete environment

## 🎯 Test Your Login

**Recommended testing flow:**
1. Start with `testuser` / `test123` for regular user experience
2. Use `admin` / `admin123` for admin features (if implemented)

Your app should now accept these credentials and redirect you to the main dashboard!
