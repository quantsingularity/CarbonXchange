import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, Button, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { getCredits } from '../../services/api'; // Assuming API service is set up

const CreditsListScreen = ({ navigation }) => {
  const [credits, setCredits] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchCredits = async (pageNum = 1) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getCredits({ page: pageNum, limit: 10 }); // Adjust limit as needed
      if (response.success) {
        // Append new credits if pageNum > 1, otherwise replace
        setCredits(pageNum === 1 ? response.data.credits : [...credits, ...response.data.credits]);
        setTotalPages(response.data.pages);
        setPage(pageNum);
      } else {
        setError(response.error?.message || 'Failed to fetch credits');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching credits');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCredits(1); // Fetch initial page on mount
  }, []);

  const handleLoadMore = () => {
    if (!isLoading && page < totalPages) {
      fetchCredits(page + 1);
    }
  };

  const renderCreditItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.itemContainer}
      onPress={() => navigation.navigate('CreditDetail', { creditId: item.id })} // Navigate to detail screen
    >
      <Text style={styles.itemType}>{item.type.replace(/_/g, ' ').toUpperCase()}</Text>
      <Text>Amount: {item.amount}</Text>
      <Text>Price: ${item.price}</Text>
      <Text>Status: {item.status}</Text>
    </TouchableOpacity>
  );

  const renderFooter = () => {
    if (!isLoading) return null;
    return <ActivityIndicator style={{ marginVertical: 20 }} />;
  };

  return (
    <View style={styles.container}>
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <Button title="Retry" onPress={() => fetchCredits(1)} />
        </View>
      )}
      <FlatList
        data={credits}
        renderItem={renderCreditItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={{ paddingBottom: 20 }}
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.5}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={() => (
          !isLoading && !error && <Text style={styles.emptyText}>No credits available.</Text>
        )}
      />
       {/* Add Button to navigate to Market Data for example */} 
       <Button title="View Market Data" onPress={() => navigation.navigate('MarketData')} />
       <Button title="My Wallet" onPress={() => navigation.navigate('Wallet')} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f5f5f5',
  },
  itemContainer: {
    backgroundColor: '#fff',
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    elevation: 2,
  },
  itemType: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  errorContainer: {
    padding: 20,
    alignItems: 'center',
  },
  errorText: {
    color: 'red',
    marginBottom: 10,
  },
  emptyText: {
      textAlign: 'center',
      marginTop: 50,
      fontSize: 16,
      color: 'gray',
  }
});

export default CreditsListScreen;

