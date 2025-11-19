import React, { useState } from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';

export default function MarketAnalysis() {
  const [forecastData, setForecastData] = useState([]);

  const fetchForecast = async () => {
    const response = await fetch('/api/forecast', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({/* features */})
    });
    setForecastData(await response.json());
  };

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <LineChart data={forecastData}>
          <Line type="monotone" dataKey="forecast" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>
      <button onClick={fetchForecast}>Update Forecast</button>
    </div>
  );
}
