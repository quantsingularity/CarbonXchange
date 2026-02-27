import React, { useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { Provider, useSelector, useDispatch } from "react-redux";
import { StatusBar } from "expo-status-bar";
import store from "./src/store";
import AppNavigator from "./src/navigation/AppNavigator";
import AuthNavigator from "./src/navigation/AuthNavigator";
import LoadingScreen from "./src/screens/LoadingScreen";
import ErrorBoundary from "./src/components/ErrorBoundary";
import { rehydrateAuth } from "./src/store/slices/authSlice";

const RootNavigator = () => {
  const { isLoggedIn, isLoading, isRehydrating } = useSelector(
    (state) => state.auth,
  );
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(rehydrateAuth());
  }, [dispatch]);

  if (isRehydrating || isLoading) {
    return (
      <LoadingScreen
        message={isRehydrating ? "Checking authentication..." : "Loading..."}
      />
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      {isLoggedIn ? <AppNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};

export default function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <RootNavigator />
      </Provider>
    </ErrorBoundary>
  );
}
