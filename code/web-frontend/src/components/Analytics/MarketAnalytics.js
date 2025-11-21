import React, { useState, useEffect, useMemo } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ReferenceLine,
  ComposedChart,
  CandlestickChart,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  Target,
  Brain,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Filter,
  Download,
  RefreshCw,
} from "lucide-react";

const MarketAnalytics = () => {
  const [selectedMetric, setSelectedMetric] = useState("price");
  const [timeRange, setTimeRange] = useState("30D");
  const [isLoading, setIsLoading] = useState(false);
  const [marketData, setMarketData] = useState([]);
  const [correlationData, setCorrelationData] = useState([]);
  const [volatilityData, setVolatilityData] = useState([]);
  const [predictionData, setPredictionData] = useState([]);

  // Generate sophisticated mock data
  const generateAnalyticsData = useMemo(() => {
    const days =
      timeRange === "7D"
        ? 7
        : timeRange === "30D"
          ? 30
          : timeRange === "90D"
            ? 90
            : 365;
    const data = [];
    let basePrice = 85;
    let baseVolume = 10000;

    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (days - i));

      // Add market cycles and trends
      const cycleFactor = Math.sin((i / days) * 4 * Math.PI) * 0.1;
      const trendFactor = (i / days) * 0.05;
      const randomFactor = (Math.random() - 0.5) * 0.08;

      const priceChange = cycleFactor + trendFactor + randomFactor;
      basePrice *= 1 + priceChange;
      basePrice = Math.max(basePrice, 50);

      const volumeChange = (Math.random() - 0.5) * 0.3;
      baseVolume *= 1 + volumeChange;
      baseVolume = Math.max(baseVolume, 5000);

      // Calculate technical indicators
      const rsi = 30 + Math.random() * 40; // RSI between 30-70
      const macd = (Math.random() - 0.5) * 2;
      const bollinger = {
        upper: basePrice * 1.02,
        lower: basePrice * 0.98,
        middle: basePrice,
      };

      data.push({
        date: date.toISOString().split("T")[0],
        timestamp: date.getTime(),
        price: parseFloat(basePrice.toFixed(2)),
        volume: Math.floor(baseVolume),
        high: parseFloat((basePrice * (1 + Math.random() * 0.02)).toFixed(2)),
        low: parseFloat((basePrice * (1 - Math.random() * 0.02)).toFixed(2)),
        open: parseFloat(
          (basePrice * (1 + (Math.random() - 0.5) * 0.01)).toFixed(2),
        ),
        close: parsePrice(basePrice.toFixed(2)),
        rsi: parseFloat(rsi.toFixed(2)),
        macd: parseFloat(macd.toFixed(4)),
        bollingerUpper: parseFloat(bollinger.upper.toFixed(2)),
        bollingerLower: parseFloat(bollinger.lower.toFixed(2)),
        bollingerMiddle: parseFloat(bollinger.middle.toFixed(2)),
        volatility: parseFloat((Math.abs(priceChange) * 100).toFixed(2)),
        momentum: parseFloat((priceChange * 100).toFixed(2)),
        support: parseFloat((basePrice * 0.95).toFixed(2)),
        resistance: parseFloat((basePrice * 1.05).toFixed(2)),
      });
    }

    return data;
  }, [timeRange]);

  // Generate correlation analysis data
  const generateCorrelationData = useMemo(() => {
    const assets = [
      "Carbon Credits",
      "Renewable Energy",
      "ESG Funds",
      "Green Bonds",
      "Clean Tech",
    ];
    const correlations = [];

    for (let i = 0; i < assets.length; i++) {
      for (let j = 0; j < assets.length; j++) {
        correlations.push({
          asset1: assets[i],
          asset2: assets[j],
          correlation: i === j ? 1 : (Math.random() * 2 - 1).toFixed(3),
          strength:
            i === j
              ? "Perfect"
              : Math.abs(Math.random() * 2 - 1) > 0.7
                ? "Strong"
                : Math.abs(Math.random() * 2 - 1) > 0.3
                  ? "Moderate"
                  : "Weak",
        });
      }
    }

    return correlations;
  }, []);

  // Generate volatility analysis
  const generateVolatilityData = useMemo(() => {
    return generateAnalyticsData.map((item, index) => ({
      ...item,
      volatility30:
        generateAnalyticsData
          .slice(Math.max(0, index - 29), index + 1)
          .reduce((sum, d) => sum + d.volatility, 0) / Math.min(30, index + 1),
      volatility7:
        generateAnalyticsData
          .slice(Math.max(0, index - 6), index + 1)
          .reduce((sum, d) => sum + d.volatility, 0) / Math.min(7, index + 1),
    }));
  }, [generateAnalyticsData]);

  // Generate AI predictions
  const generatePredictions = useMemo(() => {
    const lastPrice =
      generateAnalyticsData[generateAnalyticsData.length - 1]?.price || 85;
    const predictions = [];

    for (let i = 1; i <= 30; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);

      // Simple trend prediction with confidence intervals
      const trendFactor = 0.001 * i; // Slight upward trend
      const uncertainty = 0.02 * Math.sqrt(i); // Increasing uncertainty

      const predictedPrice =
        lastPrice * (1 + trendFactor + (Math.random() - 0.5) * 0.01);
      const confidence = Math.max(0.5, 0.95 - i * 0.01); // Decreasing confidence

      predictions.push({
        date: date.toISOString().split("T")[0],
        predicted: parseFloat(predictedPrice.toFixed(2)),
        upperBound: parseFloat((predictedPrice * (1 + uncertainty)).toFixed(2)),
        lowerBound: parseFloat((predictedPrice * (1 - uncertainty)).toFixed(2)),
        confidence: parseFloat((confidence * 100).toFixed(1)),
        model: i <= 7 ? "LSTM" : i <= 14 ? "ARIMA" : "Ensemble",
      });
    }

    return predictions;
  }, [generateAnalyticsData]);

  useEffect(() => {
    setIsLoading(true);
    // Simulate API call delay
    setTimeout(() => {
      setMarketData(generateAnalyticsData);
      setCorrelationData(generateCorrelationData);
      setVolatilityData(generateVolatilityData);
      setPredictionData(generatePredictions);
      setIsLoading(false);
    }, 1000);
  }, [
    generateAnalyticsData,
    generateCorrelationData,
    generateVolatilityData,
    generatePredictions,
  ]);

  const MetricCard = ({ title, value, change, trend, icon: Icon, color }) => (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
        <div
          className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            trend === "up"
              ? "bg-green-100 text-green-800"
              : trend === "down"
                ? "bg-red-100 text-red-800"
                : "bg-gray-100 text-gray-800"
          }`}
        >
          {trend === "up" ? (
            <ArrowUpRight size={12} />
          ) : trend === "down" ? (
            <ArrowDownRight size={12} />
          ) : (
            <Activity size={12} />
          )}
          <span className="ml-1">{change}</span>
        </div>
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );

  const TechnicalIndicator = ({ name, value, signal, description }) => (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-900">{name}</h4>
        <div
          className={`px-2 py-1 rounded text-xs font-medium ${
            signal === "BUY"
              ? "bg-green-100 text-green-800"
              : signal === "SELL"
                ? "bg-red-100 text-red-800"
                : "bg-yellow-100 text-yellow-800"
          }`}
        >
          {signal}
        </div>
      </div>
      <p className="text-lg font-semibold text-gray-900 mb-1">{value}</p>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.name}: ${typeof entry.value === "number" ? entry.value.toFixed(2) : entry.value}`}
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
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Market Analytics
            </h1>
            <p className="text-gray-600">
              Advanced technical analysis and market insights
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="7D">7 Days</option>
              <option value="30D">30 Days</option>
              <option value="90D">90 Days</option>
              <option value="1Y">1 Year</option>
            </select>
            <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <RefreshCw size={16} className="mr-2" />
              Refresh
            </button>
            <button className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Download size={16} className="mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Average Price"
          value="$85.42"
          change="+2.4%"
          trend="up"
          icon={DollarSign}
          color="blue"
        />
        <MetricCard
          title="Volatility (30D)"
          value="12.8%"
          change="+0.8%"
          trend="up"
          icon={Activity}
          color="orange"
        />
        <MetricCard
          title="Sharpe Ratio"
          value="1.34"
          change="+0.12"
          trend="up"
          icon={Target}
          color="green"
        />
        <MetricCard
          title="Beta"
          value="0.87"
          change="-0.05"
          trend="down"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Main Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Price Analysis with Technical Indicators */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <BarChart3 className="mr-2 text-blue-600" size={24} />
              Technical Analysis
            </h2>
            <div className="flex space-x-2">
              {["price", "volume", "rsi", "macd"].map((metric) => (
                <button
                  key={metric}
                  onClick={() => setSelectedMetric(metric)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    selectedMetric === metric
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {metric.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={400}>
            {selectedMetric === "price" ? (
              <ComposedChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="price"
                  fill="#3B82F6"
                  fillOpacity={0.1}
                  stroke="#3B82F6"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="bollingerUpper"
                  stroke="#EF4444"
                  strokeDasharray="5 5"
                  strokeWidth={1}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="bollingerLower"
                  stroke="#EF4444"
                  strokeDasharray="5 5"
                  strokeWidth={1}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="bollingerMiddle"
                  stroke="#F59E0B"
                  strokeWidth={1}
                  dot={false}
                />
              </ComposedChart>
            ) : selectedMetric === "volume" ? (
              <BarChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="volume" fill="#10B981" />
              </BarChart>
            ) : selectedMetric === "rsi" ? (
              <LineChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis domain={[0, 100]} stroke="#6B7280" />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={70} stroke="#EF4444" strokeDasharray="3 3" />
                <ReferenceLine y={30} stroke="#10B981" strokeDasharray="3 3" />
                <Line
                  type="monotone"
                  dataKey="rsi"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            ) : (
              <LineChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={0} stroke="#6B7280" />
                <Line
                  type="monotone"
                  dataKey="macd"
                  stroke="#F59E0B"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* Technical Indicators Summary */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Brain className="mr-2 text-purple-600" size={24} />
            Technical Signals
          </h2>
          <div className="space-y-4">
            <TechnicalIndicator
              name="RSI (14)"
              value="45.2"
              signal="NEUTRAL"
              description="Neither overbought nor oversold"
            />
            <TechnicalIndicator
              name="MACD"
              value="0.23"
              signal="BUY"
              description="Bullish momentum building"
            />
            <TechnicalIndicator
              name="Bollinger Bands"
              value="Mid-range"
              signal="NEUTRAL"
              description="Price within normal range"
            />
            <TechnicalIndicator
              name="Moving Average"
              value="Bullish"
              signal="BUY"
              description="Price above 20-day MA"
            />
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center mb-2">
              <CheckCircle className="text-blue-600 mr-2" size={20} />
              <span className="font-medium text-blue-900">Overall Signal</span>
            </div>
            <p className="text-2xl font-bold text-blue-900 mb-1">BULLISH</p>
            <p className="text-sm text-blue-700">
              3 of 4 indicators suggest upward movement
            </p>
          </div>
        </div>
      </div>

      {/* Advanced Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Volatility Analysis */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Zap className="mr-2 text-yellow-600" size={24} />
            Volatility Analysis
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={volatilityData}>
              <defs>
                <linearGradient
                  id="colorVolatility"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="volatility7"
                stackId="1"
                stroke="#F59E0B"
                fill="url(#colorVolatility)"
                name="7-day Volatility"
              />
              <Line
                type="monotone"
                dataKey="volatility30"
                stroke="#EF4444"
                strokeWidth={2}
                dot={false}
                name="30-day Volatility"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* AI Predictions */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Brain className="mr-2 text-indigo-600" size={24} />
            AI Price Predictions
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={predictionData.slice(0, 14)}>
              <defs>
                <linearGradient
                  id="colorPrediction"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="upperBound"
                stackId="1"
                stroke="#E5E7EB"
                fill="#F3F4F6"
                fillOpacity={0.5}
                name="Confidence Interval"
              />
              <Area
                type="monotone"
                dataKey="lowerBound"
                stackId="1"
                stroke="#E5E7EB"
                fill="#FFFFFF"
                name=""
              />
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#8B5CF6"
                strokeWidth={3}
                dot={{ fill: "#8B5CF6", strokeWidth: 2, r: 4 }}
                name="Predicted Price"
              />
            </AreaChart>
          </ResponsiveContainer>

          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">7-day Target</p>
              <p className="text-lg font-bold text-green-600">$87.50</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Confidence</p>
              <p className="text-lg font-bold text-blue-600">78%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Model</p>
              <p className="text-lg font-bold text-purple-600">LSTM</p>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Metrics */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <AlertTriangle className="mr-2 text-red-600" size={24} />
          Risk Assessment
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-red-600">VaR</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-1">
              Value at Risk (95%)
            </h3>
            <p className="text-2xl font-bold text-red-600">-$4.23</p>
            <p className="text-sm text-gray-600">Daily potential loss</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-orange-100 rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-orange-600">β</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Beta</h3>
            <p className="text-2xl font-bold text-orange-600">0.87</p>
            <p className="text-sm text-gray-600">Market correlation</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-blue-600">σ</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Volatility</h3>
            <p className="text-2xl font-bold text-blue-600">12.8%</p>
            <p className="text-sm text-gray-600">30-day annualized</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-green-600">SR</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Sharpe Ratio</h3>
            <p className="text-2xl font-bold text-green-600">1.34</p>
            <p className="text-sm text-gray-600">Risk-adjusted return</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to parse price (fixing the undefined parsePrice function)
function parsePrice(price) {
  return parseFloat(price);
}

export default MarketAnalytics;
