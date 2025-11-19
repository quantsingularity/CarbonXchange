import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Divider,
  Paper,
  Avatar,
  IconButton,
  Chip,
  useTheme,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  ArrowUpward,
  ArrowDownward,
  Refresh
} from '@mui/icons-material';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import useApi from '../hooks/useApi';
import { useWeb3 } from '../hooks/useWeb3';

// Fallback data for charts
const marketData = [
  { name: 'Jan', price: 4000, volume: 2400 },
  { name: 'Feb', price: 3000, volume: 1398 },
  { name: 'Mar', price: 2000, volume: 9800 },
  { name: 'Apr', price: 2780, volume: 3908 },
  { name: 'May', price: 1890, volume: 4800 },
  { name: 'Jun', price: 2390, volume: 3800 },
  { name: 'Jul', price: 3490, volume: 4300 },
];

const creditDistribution = [
  { name: 'Renewable Energy', value: 45 },
  { name: 'Reforestation', value: 30 },
  { name: 'Methane Capture', value: 25 },
];

const COLORS = ['#4CAF50', '#2196F3', '#FFC107'];

const listings = [
  { id: 1, seller: '0x1234...5678', amount: 100, pricePerToken: 0.5, project: 'Solar Farm - California' },
  { id: 2, seller: '0x8765...4321', amount: 200, pricePerToken: 0.4, project: 'Wind Energy - Texas' },
  { id: 3, seller: '0x9876...1234', amount: 150, pricePerToken: 0.6, project: 'Reforestation - Amazon' },
  { id: 4, seller: '0x5432...8765', amount: 75, pricePerToken: 0.7, project: 'Methane Capture - Colorado' },
];

export default function Dashboard() {
  const theme = useTheme();
  const api = useApi();
  const { isConnected, balance } = useWeb3();
  const [listings, setListings] = useState([]);
  const [creditDistribution, setCreditDistribution] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch listings from API
        const listingsData = await api.getListings();
        setListings(listingsData || []);

        // Fetch credit distribution from API
        const distributionData = await api.getCreditDistribution();
        setCreditDistribution(distributionData || []);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        // Use fallback data if API fails
        setListings(listings);
        setCreditDistribution(creditDistribution);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const refreshData = () => {
    // Refetch data when refresh button is clicked
    const fetchData = async () => {
      try {
        setLoading(true);
        const listingsData = await api.getListings();
        setListings(listingsData || []);

        const distributionData = await api.getCreditDistribution();
        setCreditDistribution(distributionData || []);
      } catch (error) {
        console.error("Error refreshing dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
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
              Dashboard
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Refresh />}
          onClick={refreshData}
        >
          Refresh Data
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Current Price
                </Typography>
                <IconButton size="small">
                  <MoreVert fontSize="small" />
                </IconButton>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                  $0.58
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                  <ArrowUpward sx={{ color: theme.palette.success.main, fontSize: 16 }} />
                  <Typography variant="body2" sx={{ color: theme.palette.success.main }}>
                    +5.2%
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                vs previous period
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Trading Volume
                </Typography>
                <IconButton size="small">
                  <MoreVert fontSize="small" />
                </IconButton>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                  12,543
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                  <ArrowUpward sx={{ color: theme.palette.success.main, fontSize: 16 }} />
                  <Typography variant="body2" sx={{ color: theme.palette.success.main }}>
                    +12.7%
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Credits traded this month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Your Balance
                </Typography>
                <IconButton size="small">
                  <MoreVert fontSize="small" />
                </IconButton>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                  {isConnected ? balance : '0'}
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Available carbon credits
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Market Forecast
                </Typography>
                <IconButton size="small">
                  <MoreVert fontSize="small" />
                </IconButton>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                  $0.62
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                  <ArrowUpward sx={{ color: theme.palette.success.main, fontSize: 16 }} />
                  <Typography variant="body2" sx={{ color: theme.palette.success.main }}>
                    +6.9%
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Predicted in 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Trends
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Historical price and volume data
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={marketData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="name" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line yAxisId="left" type="monotone" dataKey="price" stroke={theme.palette.primary.main} activeDot={{ r: 8 }} name="Price ($)" />
                    <Line yAxisId="right" type="monotone" dataKey="volume" stroke={theme.palette.secondary.main} name="Volume" />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Credit Distribution
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                By project type
              </Typography>
              <Box sx={{ height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height="80%">
                  <PieChart>
                    <Pie
                      data={creditDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {creditDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  {creditDistribution.map((entry, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', mx: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: COLORS[index % COLORS.length],
                          mr: 0.5,
                        }}
                      />
                      <Typography variant="caption">{entry.name}</Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Active Listings */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Active Listings
            </Typography>
            <Button variant="outlined" color="primary">
              View All
            </Button>
          </Box>
          <Box sx={{ overflowX: 'auto' }}>
            <Box sx={{ minWidth: 650 }}>
              <Box sx={{ display: 'flex', fontWeight: 600, p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
                <Box sx={{ flex: '0 0 5%' }}>#</Box>
                <Box sx={{ flex: '0 0 20%' }}>Project</Box>
                <Box sx={{ flex: '0 0 20%' }}>Seller</Box>
                <Box sx={{ flex: '0 0 15%' }}>Amount</Box>
                <Box sx={{ flex: '0 0 15%' }}>Price</Box>
                <Box sx={{ flex: '0 0 25%' }}>Action</Box>
              </Box>
              {listings.length > 0 ? (
                listings.map((listing) => (
                  <Box
                    key={listing.id}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      p: 2,
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      '&:hover': {
                        backgroundColor: theme.palette.action.hover,
                      }
                    }}
                  >
                    <Box sx={{ flex: '0 0 5%' }}>{listing.id}</Box>
                    <Box sx={{ flex: '0 0 20%' }}>{listing.project}</Box>
                    <Box sx={{ flex: '0 0 20%' }}>{listing.seller}</Box>
                    <Box sx={{ flex: '0 0 15%' }}>{listing.amount} CCO2</Box>
                    <Box sx={{ flex: '0 0 15%' }}>${listing.pricePerToken}</Box>
                    <Box sx={{ flex: '0 0 25%' }}>
                      <Button variant="contained" color="primary" size="small" sx={{ mr: 1 }}>
                        Buy
                      </Button>
                      <Button variant="outlined" size="small">
                        Details
                      </Button>
                    </Box>
                  </Box>
                ))
              ) : (
                <Box sx={{ p: 4, textAlign: 'center' }}>
                  <Typography color="textSecondary">No listings available</Typography>
                </Box>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </>
    )}
    </Box>
  );
}
