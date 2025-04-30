import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser, resetAuthError } from '../../store/slices/authSlice';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state) => state.auth);

  const handleLogin = () => {
    if (error) {
        dispatch(resetAuthError()); // Reset error before new attempt
    }
    if (!email || !password) {
        Alert.alert('Error', 'Please enter both email and password.');
        return;
    }
    dispatch(loginUser({ email, password }));
    // Navigation to AppNavigator will be handled in App.js based on isLoggedIn state
  };

  React.useEffect(() => {
    if (error) {
      Alert.alert('Login Failed', error.message || 'An unknown error occurred');
    }
  }, [error]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login to CarbonXchange</Text>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      {isLoading ? (
        <Button title="Logging in..." disabled />
      ) : (
        <Button title="Login" onPress={handleLogin} />
      )}
      <Button
        title="Don't have an account? Register"
        onPress={() => navigation.navigate('Register')}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 15,
    paddingHorizontal: 10,
    borderRadius: 5,
  },
});

export default LoginScreen;

