import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import Web3 from 'web3';

export default function TradingDashboard() {
  const [listings, setListings] = useState([]);
  const web3 = new Web3(Web3.givenProvider || 'http://localhost:8545');

  useEffect(() => {
    async function loadListings() {
      const response = await fetch('/api/listings');
      const data = await response.json();
      setListings(data);
    }
    loadListings();
  }, []);

  return (
    <div>
      <h2>Active Listings</h2>
      <BarChart width={600} height={300} data={listings}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="pricePerToken" />
        <YAxis />
        <Bar dataKey="amount" fill="#8884d8" />
      </BarChart>
    </div>
  );
}
