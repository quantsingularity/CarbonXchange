import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { createTrade } from '../../services/api'; // Assuming API service is set up

const TradingScreen = ({ route, navigation }) => {
  const { creditId, price, availableAmount } = route.params;
  const [amount, setAmount] = useState('');
  const [tradeType, setTradeType] = useState('buy'); // Default to 'buy'
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateTrade = async () => {
    setError(null);
    const tradeAmount = parseInt(amount, 10);

    if (isNaN(tradeAmount) || tradeAmount <= 0) {
      Alert.alert('Error', 'Please enter a valid amount.');
      return;
    }

    if (tradeType === 'sell' && tradeAmount > availableAmount) {
        Alert.alert('Error', `You cannot sell more than the available amount (${availableAmount}).`);
        return;
    }
    // Add similar check for buy if user balance is tracked and needed here

    setIsLoading(true);
    try {
      const tradeData = {
        creditId,
        amount: tradeAmount,
        price: price, // Use the price passed from the detail screen
        type: tradeType,
      };
      const response = await createTrade(tradeData);
      if (response.success) {
        Alert.alert('Success', `Trade order created successfully!`);
        // Navigate back or to a confirmation screen
        navigation.goBack(); 
      } else {
        setError(response.error?.message || 'Failed to create trade order');
        Alert.alert('Error', response.error?.message || 'Failed to create trade order');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
      Alert.alert('Error', err.message || 'An error occurred while creating the trade');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Trade Order</Text>
      <Text style={styles.creditInfo}>Credit ID: {creditId}</Text>
      <Text style={styles.creditInfo}>Current Price: ${price}</Text>
      <Text style={styles.creditInfo}>Available Amount: {availableAmount} Tonnes</Text>

      <View style={styles.tradeTypeContainer}>
        <Button 
          title="Buy" 
          onPress={() => setTradeType('buy')} 
          color={tradeType === 'buy' ? '#007AFF' : 'gray'} 
        />
        <Button 
          title="Sell" 
          onPress={() => setTradeType('sell')} 
          color={tradeType === 'sell' ? '#FF3B30' : 'gray'} 
        />
      </View>

      <TextInput
        style={styles.input}
        placeholder="Amount (Tonnes)"
        value={amount}
        onChangeText={setAmount}
        keyboardType="numeric"
      />

      {isLoading ? (
        <ActivityIndicator size="large" style={styles.loader} />
      ) : (
        <Button title={`Create ${tradeType === 'buy' ? 'Buy' : 'Sell'} Order`} onPress={handleCreateTrade} />
      )}

      {error && <Text style={styles.errorText}>Error: {error}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  creditInfo: {
    fontSize: 16,
    marginBottom: 8,
    color: '#555',
  },
  tradeTypeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 20,
  },
  input: {
    height: 45,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 20,
    paddingHorizontal: 10,
    borderRadius: 5,
    fontSize: 16,
  },
  loader: {
      marginTop: 10,
  },
  errorText: {
    color: 'red',
    marginTop: 15,
    textAlign: 'center',
  },
});

export default TradingScreen;

