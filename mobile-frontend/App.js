import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider, useSelector, useDispatch } from 'react-redux';
import store from './src/store';
import AppNavigator from './src/navigation/AppNavigator';
import AuthNavigator from './src/navigation/AuthNavigator';
import LoadingScreen from './src/screens/LoadingScreen';
import * as SecureStore from 'expo-secure-store';
// Import an action to update state based on stored token if needed
// Example: import { setInitialAuthState } from './src/store/slices/authSlice';

const RootNavigator = () => {
  const { isLoggedIn, isLoading, token } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const [isCheckingToken, setIsCheckingToken] = React.useState(true);

  useEffect(() => {
    // Check for token on initial load
    const checkToken = async () => {
      let userToken = null;
      try {
        userToken = await SecureStore.getItemAsync('userToken');
        // Optional: Validate token with backend here
        if (userToken) {
          // If you have an action to rehydrate state from token:
          // dispatch(setInitialAuthState({ isLoggedIn: true, token: userToken }));
          // For now, we rely on the initial state potentially being set by login/register
          // If the authSlice doesn't persist state, you'll need logic here
          // to fetch user details based on the token and update the store.
          console.log("Token found, assuming logged in for now.");
          // A simple approach without rehydration action:
          // Manually dispatching a fulfilled login action might be complex
          // Best practice is often to have an endpoint like /auth/me to get user from token
        } else {
          console.log("No token found.");
        }
      } catch (e) {
        console.error('Failed to load token', e);
      } finally {
        setIsCheckingToken(false);
      }
    };

    checkToken();
  }, [dispatch]);

  if (isCheckingToken || isLoading) {
    // Show loading screen while checking token or during login/register process
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      {isLoggedIn ? <AppNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};

export default function App() {
  return (
    <Provider store={store}>
      <RootNavigator />
    </Provider>
  );
}

