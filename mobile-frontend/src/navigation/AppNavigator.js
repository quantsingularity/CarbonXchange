import React from 'react';
import { Platform } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import CreditsListScreen from '../screens/Main/CreditsListScreen';
import CreditDetailScreen from '../screens/Main/CreditDetailScreen';
import TradingScreen from '../screens/Main/TradingScreen';
import MarketDataScreen from '../screens/Main/MarketDataScreen';
import WalletScreen from '../screens/Main/WalletScreen';
import TradeHistoryScreen from '../screens/Main/TradeHistoryScreen'; // Import the new screen
import theme from '../styles/theme'; // Import theme for styling

// Import icons (placeholder - install expo vector icons if needed)
// import { Ionicons } from '@expo/vector-icons';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Define Tab Icons (Placeholder function)
// Replace with actual icons from a library like @expo/vector-icons
const getTabBarIcon = (routeName, focused, color, size) => {
  let iconName;
  if (routeName === 'Credits') {
    iconName = focused ? 'leaf' : 'leaf-outline'; // Example names
  } else if (routeName === 'Market') {
    iconName = focused ? 'stats-chart' : 'stats-chart-outline';
  } else if (routeName === 'Wallet') {
    iconName = focused ? 'wallet' : 'wallet-outline';
  } else if (routeName === 'History') {
    iconName = focused ? 'receipt' : 'receipt-outline';
  }

  // Return placeholder text or actual Icon component
  // return <Ionicons name={iconName} size={size} color={color} />;
  return <Text style={{ color: color, fontSize: 10 }}>{iconName?.split('-')[0]}</Text>; // Simple text placeholder
};

// Main application tabs
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false, // Hide header for tabs, manage headers in stack screens
        tabBarIcon: ({ focused, color, size }) => getTabBarIcon(route.name, focused, color, size),
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.border,
          paddingBottom: Platform.OS === 'ios' ? theme.spacing.md : theme.spacing.xs, // Adjust padding for platform
          height: Platform.OS === 'ios' ? 80 : 60, // Adjust height for platform
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
          marginTop: -theme.spacing.xs, // Adjust label position
        },
      })}
    >
      <Tab.Screen
        name="Credits"
        component={CreditsListScreen}
        options={{ title: 'Credits' }}
      />
      <Tab.Screen
        name="Market"
        component={MarketDataScreen}
        options={{ title: 'Market' }}
      />
      <Tab.Screen
        name="Wallet"
        component={WalletScreen}
        options={{ title: 'Wallet' }}
      />
      <Tab.Screen
        name="History"
        component={TradeHistoryScreen}
        options={{ title: 'History' }}
      />
    </Tab.Navigator>
  );
}

// App Navigator using a Stack to contain Tabs and other screens
const AppNavigator = () => {
  return (
    <Stack.Navigator
      initialRouteName="MainTabs"
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.surface,
        },
        headerTintColor: theme.colors.primary,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        headerBackTitleVisible: false, // Hide back button text on iOS
      }}
    >
      <Stack.Screen
        name="MainTabs"
        component={MainTabs}
        options={{ headerShown: false }} // Hide header for the tab container itself
      />
      <Stack.Screen
        name="CreditDetail"
        component={CreditDetailScreen}
        options={{ title: 'Credit Details' }} // Header title for this screen
      />
      <Stack.Screen
        name="Trading"
        component={TradingScreen}
        options={{
          title: 'Initiate Trade',
          presentation: 'modal', // Example: Open Trading screen as a modal
        }}
      />
      {/* Add other non-tab screens here if needed */}
    </Stack.Navigator>
  );
};

export default AppNavigator;
