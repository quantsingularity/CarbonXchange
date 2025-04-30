import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { registerUser, resetAuthError } from '../../store/slices/authSlice';

const RegisterScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [walletAddress, setWalletAddress] = useState(''); // Optional based on your API
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state) => state.auth);

  const handleRegister = () => {
    if (error) {
        dispatch(resetAuthError()); // Reset error before new attempt
    }
    if (!email || !password || !confirmPassword || !fullName) {
      Alert.alert('Error', 'Please fill in all required fields.');
      return;
    }
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match.');
      return;
    }
    // Basic email validation (consider a more robust library)
    if (!/\S+@\S+\.\S+/.test(email)) {
        Alert.alert('Error', 'Please enter a valid email address.');
        return;
    }

    const userData = {
      email,
      password,
      fullName,
      walletAddress, // Include if required by your API
    };
    dispatch(registerUser(userData));
    // Navigation to AppNavigator will be handled in App.js based on isLoggedIn state
  };

  React.useEffect(() => {
    if (error) {
      Alert.alert('Registration Failed', error.message || 'An unknown error occurred');
    }
  }, [error]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Register for CarbonXchange</Text>
      <TextInput
        style={styles.input}
        placeholder="Full Name"
        value={fullName}
        onChangeText={setFullName}
      />
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
       <TextInput
        style={styles.input}
        placeholder="Confirm Password"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
      />
      <TextInput
        style={styles.input}
        placeholder="Wallet Address (Optional)"
        value={walletAddress}
        onChangeText={setWalletAddress}
        autoCapitalize="none"
      />
      {isLoading ? (
        <Button title="Registering..." disabled />
      ) : (
        <Button title="Register" onPress={handleRegister} />
      )}
      <Button
        title="Already have an account? Login"
        onPress={() => navigation.navigate('Login')}
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

export default RegisterScreen;

