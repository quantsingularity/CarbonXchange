import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Button, ScrollView, Alert } from 'react-native';
// Assuming an API function exists to get credit details by ID
// import { getCreditById } from '../services/api'; 

// Placeholder for API call - replace with actual implementation
const getCreditById = async (creditId) => {
  console.log(`Fetching details for credit ID: ${creditId}`);
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500)); 
  // Return mock data based on the list screen structure
  if (creditId === 'credit_id_1') { // Example ID
      return {
          success: true,
          data: {
              id: 'credit_id_1',
              type: 'reforestation',
              amount: 150,
              price: '30.00',
              status: 'available',
              verificationStatus: 'verified',
              description: 'Credits from a verified reforestation project in the Amazon rainforest. Helps restore biodiversity and capture carbon.',
              seller: { name: 'EcoForest Ltd.', rating: 4.8 },
              createdAt: '2024-02-15T10:30:00Z',
              verificationDocuments: ['doc_url_1', 'doc_url_2']
          }
      };
  } else {
       return {
          success: true, // Simulate success even for other IDs for now
          data: {
              id: creditId,
              type: 'renewable_energy',
              amount: 100,
              price: '25.50',
              status: 'available',
              verificationStatus: 'verified',
              description: 'Standard solar power project credits. Generated from a large-scale solar farm.',
              seller: { name: 'Solar Inc.', rating: 4.5 },
              createdAt: '2024-01-01T00:00:00Z',
              verificationDocuments: []
          }
      };
      // Or return error for non-existent IDs
      // return { success: false, error: { message: 'Credit not found' } };
  }
};

const CreditDetailScreen = ({ route, navigation }) => {
  const { creditId } = route.params;
  const [creditDetails, setCreditDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCreditDetails = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getCreditById(creditId);
      if (response.success) {
        setCreditDetails(response.data);
      } else {
        setError(response.error?.message || 'Failed to fetch credit details');
        Alert.alert('Error', response.error?.message || 'Failed to fetch credit details');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
      Alert.alert('Error', err.message || 'An error occurred while fetching details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCreditDetails();
  }, [creditId]);

  if (isLoading) {
    return (
      <View style={styles.centered}><ActivityIndicator size="large" /></View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Error: {error}</Text>
        <Button title="Retry" onPress={fetchCreditDetails} />
      </View>
    );
  }

  if (!creditDetails) {
    return (
      <View style={styles.centered}><Text>No credit details found.</Text></View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{creditDetails.type.replace(/_/g, ' ').toUpperCase()}</Text>
      <View style={styles.detailRow}>
        <Text style={styles.label}>Amount:</Text>
        <Text style={styles.value}>{creditDetails.amount} Tonnes CO2e</Text>
      </View>
      <View style={styles.detailRow}>
        <Text style={styles.label}>Price per Tonne:</Text>
        <Text style={styles.value}>${creditDetails.price}</Text>
      </View>
      <View style={styles.detailRow}>
        <Text style={styles.label}>Status:</Text>
        <Text style={styles.value}>{creditDetails.status}</Text>
      </View>
      <View style={styles.detailRow}>
        <Text style={styles.label}>Verification:</Text>
        <Text style={styles.value}>{creditDetails.verificationStatus}</Text>
      </View>
      <Text style={styles.descriptionTitle}>Description:</Text>
      <Text style={styles.descriptionText}>{creditDetails.description}</Text>
      
      {creditDetails.seller && (
          <View style={styles.sellerInfo}>
              <Text style={styles.label}>Seller:</Text>
              <Text>{creditDetails.seller.name} (Rating: {creditDetails.seller.rating}/5)</Text>
          </View>
      )}

      {/* Add verification document links if needed */}
      {/* {creditDetails.verificationDocuments && creditDetails.verificationDocuments.length > 0 && (...)} */}

      <Button 
        title="Initiate Trade" 
        onPress={() => navigation.navigate('Trading', { creditId: creditDetails.id, price: creditDetails.price, availableAmount: creditDetails.amount })} 
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
    paddingVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#555',
  },
  value: {
    fontSize: 16,
    color: '#333',
  },
  descriptionTitle: {
      fontSize: 18,
      fontWeight: 'bold',
      marginTop: 15,
      marginBottom: 5,
      color: '#333',
  },
  descriptionText: {
      fontSize: 15,
      lineHeight: 22,
      color: '#444',
      marginBottom: 20,
  },
  sellerInfo: {
      marginTop: 10,
      marginBottom: 20,
      padding: 10,
      backgroundColor: '#f9f9f9',
      borderRadius: 5,
  },
  errorText: {
    color: 'red',
    marginBottom: 10,
  },
});

export default CreditDetailScreen;

