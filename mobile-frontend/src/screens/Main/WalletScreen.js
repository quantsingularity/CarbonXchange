import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Button, FlatList, TouchableOpacity } from 'react-native';
import { getWalletBalance, getUserTrades } from '../../services/api'; // Assuming API service is set up
import { useSelector } from 'react-redux';

const WalletScreen = ({ navigation }) => {
  const [balance, setBalance] = useState(null);
  const [trades, setTrades] = useState([]);
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);
  const [isLoadingTrades, setIsLoadingTrades] = useState(false);
  const [errorBalance, setErrorBalance] = useState(null);
  const [errorTrades, setErrorTrades] = useState(null);
  const [tradePage, setTradePage] = useState(1);
  const [totalTradePages, setTotalTradePages] = useState(1);

  const { user } = useSelector((state) => state.auth); // Get user info if needed

  const fetchWalletBalance = async () => {
    setIsLoadingBalance(true);
    setErrorBalance(null);
    try {
      const response = await getWalletBalance();
      if (response.success) {
        setBalance(response.data);
      } else {
        setErrorBalance(response.error?.message || 'Failed to fetch wallet balance');
      }
    } catch (err) {
      setErrorBalance(err.message || 'An error occurred while fetching balance');
    } finally {
      setIsLoadingBalance(false);
    }
  };

  const fetchUserTrades = async (pageNum = 1) => {
    setIsLoadingTrades(true);
    setErrorTrades(null);
    try {
      const response = await getUserTrades({ page: pageNum, limit: 10 }); // Adjust limit
      if (response.success) {
        setTrades(pageNum === 1 ? response.data.trades : [...trades, ...response.data.trades]);
        setTotalTradePages(response.data.pages);
        setTradePage(pageNum);
      } else {
        setErrorTrades(response.error?.message || 'Failed to fetch trades');
      }
    } catch (err) {
      setErrorTrades(err.message || 'An error occurred while fetching trades');
    } finally {
      setIsLoadingTrades(false);
    }
  };

  useEffect(() => {
    fetchWalletBalance();
    fetchUserTrades(1); // Fetch initial page of trades
  }, []);

  const handleLoadMoreTrades = () => {
    if (!isLoadingTrades && tradePage < totalTradePages) {
      fetchUserTrades(tradePage + 1);
    }
  };

  const renderTradeItem = ({ item }) => (
    <View style={styles.tradeItemContainer}>
      <Text>Type: {item.type.toUpperCase()}</Text>
      <Text>Credit ID: {item.creditId}</Text> 
      <Text>Amount: {item.amount}</Text>
      <Text>Price: ${item.price}</Text>
      <Text>Status: {item.status}</Text>
      <Text>Date: {new Date(item.createdAt).toLocaleDateString()}</Text>
    </View>
  );

  const renderTradeFooter = () => {
    if (!isLoadingTrades) return null;
    return <ActivityIndicator style={{ marginVertical: 20 }} />;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Wallet</Text>
      
      <View style={styles.section}>
        <Text style={styles.subTitle}>Balance</Text>
        {isLoadingBalance ? (
          <ActivityIndicator />
        ) : errorBalance ? (
          <View>
            <Text style={styles.errorText}>Error fetching balance: {errorBalance}</Text>
            <Button title="Retry Balance" onPress={fetchWalletBalance} />
          </View>
        ) : balance ? (
          <View>
            <Text style={styles.balanceText}>Token Balance: {balance.tokenBalance}</Text>
            <Text style={styles.balanceText}>Credit Balance: {balance.creditBalance} Tonnes</Text>
            <Text style={styles.balanceText}>Pending Trades: {balance.pendingTrades}</Text>
          </View>
        ) : (
          <Text>No balance information available.</Text>
        )}
      </View>

      <Text style={styles.subTitle}>Trade History</Text>
      {errorTrades && (
          <View style={{alignItems: 'center'}}>
            <Text style={styles.errorText}>Error fetching trades: {errorTrades}</Text>
            <Button title="Retry Trades" onPress={() => fetchUserTrades(1)} />
          </View>
      )}
      <FlatList
        data={trades}
        renderItem={renderTradeItem}
        keyExtractor={(item) => item.id.toString()} // Assuming trades have unique IDs
        style={styles.tradeList}
        contentContainerStyle={{ paddingBottom: 20 }}
        onEndReached={handleLoadMoreTrades}
        onEndReachedThreshold={0.5}
        ListFooterComponent={renderTradeFooter}
        ListEmptyComponent={() => (
          !isLoadingTrades && !errorTrades && <Text style={styles.emptyText}>No trade history found.</Text>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 15,
    backgroundColor: '#f9f9f9',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  subTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
    color: '#444',
  },
  section: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1.41,
    elevation: 2,
  },
  balanceText: {
    fontSize: 16,
    marginBottom: 8,
    color: '#555',
  },
  tradeList: {
    flex: 1, // Ensure FlatList takes available space
  },
  tradeItemContainer: {
    backgroundColor: '#fff',
    padding: 12,
    marginBottom: 10,
    borderRadius: 5,
    borderWidth: 1,
    borderColor: '#eee',
  },
  errorText: {
    color: 'red',
    marginBottom: 10,
    textAlign: 'center',
  },
  emptyText: {
      textAlign: 'center',
      marginTop: 30,
      fontSize: 16,
      color: 'gray',
  }
});

export default WalletScreen;

