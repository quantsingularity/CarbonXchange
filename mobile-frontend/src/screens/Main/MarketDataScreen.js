import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Button, ScrollView } from 'react-native';
import { getMarketStats, getMarketForecast } from '../../services/api'; // Assuming API service is set up

const MarketDataScreen = () => {
  const [stats, setStats] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isLoadingForecast, setIsLoadingForecast] = useState(false);
  const [errorStats, setErrorStats] = useState(null);
  const [errorForecast, setErrorForecast] = useState(null);

  const fetchMarketStats = async () => {
    setIsLoadingStats(true);
    setErrorStats(null);
    try {
      const response = await getMarketStats();
      if (response.success) {
        setStats(response.data);
      } else {
        setErrorStats(response.error?.message || 'Failed to fetch market stats');
      }
    } catch (err) {
      setErrorStats(err.message || 'An error occurred while fetching stats');
    } finally {
      setIsLoadingStats(false);
    }
  };

  const fetchMarketForecast = async (timeframe = '24h', type = 'price') => {
    setIsLoadingForecast(true);
    setErrorForecast(null);
    try {
      const response = await getMarketForecast({ timeframe, type });
      if (response.success) {
        // Assuming forecast data structure, adjust as needed
        setForecast({ timeframe, type, data: response.data }); 
      } else {
        setErrorForecast(response.error?.message || 'Failed to fetch market forecast');
      }
    } catch (err) {
      setErrorForecast(err.message || 'An error occurred while fetching forecast');
    } finally {
      setIsLoadingForecast(false);
    }
  };

  useEffect(() => {
    fetchMarketStats();
    fetchMarketForecast(); // Fetch default forecast on mount
  }, []);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Market Statistics</Text>
      {isLoadingStats ? (
        <ActivityIndicator />
      ) : errorStats ? (
        <View>
          <Text style={styles.errorText}>Error fetching stats: {errorStats}</Text>
          <Button title="Retry Stats" onPress={fetchMarketStats} />
        </View>
      ) : stats ? (
        <View style={styles.section}>
          <Text style={styles.statItem}>Total Volume: {stats.totalVolume}</Text>
          <Text style={styles.statItem}>24h Volume: {stats.totalVolume}</Text> 
          <Text style={styles.statItem}>Average Price: ${stats.averagePrice}</Text>
          <Text style={styles.statItem}>24h Price Change: {stats.priceChange24h}%</Text>
        </View>
      ) : (
        <Text>No statistics available.</Text>
      )}

      <Text style={styles.title}>Market Forecast</Text>
      {/* Add buttons or picker to select timeframe/type */} 
      {isLoadingForecast ? (
        <ActivityIndicator />
      ) : errorForecast ? (
        <View>
          <Text style={styles.errorText}>Error fetching forecast: {errorForecast}</Text>
          <Button title="Retry Forecast" onPress={() => fetchMarketForecast()} />
        </View>
      ) : forecast ? (
        <View style={styles.section}>
          <Text style={styles.subTitle}>Forecast ({forecast.timeframe}, {forecast.type}):</Text>
          {/* Display forecast data - structure depends on API response */} 
          <Text>Forecast Data: {JSON.stringify(forecast.data)}</Text> 
        </View>
      ) : (
        <Text>No forecast available.</Text>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f9f9f9',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 15,
    marginTop: 10,
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
  statItem: {
    fontSize: 16,
    marginBottom: 8,
    color: '#555',
  },
  errorText: {
    color: 'red',
    marginBottom: 10,
  },
});

export default MarketDataScreen;

