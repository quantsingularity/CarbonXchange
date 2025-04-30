import axios from 'axios';
import * as SecureStore from 'expo-secure-store'; // For storing JWT token securely

// Define the base URL for the API based on environment (adjust as needed)
// Using placeholder, replace with actual dev/prod URLs from docs if available
const API_BASE_URL = 'http://localhost:3000/api/v1'; // Replace with actual backend URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add JWT token to requests
apiClient.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('userToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Function to save token
const saveToken = async (token) => {
  try {
    await SecureStore.setItemAsync('userToken', token);
  } catch (error) {
    console.error('Error saving token:', error);
  }
};

// Function to remove token
const removeToken = async () => {
  try {
    await SecureStore.deleteItemAsync('userToken');
  } catch (error) {
    console.error('Error removing token:', error);
  }
};

// Authentication API calls
export const login = async (email, password) => {
  try {
    const response = await apiClient.post('/auth/login', { email, password });
    if (response.data.success && response.data.token) {
      await saveToken(response.data.token);
    }
    return response.data;
  } catch (error) {
    console.error('Login API error:', error.response?.data || error.message);
    throw error;
  }
};

export const register = async (userData) => {
  try {
    const response = await apiClient.post('/auth/register', userData);
    if (response.data.success && response.data.token) {
      await saveToken(response.data.token);
    }
    return response.data;
  } catch (error) {
    console.error('Register API error:', error.response?.data || error.message);
    throw error;
  }
};

export const logoutUser = async () => {
    await removeToken();
    // Optionally: Call a backend logout endpoint if it exists
};

// Carbon Credits API calls
export const getCredits = async (params = {}) => {
  try {
    const response = await apiClient.get('/credits', { params });
    return response.data;
  } catch (error) {
    console.error('Get Credits API error:', error.response?.data || error.message);
    throw error;
  }
};

export const createCredit = async (creditData) => {
  try {
    const response = await apiClient.post('/credits', creditData);
    return response.data;
  } catch (error) {
    console.error('Create Credit API error:', error.response?.data || error.message);
    throw error;
  }
};

// Trading API calls
export const createTrade = async (tradeData) => {
  try {
    const response = await apiClient.post('/trades', tradeData);
    return response.data;
  } catch (error) {
    console.error('Create Trade API error:', error.response?.data || error.message);
    throw error;
  }
};

export const getUserTrades = async (params = {}) => {
  try {
    const response = await apiClient.get('/trades/user', { params });
    return response.data;
  } catch (error) {
    console.error('Get User Trades API error:', error.response?.data || error.message);
    throw error;
  }
};

// Market Data API calls
export const getMarketStats = async () => {
  try {
    const response = await apiClient.get('/market/statistics');
    return response.data;
  } catch (error) {
    console.error('Get Market Stats API error:', error.response?.data || error.message);
    throw error;
  }
};

export const getMarketForecast = async (params = {}) => {
  try {
    const response = await apiClient.get('/market/forecast', { params });
    return response.data;
  } catch (error) {
    console.error('Get Market Forecast API error:', error.response?.data || error.message);
    throw error;
  }
};

// Wallet API calls
export const getWalletBalance = async () => {
  try {
    const response = await apiClient.get('/wallet/balance');
    return response.data;
  } catch (error) {
    console.error('Get Wallet Balance API error:', error.response?.data || error.message);
    throw error;
  }
};

// Add other API functions as needed based on api-reference.md




export const getCreditById = async (creditId) => {
  try {
    const response = await apiClient.get(`/credits/${creditId}`);
    return response.data;
  } catch (error) {
    console.error("Get Credit By ID API error:", error.response?.data || error.message);
    throw error;
  }
};
