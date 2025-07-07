# MLB Analytics Mobile - Development Guide

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- npm or yarn
- Expo CLI
- iOS Simulator or Android emulator

### Setup
```bash
cd react-native-frontend/mlb-analytics-mobile
npm install
npm start
```

## 📱 App Architecture

### Core Features Implemented
✅ **Authentication System**
- Login/Register screens with validation
- JWT token management
- Persistent authentication state
- Secure token storage

✅ **Navigation Structure**
- Bottom tab navigation
- Stack navigation for details
- Authentication flow
- Type-safe navigation

✅ **Dashboard System**
- Customizable widget-based interface
- Real-time data updates
- Widget management (add/remove/reorder)
- Responsive layout

✅ **Search Functionality**
- Natural language search integration
- Player and team search
- Search history
- Instant results

✅ **Data Management**
- Zustand state management
- React Query for server state
- AsyncStorage persistence
- Offline caching

✅ **UI Components**
- Material Design with React Native Paper
- Reusable components
- Responsive design
- Error handling

## 🏗️ Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── widgets/         # Dashboard widgets
│   ├── ErrorBoundary.tsx
│   └── Loading.tsx
├── hooks/               # Custom hooks
│   └── index.ts
├── navigation/          # Navigation setup
│   └── AppNavigator.tsx
├── screens/             # Screen components
│   ├── auth/           # Login/Register
│   ├── home/           # Dashboard
│   ├── search/         # Search functionality
│   ├── player/         # Player profiles
│   ├── team/           # Team details
│   ├── favorites/      # Favorites management
│   └── settings/       # User settings
├── services/           # API services
│   └── mlbApi.ts
├── store/              # State management
│   └── index.ts
├── types/              # TypeScript definitions
│   └── index.ts
└── utils/              # Utility functions
    └── index.ts
```

## 🔧 Key Components

### Authentication Flow
- `LoginScreen`: User login with validation
- `RegisterScreen`: New user registration
- `AuthStore`: Authentication state management
- JWT token handling with secure storage

### Dashboard System
- `HomeScreen`: Main dashboard with widgets
- `DashboardStore`: Widget configuration
- Widget types: standings, player stats, team stats, recent games
- Drag & drop widget management

### Search System
- `SearchScreen`: Natural language search interface
- `SearchStore`: Search history and results
- Integration with Django backend NLP
- Real-time search suggestions

### Data Layer
- `mlbApi.ts`: Comprehensive API service
- React Query for caching and synchronization
- Offline storage with AsyncStorage
- Type-safe API responses

## 🎨 UI/UX Features

### Design System
- Material Design components
- Consistent color scheme
- Responsive layouts
- Dark/light theme support

### User Experience
- Pull-to-refresh functionality
- Loading states and error handling
- Smooth animations
- Offline support

### Accessibility
- Screen reader support
- Keyboard navigation
- Color contrast compliance
- Large text support

## 🔗 Backend Integration

### API Endpoints
- Authentication: login, register, logout
- Players: profiles, stats, search
- Teams: details, roster, schedule
- Games: recent, upcoming, live
- Natural language search
- User preferences and favorites

### Data Synchronization
- Real-time updates
- Background sync
- Conflict resolution
- Offline queue

## 🧪 Testing Strategy

### Unit Tests
- Component testing with React Testing Library
- Service layer testing
- Store testing
- Utility function testing

### Integration Tests
- API integration
- Navigation flow
- Authentication flow
- Data synchronization

### E2E Tests
- Critical user journeys
- Cross-platform compatibility
- Performance testing

## 🚀 Deployment

### Development
```bash
npm start           # Start development server
npm run android     # Run on Android
npm run ios         # Run on iOS
npm run web         # Run on web
```

### Production Build
```bash
eas build --platform android
eas build --platform ios
eas submit --platform android
eas submit --platform ios
```

## 📊 Performance Optimization

### Implemented Optimizations
- React Query caching
- Image optimization
- Lazy loading
- Bundle splitting
- Memory management

### Monitoring
- Performance metrics
- Error tracking
- User analytics
- Crash reporting

## 🔐 Security

### Authentication Security
- JWT token validation
- Secure storage (Keychain/Keystore)
- Token refresh handling
- Logout on token expiry

### Data Security
- HTTPS communication
- Input validation
- XSS protection
- SQL injection prevention

## 📱 Platform-Specific Features

### iOS
- Face ID/Touch ID support
- iOS-specific UI patterns
- Push notifications
- Background app refresh

### Android
- Fingerprint authentication
- Android-specific UI patterns
- Background services
- Deep linking

## 🔄 State Management

### Zustand Stores
- `AuthStore`: User authentication
- `DashboardStore`: Widget management
- `SearchStore`: Search functionality
- `FavoritesStore`: User favorites
- `MLBDataStore`: MLB data cache

### Data Flow
1. User interactions → Actions
2. Actions → Store updates
3. Store updates → Component re-renders
4. Background sync → API calls
5. API responses → Store updates

## 🌐 Offline Support

### Offline Capabilities
- Cached data viewing
- Offline favorites management
- Queue API calls
- Sync on reconnect

### Implementation
- AsyncStorage for persistence
- Network state monitoring
- Offline indicators
- Sync conflict resolution

## 📈 Analytics & Monitoring

### User Analytics
- Screen views
- User interactions
- Feature usage
- Performance metrics

### Error Monitoring
- Crash reports
- Error boundaries
- API error tracking
- User feedback

## 🔮 Future Enhancements

### Planned Features
- Push notifications
- Social features
- Fantasy baseball integration
- Advanced analytics
- Live game tracking
- Widget marketplace

### Technical Improvements
- GraphQL integration
- Real-time WebSocket connections
- Advanced caching strategies
- Performance optimizations
- Code splitting

## 🤝 Contributing

### Development Workflow
1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Standards
- TypeScript strict mode
- ESLint configuration
- Prettier formatting
- Conventional commits
- Code reviews

## 📚 Resources

### Documentation
- React Native docs
- Expo documentation
- React Navigation
- React Query
- Zustand

### Tools
- VS Code extensions
- React DevTools
- Flipper debugging
- Expo DevTools

## 🐛 Troubleshooting

### Common Issues
1. **Metro bundler cache**: `npx expo r --clear`
2. **iOS simulator**: Reset simulator
3. **Android emulator**: Wipe data
4. **Dependencies**: `rm -rf node_modules && npm install`

### Debug Tips
- Use React DevTools
- Check console logs
- Verify API responses
- Test on different devices
- Check network connectivity

## 📞 Support

For technical support or questions:
- Check documentation
- Review code comments
- Create GitHub issues
- Contact development team

---

**Built with ❤️ using React Native, Expo, and TypeScript**
