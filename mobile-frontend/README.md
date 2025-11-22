# CarbonXchange Mobile Frontend

This directory contains the mobile application for the CarbonXchange platform, designed to provide users with on-the-go access to carbon credit trading, market data, and portfolio management.

## 🚀 Technology Stack

The mobile application is built using the following core technologies:

| Category | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | **React Native** | A framework for building native mobile apps using JavaScript and React. |
| **Platform** | **Expo** | A set of tools and services built around React Native to simplify development, building, and deployment. |
| **Language** | **JavaScript** (ES6+) | The primary language for application logic. |
| **State Management** | **Redux Toolkit** | Used for predictable state management across the application, including asynchronous logic via Redux Thunks. |
| **Navigation** | **React Navigation** | Handles the application's routing and screen transitions (Stack and Tab navigators). |
| **Data Fetching** | **Axios** | Used for making HTTP requests to the backend REST API. |
| **Security** | **Expo SecureStore** | Used for securely storing sensitive data like the user's JWT token on the device. |
| **Charting** | **react-native-chart-kit** | Used for displaying data visualizations, such as market trends. |

## 📁 Directory Structure

The application follows a standard structure for a React Native/Expo project, with a clear separation of concerns:

```
mobile-frontend/
├── assets/                 # Static assets (images, fonts, etc.)
├── src/
│   ├── navigation/         # Navigation setup (AppNavigator, AuthNavigator)
│   ├── screens/            # Application screens/pages
│   │   ├── Auth/           # Authentication screens (LoginScreen, RegisterScreen)
│   │   ├── Main/           # Main application screens (MarketDataScreen, TradingScreen, etc.)
│   │   └── LoadingScreen.js# Screen displayed during initial token check
│   ├── services/           # API communication logic (api.js)
│   ├── store/              # Redux store configuration and slices (e.g., authSlice)
│   └── styles/             # Centralized styling definitions
├── App.js                  # Main application component and navigation container
├── app.json                # Expo configuration file
├── package.json            # Project dependencies and scripts
└── index.js                # Entry point for the React Native application
```

## ⚙️ Setup and Installation

To set up the project locally, you must have Node.js and Expo CLI installed.

1.  **Navigate to the project directory:**
    ```bash
    cd CarbonXchange/mobile-frontend
    ```

2.  **Install dependencies:**
    The project uses `npm` or `yarn` for package management. We recommend using the package manager that created the existing lock file (`package-lock.json` or `yarn.lock`).
    ```bash
    # Using npm
    npm install
    # OR Using yarn
    yarn install
    ```

3.  **Configure Backend URL:**
    The API client in `src/services/api.js` is currently hardcoded to a placeholder:
    ```javascript
    const API_BASE_URL = "http://localhost:3000/api/v1"; // Replace with actual backend URL
    ```
    You will need to update this `API_BASE_URL` to point to your running backend server's IP address or domain. For development on a physical device, `localhost` will not work; you must use your computer's local network IP address (e.g., `http://192.168.1.x:3000/api/v1`).

## ▶️ Available Scripts

In the project directory, you can run the following scripts using the Expo CLI:

| Script | Command | Description |
| :--- | :--- | :--- |
| **Start Development** | `npm start` or `expo start` | Starts the Expo development server. You can then scan the QR code with the Expo Go app on your phone or run on an emulator. |
| **Run on Android** | `npm run android` | Builds and runs the app on a connected Android device or emulator. |
| **Run on iOS** | `npm run ios` | Builds and runs the app on a connected iOS simulator (requires macOS). |
| **Run on Web** | `npm run web` | Runs the app in a web browser using Expo Web. |
| **Run Tests** | `npm test` | Executes unit and integration tests using Jest. |
| **Lint Code** | `npm run lint` | Runs ESLint to check for code quality and style issues. |

## 🔒 Authentication and State Management

*   **Authentication Flow:** The application uses `App.js` to determine the initial navigation stack. It checks for a stored `userToken` using `expo-secure-store`. If a token is found, the user is directed to the `AppNavigator` (main screens); otherwise, they are directed to the `AuthNavigator` (login/register screens).
*   **State Management:** **Redux Toolkit** is used to manage global state. The `authSlice` handles user login, registration, and logout, storing the user object and JWT token.
*   **API Security:** The `src/services/api.js` file includes an **Axios interceptor** that automatically attaches the JWT token (retrieved from SecureStore) as a `Bearer` token in the `Authorization` header for all authenticated API requests.

## 📱 Key Features and Screens

The application is structured around several key functional areas:

| Screen/Area | Purpose | Components/Files |
| :--- | :--- | :--- |
| **Authentication** | User login and registration. | `src/screens/Auth/LoginScreen.js`, `src/screens/Auth/RegisterScreen.js` |
| **Market Data** | Viewing real-time and historical carbon credit market statistics. | `src/screens/Main/MarketDataScreen.js` |
| **Trading** | Executing buy and sell orders for carbon credits. | `src/screens/Main/TradingScreen.js` |
| **Portfolio/Wallet** | Checking current credit holdings and fiat balance. | `src/screens/Main/WalletScreen.js` |
| **Credit Management** | Listing and viewing details of carbon credits. | `src/screens/Main/CreditsListScreen.js`, `src/screens/Main/CreditDetailScreen.js` |
| **Trade History** | Reviewing past trading activities. | `src/screens/Main/TradeHistoryScreen.js` |
