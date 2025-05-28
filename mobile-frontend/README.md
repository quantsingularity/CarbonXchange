# Mobile Frontend Directory

## Overview

The mobile-frontend directory contains the React Native application that serves as the mobile client for the Carbonxchange platform. This cross-platform mobile application provides users with a comprehensive interface to interact with the Carbonxchange ecosystem on iOS and Android devices. The mobile frontend delivers a responsive, intuitive user experience that allows users to monitor carbon credits, execute trades, view analytics, and manage their accounts while on the go.

## Technology Stack

The mobile application is built using the following key technologies:

- **React Native**: A cross-platform framework that enables development of native mobile applications using JavaScript and React
- **Expo**: A set of tools and services built around React Native that simplifies the development, building, and deployment processes
- **JavaScript/ES6+**: The primary programming language used throughout the application
- **Jest**: A testing framework for ensuring code quality and reliability
- **ESLint**: A static code analysis tool for identifying problematic patterns in JavaScript code

## Directory Structure

The mobile-frontend directory is organized as follows:

### Root Configuration Files

Several configuration files exist at the root level:
- `app.json`: Contains Expo configuration settings for the application
- `package.json` and `package-lock.json`: Define dependencies and scripts for the Node.js ecosystem
- `.eslintrc.js`: Contains ESLint configuration for code quality enforcement
- `babel.config.js`: Configures Babel for JavaScript transpilation
- `jest.config.js`: Configures the Jest testing framework
- `index.js`: The entry point for the React Native application
- `App.js`: The root component of the React Native application

### Source Code

The `src` directory contains the main application code, organized into several subdirectories:

- **components**: Reusable UI components used throughout the application
- **screens**: Screen components representing different views in the application
- **navigation**: Navigation configuration and components
- **services**: API clients and other service integrations
- **redux**: State management using Redux (actions, reducers, store)
- **utils**: Utility functions and helpers
- **hooks**: Custom React hooks
- **constants**: Application constants and configuration values

### Assets

The `assets` directory contains static resources used by the application:
- Images and icons
- Fonts
- Animation files
- Other static resources

### Testing

The `__mocks__` directory contains mock implementations used during testing to simulate dependencies and external services.

## Development Workflow

The mobile frontend development workflow typically involves:

1. **Setup**: Installing dependencies using npm or yarn
2. **Development**: Writing code with hot reloading enabled via Expo
3. **Testing**: Running unit and integration tests using Jest
4. **Building**: Creating production builds for iOS and Android
5. **Deployment**: Publishing to the App Store and Google Play Store

## Key Features

The mobile application provides several key features:

1. **User Authentication**: Secure login, registration, and account management
2. **Carbon Credit Dashboard**: Real-time overview of carbon credit holdings and market activity
3. **Trading Interface**: Tools for buying, selling, and trading carbon credits
4. **Analytics**: Visualizations and insights into carbon credit performance and market trends
5. **Notifications**: Real-time alerts for important events and transactions
6. **Profile Management**: User profile and preference settings
7. **Offline Support**: Basic functionality when network connectivity is limited

## Integration Points

The mobile frontend integrates with other Carbonxchange components through:

1. **Backend API**: RESTful API calls to the backend services
2. **Blockchain**: Integration with blockchain services for transaction verification
3. **Analytics**: Connection to AI models for predictive insights

## Getting Started

To begin development on the mobile frontend:

1. Ensure you have Node.js and npm installed
2. Install Expo CLI: `npm install -g expo-cli`
3. Install dependencies: `npm install` or `yarn install`
4. Start the development server: `npm start` or `yarn start`
5. Use the Expo Go app on your device or an emulator to run the application

## Best Practices

When contributing to the mobile frontend, follow these best practices:

1. **Component Structure**: Create reusable, well-documented components
2. **State Management**: Use Redux for global state and React hooks for local state
3. **Testing**: Write tests for all new components and functionality
4. **Performance**: Optimize rendering and minimize unnecessary re-renders
5. **Accessibility**: Ensure the application is accessible to all users
6. **Responsive Design**: Design for various screen sizes and orientations
7. **Code Style**: Follow the established code style enforced by ESLint

## Troubleshooting

Common issues and their solutions:

1. **Build Failures**: Ensure all dependencies are correctly installed and compatible
2. **API Connection Issues**: Verify API endpoints and authentication configuration
3. **Performance Problems**: Check for unnecessary re-renders or heavy computations
4. **Testing Errors**: Ensure mocks are properly configured for external dependencies

For more detailed information about the mobile frontend, refer to the comprehensive documentation in the `/docs` directory.
