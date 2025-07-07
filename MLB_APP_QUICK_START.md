# MLB Analytics Mobile App - Quick Start Scripts

## 🚀 Quick Start

### Start the Complete App
```bash
./start-mlb-app.sh
```

This script will:
- ✅ Start Django backend on `http://localhost:8000`
- ✅ Start React Native frontend with Expo
- ✅ Clean up any existing processes
- ✅ Set up virtual environment if needed
- ✅ Install dependencies if needed
- ✅ Display QR code for Expo Go testing

### Stop the App
```bash
./stop-mlb-app.sh
```

This script will:
- 🛑 Stop Django server (port 8000)
- 🛑 Stop Expo server (port 8081)
- 🛑 Stop Metro bundler (port 8082)
- 🛑 Clean up all related processes

## 📱 Testing on iPhone

1. **Download Expo Go** from the iOS App Store
2. **Run the start script**: `./start-mlb-app.sh`
3. **Scan QR code** with Expo Go app
4. **Test your MLB Analytics app!**

## 🔧 Manual Commands

If you prefer to start services manually:

### Django Backend
```bash
cd mlb-analytics-backend/src
source venv/bin/activate
python manage.py runserver 8000
```

### React Native Frontend
```bash
cd react-native-frontend/mlb-analytics-mobile
npx expo start --go
```

## 📊 Services Overview

- **Django Backend**: Full MLB API with 95% coverage
- **React Native Frontend**: Mobile app with natural language search
- **Features**: Dashboard widgets, player profiles, team stats, favorites

## 🎯 Features Available

✅ Authentication system
✅ Customizable dashboard with 4 widget types
✅ Natural language search ("Who leads in home runs?")
✅ Player profiles with statistics and charts
✅ Team details with schedules and rosters
✅ Favorites management
✅ Settings and preferences
✅ Real-time data from MLB API
✅ Offline caching

Your complete MLB Analytics mobile app is ready to use!
