# ZarbdorUn Mobile App (Customer)

Flutter mobile application for customers to browse products, place orders, and track deliveries.

## Features

- **Guest Mode**: Browse products without authentication
- **Authentication**: OTP-based login via phone number
- **Product Catalog**: Browse by categories, search products
- **Shopping Cart**: Add/remove items, manage quantities
- **Favorites**: Save favorite products
- **Order Management**: Place orders, track status
- **Real-time Chat**: Communicate with sellers/couriers via WebSocket
- **Bilingual**: Uzbek Latin and Russian support
- **Location Picker**: Select delivery address on map
- **Image Upload**: Share images in chat
- **Offline Detection**: Automatic retry on network restoration

## Tech Stack

- **Framework**: Flutter 3.0+
- **State Management**: Provider
- **HTTP**: Dio
- **WebSocket**: web_socket_channel
- **Maps**: Google Maps Flutter
- **Storage**: SharedPreferences
- **UI**: Material Design 3, Google Fonts (Inter)

## Project Structure

```
lib/
├── main.dart                   # App entry point
├── config/                     # App configuration
│   ├── constants.dart          # API URLs, colors, keys
│   ├── theme.dart              # Material theme
│   └── routes.dart             # Named routes
├── models/                     # Data models
├── providers/                  # State management
├── services/                   # API & WebSocket services
├── screens/                    # UI screens
└── widgets/                    # Reusable widgets
```

## Getting Started

### Prerequisites

- Flutter SDK 3.0 or higher
- Dart SDK 3.0 or higher
- Android Studio / VS Code with Flutter extensions
- Google Maps API key (for maps functionality)

### Installation

1. Clone the repository
2. Navigate to the mobile_app directory:
   ```bash
   cd mobile_app
   ```

3. Install dependencies:
   ```bash
   flutter pub get
   ```

4. Configure API endpoint in `lib/config/constants.dart`:
   ```dart
   static const String baseUrl = 'YOUR_API_URL';
   static const String wsUrl = 'YOUR_WEBSOCKET_URL';
   ```

5. Run the app:
   ```bash
   flutter run
   ```

## Configuration

### API Configuration

Update the API endpoints in `lib/config/constants.dart`:

```dart
static const String baseUrl = 'http://localhost:8000/api/v1';
static const String wsUrl = 'ws://localhost:8000/ws';
```

### Google Maps

Add your Google Maps API key to:

**Android** (`android/app/src/main/AndroidManifest.xml`):
```xml
<meta-data
    android:name="com.google.android.geo.API_KEY"
    android:value="YOUR_API_KEY"/>
```

**iOS** (`ios/Runner/AppDelegate.swift`):
```swift
GMSServices.provideAPIKey("YOUR_API_KEY")
```

## Color Scheme

- Primary: Orange (#F97316)
- Secondary: Slate (#1E293B)
- Background: (#F8FAFC)
- Error: Red (#EF4444)
- Success: Green (#10B981)

## Build

### Android
```bash
flutter build apk --release
```

### iOS
```bash
flutter build ios --release
```

## State Management

The app uses Provider for state management with the following providers:

- **AuthProvider**: User authentication state
- **LanguageProvider**: App language (Uzbek/Russian)
- **ProductsProvider**: Product catalog & categories
- **CartProvider**: Shopping cart items
- **FavoritesProvider**: Favorite products
- **OrdersProvider**: Order history & management
- **ChatProvider**: Real-time chat messages

## License

Copyright © 2024 ZarbdorUn. All rights reserved.
