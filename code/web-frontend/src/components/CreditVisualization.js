import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

export default function CreditVisualization() {
  const [creditData, setCreditData] = useState([]);

  useEffect(() => {
    fetch('/api/credit-distribution')
      .then(res => res.json())
      .then(data => setCreditData(data));
  }, []);

  return (
    <PieChart width={400} height={400}>
      <Pie
        data={creditData}
        cx={200}
        cy={200}
        innerRadius={60}
        outerRadius={80}
        paddingAngle={5}
        dataKey="value"
      >
        {creditData.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
    </PieChart>
  );
}
