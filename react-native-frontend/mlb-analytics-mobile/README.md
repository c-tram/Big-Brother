# MLB Analytics Mobile App

A comprehensive React Native mobile application for baseball analytics, built with Expo and TypeScript. This app connects to a Django backend with ~95% MLB API coverage to provide users with detailed baseball statistics, real-time data, and natural language search capabilities.

## Features

### 🏟️ Core Functionality
- **User Authentication**: Secure login and registration system
- **Natural Language Search**: Ask questions about baseball data in plain English
- **Customizable Dashboard**: Widget-based home screen with personalized content
- **Player Profiles**: Detailed statistics and performance analytics
- **Team Information**: Comprehensive team stats, schedules, and standings
- **Favorites Management**: Save and track favorite players and teams

### 📊 Analytics & Data
- Real-time MLB standings
- Player batting, pitching, and fielding statistics
- Team performance metrics
- Recent and upcoming game information
- Interactive charts and visualizations
- Advanced analytics leveraging comprehensive backend API

### 🎨 User Experience
- Modern Material Design UI with React Native Paper
- Responsive design for various screen sizes
- Dark/light theme support
- Offline caching for improved performance
- Pull-to-refresh functionality
- Search history and suggestions

## Tech Stack

### Frontend
- **React Native** with **Expo** - Cross-platform mobile development
- **TypeScript** - Type-safe development
- **React Navigation** - Navigation system
- **React Native Paper** - Material Design components
- **Zustand** - State management with persistence
- **React Query** - Server state management and caching
- **React Native Chart Kit** - Data visualization
- **Expo Secure Store** - Secure token storage

### Backend Integration
- Django REST API with comprehensive MLB data coverage
- JWT authentication
- Real-time data synchronization
- Natural language processing for search queries

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── widgets/        # Dashboard widgets
├── hooks/              # Custom React hooks
├── navigation/         # Navigation configuration
├── screens/            # Screen components
│   ├── auth/          # Authentication screens
│   ├── home/          # Dashboard/home screen
│   ├── search/        # Search functionality
│   ├── player/        # Player profile screen
│   ├── team/          # Team details screen
│   ├── favorites/     # Favorites management
│   └── settings/      # App settings
├── services/          # API and external services
├── store/             # Zustand state management
├── types/             # TypeScript type definitions
└── utils/             # Utility functions and helpers
```

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Expo CLI
- iOS Simulator or Android emulator (for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd react-native-frontend/mlb-analytics-mobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Run on device/simulator**
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app on your device

### Environment Configuration

Create a `.env` file in the project root:
```env
API_BASE_URL=http://your-django-backend-url/api
```

## Key Features Implemented

### 🔐 Authentication System
- Secure login and registration
- JWT token management
- Persistent authentication state
- Password validation and user feedback

### 🏠 Customizable Dashboard
- Widget-based interface
- Drag-and-drop widget arrangement
- Real-time data updates
- Personal favorites integration

### 🔍 Advanced Search
- Natural language query processing
- Player and team search
- Search history and suggestions
- Instant results with relevance scoring

### 📱 Screen Components
- **LoginScreen**: User authentication with form validation
- **RegisterScreen**: New user registration
- **HomeScreen**: Customizable dashboard with widgets
- **SearchScreen**: Natural language search interface
- **PlayerProfileScreen**: Detailed player statistics and charts
- **TeamDetailsScreen**: Team information, roster, and schedule
- **FavoritesScreen**: Manage favorite players and teams
- **SettingsScreen**: User preferences and app configuration

### 🧩 Reusable Widgets
- **StandingsWidget**: League standings display
- **PlayerStatsWidget**: Player performance metrics
- **TeamStatsWidget**: Team statistics overview
- **RecentGamesWidget**: Latest game results

## State Management

The app uses Zustand for state management with the following stores:

- **AuthStore**: User authentication and profile data
- **DashboardStore**: Widget configuration and layout
- **SearchStore**: Search history and cached results
- **FavoritesStore**: User's favorite players and teams
- **MLBDataStore**: Cached baseball data with TTL

## API Integration

The app integrates with a comprehensive Django backend featuring:

- Player profiles and statistics
- Team information and schedules
- Real-time game data
- League standings
- Advanced analytics
- Natural language search processing
- User preferences and favorites sync

## Development Features

### 🛠 Development Tools
- TypeScript for type safety
- ESLint for code quality
- React Query for efficient data fetching
- AsyncStorage for offline persistence
- Expo development tools

### 📊 Performance Optimizations
- Data caching with TTL
- Lazy loading of screens
- Optimized re-renders with React.memo
- Efficient list rendering with FlatList
- Background data synchronization

## Future Enhancements

- Push notifications for game updates
- Live game tracking
- Social features (sharing stats, discussions)
- Advanced charting and visualizations
- Offline mode improvements
- Widget marketplace
- Fantasy baseball integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions about the app, please refer to the documentation or create an issue in the repository.
