import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { useDispatch } from 'react-redux';
// Import an action to set the initial auth state if needed, or handle directly in App.js
// Example: import { setInitialAuthState } from './store/slices/authSlice';

const LoadingScreen = ({ navigation }) => {
  const dispatch = useDispatch();

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = await SecureStore.getItemAsync('userToken');
        // Here you might want to validate the token with the backend
        // For simplicity, we'll just check if a token exists
        if (token) {
          // Dispatch an action to update Redux state if necessary
          // dispatch(setInitialAuthState({ isLoggedIn: true, token }));
          // Navigation logic will be handled in App.js based on Redux state
        } else {
          // dispatch(setInitialAuthState({ isLoggedIn: false, token: null }));
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        // Handle error, maybe navigate to login
        // dispatch(setInitialAuthState({ isLoggedIn: false, token: null }));
      } 
      // The actual navigation switch will happen in App.js based on the store's state
    };

    checkAuthStatus();
  }, [dispatch]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default LoadingScreen;

