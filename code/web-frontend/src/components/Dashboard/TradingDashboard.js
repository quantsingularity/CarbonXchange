import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import {
  TrendingUp, TrendingDown, DollarSign, Activity, Users, 
  BarChart3, PieChart as PieChartIcon, Settings, Bell,
  ArrowUpRight, ArrowDownRight, Zap, Shield, Globe
} from 'lucide-react';

const TradingDashboard = () => {
  const [marketData, setMarketData] = useState([]);
  const [portfolioData, setPortfolioData] = useState([]);
  const [tradingVolume, setTradingVolume] = useState([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');
  const [isLoading, setIsLoading] = useState(true);
  const [realTimePrice, setRealTimePrice] = useState(85.42);

  // Mock data generation for demonstration
  const generateMockData = useCallback(() => {
    const timeframes = {
      '1D': 24,
      '1W': 7,
      '1M': 30,
      '3M': 90,
      '1Y': 365
    };

    const hours = timeframes[selectedTimeframe];
    const data = [];
    let basePrice = 80;

    for (let i = 0; i < hours; i++) {
      const change = (Math.random() - 0.5) * 4;
      basePrice += change;
      basePrice = Math.max(basePrice, 50); // Minimum price

      data.push({
        time: selectedTimeframe === '1D' ? `${i}:00` : `Day ${i + 1}`,
        price: parseFloat(basePrice.toFixed(2)),
        volume: Math.floor(Math.random() * 10000) + 5000,
        change: change,
        timestamp: new Date(Date.now() - (hours - i) * 60 * 60 * 1000)
      });
    }

    setMarketData(data);

    // Portfolio allocation data
    const portfolioAllocation = [
      { name: 'Renewable Energy Credits', value: 35, color: '#10B981' },
      { name: 'Forest Conservation', value: 28, color: '#3B82F6' },
      { name: 'Clean Technology', value: 22, color: '#8B5CF6' },
      { name: 'Carbon Capture', value: 15, color: '#F59E0B' }
    ];
    setPortfolioData(portfolioAllocation);

    // Trading volume data
    const volumeData = data.map(item => ({
      time: item.time,
      volume: item.volume,
      buyVolume: Math.floor(item.volume * (0.4 + Math.random() * 0.2)),
      sellVolume: Math.floor(item.volume * (0.4 + Math.random() * 0.2))
    }));
    setTradingVolume(volumeData);

    setIsLoading(false);
  }, [selectedTimeframe]);

  useEffect(() => {
    generateMockData();
  }, [generateMockData]);

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setRealTimePrice(prev => {
        const change = (Math.random() - 0.5) * 2;
        return Math.max(parseFloat((prev + change).toFixed(2)), 50);
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const StatCard = ({ title, value, change, icon: Icon, trend }) => (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <div className={`flex items-center mt-2 ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {trend === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
              <span className="text-sm font-medium ml-1">{change}</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full ${trend === 'up' ? 'bg-green-100' : trend === 'down' ? 'bg-red-100' : 'bg-blue-100'}`}>
          <Icon className={`w-6 h-6 ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-blue-600'}`} />
        </div>
      </div>
    </div>
  );

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{`Time: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.dataKey}: ${entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Carbon Credit Trading Dashboard</h1>
            <p className="text-gray-600">Real-time market data and portfolio analytics</p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Bell size={20} />
            </button>
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Settings size={20} />
            </button>
            <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Live Market</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Current Price"
          value={`$${realTimePrice}`}
          change="+2.4%"
          icon={DollarSign}
          trend="up"
        />
        <StatCard
          title="24h Volume"
          value="$2.4M"
          change="+12.8%"
          icon={Activity}
          trend="up"
        />
        <StatCard
          title="Active Traders"
          value="1,247"
          change="+5.2%"
          icon={Users}
          trend="up"
        />
        <StatCard
          title="Market Cap"
          value="$847M"
          change="-1.2%"
          icon={Globe}
          trend="down"
        />
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Price Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <TrendingUp className="mr-2 text-green-600" size={24} />
              Price Movement
            </h2>
            <div className="flex space-x-2">
              {['1D', '1W', '1M', '3M', '1Y'].map((timeframe) => (
                <button
                  key={timeframe}
                  onClick={() => setSelectedTimeframe(timeframe)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    selectedTimeframe === timeframe
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {timeframe}
                </button>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={marketData}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="time" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#3B82F6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorPrice)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Portfolio Allocation */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <PieChartIcon className="mr-2 text-purple-600" size={24} />
            Portfolio Allocation
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={portfolioData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {portfolioData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {portfolioData.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-sm text-gray-600">{item.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trading Volume and Market Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Trading Volume */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <BarChart3 className="mr-2 text-blue-600" size={24} />
            Trading Volume
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={tradingVolume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="time" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="buyVolume" stackId="a" fill="#10B981" />
              <Bar dataKey="sellVolume" stackId="a" fill="#EF4444" />
            </BarChart>
          </ResponsiveContainer>
          <div className="flex justify-center mt-4 space-x-6">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-sm text-gray-600">Buy Volume</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <span className="text-sm text-gray-600">Sell Volume</span>
            </div>
          </div>
        </div>

        {/* Market Activity Feed */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Zap className="mr-2 text-yellow-600" size={24} />
            Recent Activity
          </h2>
          <div className="space-y-4 max-h-64 overflow-y-auto">
            {[
              { type: 'buy', amount: '1,250', price: '$85.42', time: '2 min ago', user: 'GreenTech Corp' },
              { type: 'sell', amount: '850', price: '$85.38', time: '5 min ago', user: 'EcoFund Ltd' },
              { type: 'buy', amount: '2,100', price: '$85.45', time: '8 min ago', user: 'Carbon Solutions' },
              { type: 'sell', amount: '675', price: '$85.40', time: '12 min ago', user: 'CleanEnergy Inc' },
              { type: 'buy', amount: '1,800', price: '$85.43', time: '15 min ago', user: 'Sustainable Ventures' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-3 ${
                    activity.type === 'buy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {activity.user} {activity.type === 'buy' ? 'bought' : 'sold'} {activity.amount} credits
                    </p>
                    <p className="text-xs text-gray-500">at {activity.price} • {activity.time}</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  activity.type === 'buy' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {activity.type.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <Shield className="mr-2 text-indigo-600" size={24} />
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center p-4 bg-green-50 hover:bg-green-100 rounded-lg border border-green-200 transition-colors group">
            <TrendingUp className="mr-2 text-green-600 group-hover:scale-110 transition-transform" size={20} />
            <span className="font-medium text-green-800">Place Buy Order</span>
          </button>
          <button className="flex items-center justify-center p-4 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors group">
            <TrendingDown className="mr-2 text-red-600 group-hover:scale-110 transition-transform" size={20} />
            <span className="font-medium text-red-800">Place Sell Order</span>
          </button>
          <button className="flex items-center justify-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors group">
            <BarChart3 className="mr-2 text-blue-600 group-hover:scale-110 transition-transform" size={20} />
            <span className="font-medium text-blue-800">View Analytics</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;

