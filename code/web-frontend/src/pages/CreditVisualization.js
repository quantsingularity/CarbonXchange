import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Tabs,
  Tab,
  Paper,
  Divider,
  useTheme,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import useApi from '../hooks/useApi';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Treemap,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend
} from 'recharts';
import { Refresh, FilterList } from '@mui/icons-material';

// Sample data for charts
const creditTypeData = [
  { name: 'Renewable Energy', value: 45 },
  { name: 'Reforestation', value: 30 },
  { name: 'Methane Capture', value: 25 },
];

const regionData = [
  { name: 'North America', value: 35 },
  { name: 'Europe', value: 30 },
  { name: 'Asia', value: 20 },
  { name: 'South America', value: 10 },
  { name: 'Africa', value: 5 },
];

const projectData = [
  {
    name: 'Renewable Energy',
    children: [
      { name: 'Solar Farms', size: 25 },
      { name: 'Wind Energy', size: 15 },
      { name: 'Hydroelectric', size: 5 },
    ],
  },
  {
    name: 'Reforestation',
    children: [
      { name: 'Amazon Basin', size: 15 },
      { name: 'African Forests', size: 10 },
      { name: 'Southeast Asia', size: 5 },
    ],
  },
  {
    name: 'Methane Capture',
    children: [
      { name: 'Landfill Gas', size: 15 },
      { name: 'Agricultural', size: 10 },
    ],
  },
];

const impactData = [
  { name: 'Jan', co2Reduction: 4000, trees: 2400 },
  { name: 'Feb', co2Reduction: 3000, trees: 1398 },
  { name: 'Mar', co2Reduction: 2000, trees: 9800 },
  { name: 'Apr', co2Reduction: 2780, trees: 3908 },
  { name: 'May', co2Reduction: 1890, trees: 4800 },
  { name: 'Jun', co2Reduction: 2390, trees: 3800 },
];

const COLORS = ['#4CAF50', '#2196F3', '#FFC107', '#FF5722', '#9C27B0'];

export default function CreditVisualization() {
  const theme = useTheme();
  const api = useApi();
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('1y');
  const [creditData, setCreditData] = useState([]);
  const [regionData, setRegionData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCreditData();
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
    fetchCreditData();
  };

  const fetchCreditData = async () => {
    try {
      setLoading(true);
      const distribution = await api.getCreditDistribution();
      if (distribution && distribution.length > 0) {
        setCreditData(distribution);
        // For this demo, we'll use the same data for region
        // In a real app, you would fetch different data
        setRegionData(regionData.length > 0 ? regionData : distribution);
      } else {
        // Fallback to sample data
        setCreditData(creditTypeData);
        setRegionData(regionData);
      }
    } catch (error) {
      console.error("Error fetching credit distribution:", error);
      // Use fallback data
      setCreditData(creditTypeData);
      setRegionData(regionData);
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
              Credit Visualization
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<Refresh />}
              onClick={fetchCreditData}
            >
              Refresh Data
            </Button>
          </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FilterList sx={{ mr: 1, color: theme.palette.text.secondary }} />
          <Typography variant="subtitle2" color="textSecondary">
            Filters:
          </Typography>
        </Box>
        <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={handleTimeRangeChange}
            label="Time Range"
          >
            <MenuItem value="1m">Last Month</MenuItem>
            <MenuItem value="3m">Last 3 Months</MenuItem>
            <MenuItem value="6m">Last 6 Months</MenuItem>
            <MenuItem value="1y">Last Year</MenuItem>
            <MenuItem value="all">All Time</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Tabs */}
      <Box sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 600,
            },
            '& .Mui-selected': {
              color: theme.palette.primary.main,
            },
            '& .MuiTabs-indicator': {
              backgroundColor: theme.palette.primary.main,
            }
          }}
        >
          <Tab label="Distribution" />
          <Tab label="Projects" />
          <Tab label="Environmental Impact" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Credit Distribution by Type
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Breakdown of carbon credits by project category
                </Typography>
                <Box sx={{ height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie
                        data={creditData.length > 0 ? creditData : creditTypeData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {(creditData.length > 0 ? creditData : creditTypeData).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    {creditTypeData.map((entry, index) => (
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
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Credit Distribution by Region
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Geographical distribution of carbon credit projects
                </Typography>
                <Box sx={{ height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie
                        data={regionData.length > 0 ? regionData : regionData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {(regionData.length > 0 ? regionData : regionData).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <Box sx={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', mt: 2 }}>
                    {regionData.map((entry, index) => (
                      <Box key={index} sx={{ display: 'flex', alignItems: 'center', mx: 1, mb: 1 }}>
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
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Project Breakdown
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Hierarchical view of carbon credit projects by type and size
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={projectData}
                  dataKey="size"
                  ratio={4/3}
                  stroke="#fff"
                  fill={theme.palette.primary.main}
                  content={({ root, depth, x, y, width, height, index, payload, colors, rank, name }) => {
                    return (
                      <g>
                        <rect
                          x={x}
                          y={y}
                          width={width}
                          height={height}
                          style={{
                            fill: depth < 2
                              ? COLORS[Math.floor((index / root.children.length) * COLORS.length) % COLORS.length]
                              : COLORS[Math.floor((index / root.children.length) * COLORS.length) % COLORS.length] + '80',
                            stroke: '#fff',
                            strokeWidth: 2 / (depth + 1e-10),
                            strokeOpacity: 1 / (depth + 1e-10),
                          }}
                        />
                        {depth === 1 && width > 50 && height > 30 && (
                          <text
                            x={x + width / 2}
                            y={y + height / 2 + 7}
                            textAnchor="middle"
                            fill="#fff"
                            fontSize={12}
                            fontWeight={600}
                          >
                            {name}
                          </text>
                        )}
                      </g>
                    );
                  }}
                >
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div style={{
                            backgroundColor: '#fff',
                            padding: '10px',
                            border: '1px solid #ccc',
                            borderRadius: '4px'
                          }}>
                            <p>{`${payload[0].name} : ${payload[0].value}`}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </Treemap>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      )}

      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Environmental Impact Metrics
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              CO₂ reduction and equivalent trees planted
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={impactData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis yAxisId="left" orientation="left" stroke={theme.palette.primary.main} />
                  <YAxis yAxisId="right" orientation="right" stroke={theme.palette.secondary.main} />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="co2Reduction" name="CO₂ Reduction (tons)" fill={theme.palette.primary.main} />
                  <Bar yAxisId="right" dataKey="trees" name="Trees Equivalent" fill={theme.palette.secondary.main} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                Impact Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, textAlign: 'center', bgcolor: theme.palette.primary.light + '20' }}>
                    <Typography variant="h4" color="primary" fontWeight={700}>
                      16,060
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total CO₂ Reduction (tons)
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, textAlign: 'center', bgcolor: theme.palette.secondary.light + '20' }}>
                    <Typography variant="h4" color="secondary" fontWeight={700}>
                      26,104
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Equivalent Trees Planted
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          </CardContent>
        </Card>
      </Box>
    )}
  </Box>
);
}
