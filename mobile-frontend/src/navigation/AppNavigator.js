import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import CreditsListScreen from '../screens/Main/CreditsListScreen';
import CreditDetailScreen from '../screens/Main/CreditDetailScreen';
import TradingScreen from '../screens/Main/TradingScreen';
import MarketDataScreen from '../screens/Main/MarketDataScreen';
import WalletScreen from '../screens/Main/WalletScreen';

const Stack = createNativeStackNavigator();

// Placeholder for potential Tab Navigator if needed later
// import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
// const Tab = createBottomTabNavigator();

// function MainTabs() {
//   return (
//     <Tab.Navigator>
//       <Tab.Screen name="Credits" component={CreditsListScreen} />
//       <Tab.Screen name="Market" component={MarketDataScreen} />
//       <Tab.Screen name="Wallet" component={WalletScreen} />
//     </Tab.Navigator>
//   );
// }

const AppNavigator = () => {
  return (
    <Stack.Navigator initialRouteName="CreditsList">
      {/* Use MainTabs here if implementing tab navigation */}
      <Stack.Screen name="CreditsList" component={CreditsListScreen} options={{ title: 'Carbon Credits' }} />
      <Stack.Screen name="CreditDetail" component={CreditDetailScreen} options={{ title: 'Credit Details' }} />
      <Stack.Screen name="Trading" component={TradingScreen} options={{ title: 'Trade' }} />
      <Stack.Screen name="MarketData" component={MarketDataScreen} options={{ title: 'Market Data' }} />
      <Stack.Screen name="Wallet" component={WalletScreen} options={{ title: 'My Wallet' }} />
    </Stack.Navigator>
  );
};

export default AppNavigator;

