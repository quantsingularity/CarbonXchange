import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  TextField,
  MenuItem,
  InputAdornment,
  Slider,
  Paper,
  Divider,
  useTheme,
  CircularProgress
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Search as SearchIcon, TrendingUp } from '@mui/icons-material';
import useApi from '../hooks/useApi';

// Sample data for forecast chart
const forecastData = [
  { month: 'Jan', actual: 4000, forecast: 4200 },
  { month: 'Feb', actual: 3000, forecast: 3100 },
  { month: 'Mar', actual: 2000, forecast: 2200 },
  { month: 'Apr', actual: 2780, forecast: 2900 },
  { month: 'May', actual: 1890, forecast: 2100 },
  { month: 'Jun', actual: null, forecast: 2500 },
  { month: 'Jul', actual: null, forecast: 3000 },
  { month: 'Aug', actual: null, forecast: 3400 },
];

export default function MarketAnalysis() {
  const theme = useTheme();
  const api = useApi();
  const [timeframe, setTimeframe] = useState('6m');
  const [confidenceLevel, setConfidenceLevel] = useState(80);
  const [forecastResult, setForecastResult] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initial data load
    fetchForecastData();
  }, []);

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleConfidenceLevelChange = (event, newValue) => {
    setConfidenceLevel(newValue);
  };

  const fetchForecastData = async () => {
    try {
      setLoading(true);
      // Prepare features based on selected timeframe and confidence level
      const features = {
        timeframe: timeframe,
        confidence: confidenceLevel,
        // Add other features as needed
      };

      const result = await api.getForecast(features);
      if (result && result.forecast) {
        setForecastResult(result.forecast);
      } else {
        // Fallback to sample data if API returns empty result
        setForecastResult(forecastData);
      }
    } catch (error) {
      console.error("Error fetching forecast data:", error);
      // Use fallback data on error
      setForecastResult(forecastData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Market Analysis
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<TrendingUp />}
              onClick={fetchForecastData}
            >
              Generate New Forecast
            </Button>
          </Box>

      {/* Filters and Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              label="Forecast Timeframe"
              value={timeframe}
              onChange={handleTimeframeChange}
              variant="outlined"
            >
              <MenuItem value="1m">1 Month</MenuItem>
              <MenuItem value="3m">3 Months</MenuItem>
              <MenuItem value="6m">6 Months</MenuItem>
              <MenuItem value="1y">1 Year</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>
              Confidence Level: {confidenceLevel}%
            </Typography>
            <Slider
              value={confidenceLevel}
              onChange={handleConfidenceLevelChange}
              aria-labelledby="confidence-level-slider"
              valueLabelDisplay="auto"
              step={5}
              marks
              min={50}
              max={95}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search Projects"
              variant="outlined"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Main Forecast Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Carbon Credit Price Forecast
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            Historical data with AI-powered price predictions
          </Typography>
          <Box sx={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={forecastResult.length > 0 ? forecastResult : forecastData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke={theme.palette.primary.main}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 8 }}
                  name="Historical Price"
                />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  stroke={theme.palette.secondary.main}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 4 }}
                  name="Forecasted Price"
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>

      {/* Market Insights */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Insights
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                  Supply and Demand Analysis
                </Typography>
                <Typography variant="body2" paragraph>
                  Current market conditions indicate a growing demand for carbon credits, particularly in renewable energy sectors. Supply constraints are expected to continue for the next quarter, potentially driving prices upward.
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                  Regulatory Impact
                </Typography>
                <Typography variant="body2" paragraph>
                  Recent policy changes in the EU and North America are likely to increase corporate demand for carbon offsets. New compliance requirements could create additional market pressure by Q3 2025.
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                  Investment Recommendation
                </Typography>
                <Typography variant="body2">
                  Based on AI forecasting models, the optimal strategy suggests accumulating credits during the current price stability period, before the anticipated rise in Q3-Q4 2025.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Factors
              </Typography>
              <Divider sx={{ my: 2 }} />

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Policy Impact</Typography>
                  <Typography variant="body2" fontWeight={600}>High</Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: 'background.paper', height: 8, borderRadius: 4 }}>
                  <Box sx={{ width: '85%', bgcolor: theme.palette.primary.main, height: 8, borderRadius: 4 }} />
                </Box>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Corporate Demand</Typography>
                  <Typography variant="body2" fontWeight={600}>Very High</Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: 'background.paper', height: 8, borderRadius: 4 }}>
                  <Box sx={{ width: '92%', bgcolor: theme.palette.primary.main, height: 8, borderRadius: 4 }} />
                </Box>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Project Availability</Typography>
                  <Typography variant="body2" fontWeight={600}>Medium</Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: 'background.paper', height: 8, borderRadius: 4 }}>
                  <Box sx={{ width: '60%', bgcolor: theme.palette.primary.main, height: 8, borderRadius: 4 }} />
                </Box>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Market Volatility</Typography>
                  <Typography variant="body2" fontWeight={600}>Low</Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: 'background.paper', height: 8, borderRadius: 4 }}>
                  <Box sx={{ width: '30%', bgcolor: theme.palette.primary.main, height: 8, borderRadius: 4 }} />
                </Box>
              </Box>

              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Price Trend Confidence</Typography>
                  <Typography variant="body2" fontWeight={600}>High</Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: 'background.paper', height: 8, borderRadius: 4 }}>
                  <Box sx={{ width: '78%', bgcolor: theme.palette.primary.main, height: 8, borderRadius: 4 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
    )}
    </Box>
  );
}
