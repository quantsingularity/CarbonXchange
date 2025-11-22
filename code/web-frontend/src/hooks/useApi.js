import React from 'react';
import axios from 'axios';

// Create a custom hook for API calls
export const useApi = () => {
    const apiClient = axios.create({
        baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const getListings = async () => {
        try {
            const response = await apiClient.get('/api/listings');
            return response.data;
        } catch (error) {
            console.error('Error fetching listings:', error);
            throw error;
        }
    };

    const getCreditDistribution = async () => {
        try {
            const response = await apiClient.get('/api/credit-distribution');
            return response.data;
        } catch (error) {
            console.error('Error fetching credit distribution:', error);
            throw error;
        }
    };

    const getForecast = async (features) => {
        try {
            const response = await apiClient.post('/api/forecast', features);
            return response.data;
        } catch (error) {
            console.error('Error fetching forecast:', error);
            throw error;
        }
    };

    const getUserInfo = async (walletAddress) => {
        try {
            const response = await apiClient.get(`/api/user/${walletAddress}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching user info:', error);
            throw error;
        }
    };

    return {
        getListings,
        getCreditDistribution,
        getForecast,
        getUserInfo,
    };
};

export default useApi;
