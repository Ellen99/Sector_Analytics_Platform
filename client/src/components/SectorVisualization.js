import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  ToggleButtonGroup, 
  ToggleButton, 
  Stack, 
  Chip,
  Divider,
  Paper,
  LinearProgress
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { Line } from 'react-chartjs-2';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend, Filler);

function SectorVisualization({ sector, startYear, endYear }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingStage, setLoadingStage] = useState('initializing');
  const [performanceProcessing, setPerformanceProcessing] = useState('raw');
  const [publicationProcessing, setPublicationProcessing] = useState('raw');

  useEffect(() => {
    if (sector) {
      setLoading(true);
      setLoadingStage('initializing');
      
      // Set timeout to simulate API stages for user feedback
      // TODO these should come from backend events or progress indicators
      setTimeout(() => setLoadingStage('fetching-market-data'), 3000);
      setTimeout(() => setLoadingStage('fetching-publications'), 7000);
      setTimeout(() => setLoadingStage('analyzing'), 12500);
      
      fetch(
        `${process.env.REACT_APP_API_URL}/api/sector-data?sector=${sector}&start_year=${startYear}&end_year=${endYear}`
      )
        .then((res) => res.json())
        .then((data) => {
          setData(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [sector, startYear, endYear]);

  const handlePerformanceProcessingChange = (event, newProcessing) => {
    if (newProcessing !== null) {
      setPerformanceProcessing(newProcessing);
    }
  };

  const handlePublicationProcessingChange = (event, newProcessing) => {
    if (newProcessing !== null) {
      setPublicationProcessing(newProcessing);
    }
  };
  const renderCorrelationInfo = () => {
    if (!data) return null;
    
    // Define color based on correlation strength
    const getCorrelationColor = (value) => {
      if (typeof value !== 'number') return 'text.secondary';
      const absValue = Math.abs(value);
      if (absValue >= 0.7) return value > 0 ? 'success.main' : 'error.main'; // Strong
      if (absValue >= 0.4) return value > 0 ? 'success.light' : 'error.light'; // Moderate
      return 'text.secondary'; // Weak
    };
    
    // Define interpretation based on correlation value
    const getCorrelationStrength = (value) => {
      if (typeof value !== 'number') return 'N/A';
      const absValue = Math.abs(value);
      if (absValue >= 0.7) return 'Strong';
      if (absValue >= 0.4) return 'Moderate';
      if (absValue >= 0.2) return 'Weak';
      return 'Very weak';
    };
    
    const rawCorrelation = data.raw_correlation;
    const laggedCorrelation = data.lagged_correlation;
  
    if (!rawCorrelation && !laggedCorrelation) return null;
    return (
      <Paper
        elevation={2}
        sx={{
          padding: '1.5rem',
          marginBottom: '2rem',
          borderRadius: '8px',
          backgroundColor: '#fafcff'
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Correlation Analysis
        </Typography>
        
        <Grid container spacing={3} sx={{ mt: 1 }}>
          {/* Raw Correlation */}
          <Grid item xs={12} md={6}>
            <Box 
              sx={{ 
                borderRadius: '8px', 
                padding: '1rem', 
                backgroundColor: '#f5f5f5',
                height: '100%'
              }}
            >
              <Typography variant="subtitle1" gutterBottom fontWeight={500}>
                Raw Correlation
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Direct relationship without accounting for time lag:
              </Typography>
              
              {typeof rawCorrelation === 'number' ? (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      fontWeight: 'bold', 
                      color: getCorrelationColor(rawCorrelation) 
                    }}
                  >
                    {rawCorrelation > 0 ? '+' : ''}{rawCorrelation}
                  </Typography>
                  <Box sx={{ ml: 2 }}>
                    <Typography variant="body2">
                      {getCorrelationStrength(rawCorrelation)} {rawCorrelation > 0 ? 'positive' : 'negative'} correlation
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Publications and market performance {Math.abs(rawCorrelation) < 0.2 ? 'show little direct relationship' : 'move together'}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography color="text.secondary">
                  {rawCorrelation || "Insufficient data for correlation analysis"}
                </Typography>
              )}
            </Box>
          </Grid>
          
          {/* Lagged Correlation */}
          <Grid item xs={12} md={6}>
            <Box 
              sx={{ 
                borderRadius: '8px', 
                padding: '1rem', 
                backgroundColor: '#f0f7ff',
                height: '100%'
              }}
            >
              <Typography variant="subtitle1" gutterBottom fontWeight={500}>
                Lagged Correlation (Lag: {data.best_lag || 0} months)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Relationship after adjusting for optimal time lag from Granger analysis:
              </Typography>
              
              {typeof laggedCorrelation === 'number' ? (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      fontWeight: 'bold', 
                      color: getCorrelationColor(laggedCorrelation) 
                    }}
                  >
                    {laggedCorrelation > 0 ? '+' : ''}{laggedCorrelation}
                  </Typography>
                  <Box sx={{ ml: 2 }}>
                    <Typography variant="body2">
                      {getCorrelationStrength(laggedCorrelation)} {laggedCorrelation > 0 ? 'positive' : 'negative'} correlation with lag
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Math.abs(laggedCorrelation) > Math.abs(rawCorrelation || 0) ? 
                        'Stronger relationship after accounting for time lag' : 
                        'Time lag does not strengthen the correlation'}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography color="text.secondary">
                  {laggedCorrelation || "Insufficient data for lagged correlation analysis"}
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>
        
        <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic', color: 'text.secondary' }}>
          Note: Pearson correlation measures the linear relationship between variables, ranging from -1 (perfect negative) to +1 (perfect positive).
        </Typography>
      </Paper>
    );
  };
  
  // Loading state with detailed information
  if (loading) {
    const loadingMessages = {
      'initializing': 'Initializing analysis for sector: ' + sector,
      'fetching-market-data': 'Fetching market performance data for ' + sector + ' from Financial Markets API...',
      'fetching-publications': 'Retrieving academic publication data from OpenAlex API...',
      'analyzing': 'Performing time series analysis and Granger causality tests...'
    };
    
    return (
      <Box sx={{ width: '100%', padding: '2rem' }}>
        <Typography variant="h5" gutterBottom>
          {sector} Sector Analysis
        </Typography>
        <Paper 
          elevation={1} 
          sx={{ 
            padding: '2rem', 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            gap: 2,
            backgroundColor: '#fafafa'
          }}
        >
          <Typography variant="h6" align="center">
            {loadingMessages[loadingStage]}
          </Typography>
          <Box sx={{ width: '80%', mt: 2 }}>
            <LinearProgress color="primary" />
          </Box>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
            Analyzing data from {startYear} to {endYear}
          </Typography>
        </Paper>
      </Box>
    );
  }

  if (!data || (!data.performance_data && !data.publication_data)) {
    return <Typography>No data available for the selected sector.</Typography>;
  }

  // Prepare data for the charts based on selected processing mode
  let performanceLabels = [];
  let performanceValues = [];
  let publicationLabels = [];
  let publicationValues = [];

  if (data.processed_performance && data.processed_publications) {
    performanceLabels = data.processed_performance.map(item => item.month_year);
    performanceValues = data.processed_performance.map(item => item[performanceProcessing]);
    
    publicationLabels = data.processed_publications.map(item => item.year_month);
    publicationValues = data.processed_publications.map(item => item[publicationProcessing]);
  } else {
    performanceLabels = data.performance_data.map(item => item.month_year);
    performanceValues = data.performance_data.map(item => item.monthly_return);
    
    publicationLabels = data.publication_data.map(item => item.year_month);
    publicationValues = data.publication_data.map(item => item.count);
  }

  // Prepare comparison chart data
  const comparisonChartData = {
    labels: data.comparison_data ? data.comparison_data.map(item => item.date) : [],
    datasets: [
      {
        label: `Sector Performance (lagged by ${data.best_lag || 0} months)`,
        data: data.comparison_data ? data.comparison_data.map(item => item.performance) : [],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 1,
        tension: 0.1
      },
      {
        label: 'Publication Count',
        data: data.comparison_data ? data.comparison_data.map(item => item.publication) : [],
        borderColor: 'rgba(153, 102, 255, 1)',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 1,
        tension: 0.1
      }
    ]
  };

  const comparisonChartOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: `Normalized Comparison (Best Lag: ${data.best_lag || 0} months)`
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Z-score Normalized Value'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        }
      }
    }
  };

  const getChartTitle = (dataType, processingType) => {
    const processingLabel = {
      'raw': 'Raw',
      'stationary': 'Stationarized',
      'detrended': 'Detrended'
    };
    
    return `${dataType} (${processingLabel[processingType]})`;
  };

  const performanceChartData = {
    labels: performanceLabels,
    datasets: [
      {
        label: getChartTitle('Sector Performance', performanceProcessing),
        data: performanceValues,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
      },
    ],
  };

  const publicationChartData = {
    labels: publicationLabels,
    datasets: [
      {
        label: getChartTitle('Publication Counts', publicationProcessing),
        data: publicationValues,
        borderColor: 'rgba(153, 102, 255, 1)',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        fill: true,
      },
    ],
  };

  return (
    <Box sx={{ padding: '2rem', width: '100%' }}>
      <Typography variant="h5" gutterBottom>
        Sector Performance and Publications for {sector}
      </Typography>
      
      {/* Keywords Section */}
      {data.sector_keywords && data.sector_keywords.length > 0 && (
        <Paper 
          elevation={0} 
          sx={{ 
            padding: '1rem', 
            marginBottom: '2rem', 
            backgroundColor: '#f7f9fc',
            border: '1px solid #e0e0e0',
            borderRadius: '8px'
          }}
        >
          <Typography variant="subtitle1" sx={{ fontWeight: 600, marginBottom: '0.5rem' }}>
            Publication Search Keywords:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {data.sector_keywords.map((keyword, index) => (
              <Chip 
                key={index} 
                label={keyword} 
                variant="outlined" 
                color="primary" 
                size="small"
              />
            ))}
          </Box>
        </Paper>
      )}
  
      {/* Grid for Text Boxes */}
      <Grid container spacing={2} sx={{ marginBottom: '2rem' }}>
        {data.gpt_interpretation && (
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                backgroundColor: '#f0f4ff',
                borderLeft: '6px solid rgb(28, 84, 139)',
                padding: '1rem',
                borderRadius: '4px',
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                💡 AI Insight:
              </Typography>
              <Typography>{data.gpt_interpretation}</Typography>
            </Box>
          </Grid>
        )}
  
        {data.granger_results && (
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                backgroundColor: '#fff7e6',
                borderLeft: '6px solid rgb(152, 72, 117)',
                padding: '1rem',
                borderRadius: '4px',
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Granger Causality Summary:
              </Typography>
              <ul style={{ paddingLeft: '1rem', marginTop: '0.5rem' }}>
                {Object.entries(data.granger_results).map(([lag, result]) => (
                  <li key={lag} style={{ marginBottom: '0.5rem' }}>
                    <Typography variant="body2">
                      <strong>Lag {lag}:</strong> F-stat = {result.f_stat}, p-value = {result.p_value} →{' '}
                      <strong>{result.significant === 'Yes' ? 'Significant' : 'Not Significant'}</strong>
                    </Typography>
                  </li>
                ))}
              </ul>
            </Box>
          </Grid>
        )}
      </Grid>
      {renderCorrelationInfo()}
      
      {/* Normalized Comparison Chart */}
      {data.comparison_data && data.comparison_data.length > 0 && (
        <Box sx={{ marginBottom: '2rem' }}>
          <Paper 
            elevation={3} 
            sx={{ 
              padding: '1rem', 
              borderRadius: '8px'
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Normalized Comparison with Optimal Lag
            </Typography>
            <Typography variant="body2" sx={{ marginBottom: '1rem', color: 'text.secondary' }}>
              This chart shows both time series normalized (z-score) and aligned with the optimal lag of {data.best_lag || 0} months 
              based on Granger causality analysis. This helps visualize potential leading/lagging relationships.
            </Typography>
            <Line data={comparisonChartData} options={comparisonChartOptions} />
          </Paper>
        </Box>
      )}
  
      {/* Grid for Individual Charts */}
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Stack direction="column" spacing={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Sector Performance</Typography>
              <ToggleButtonGroup
                value={performanceProcessing}
                exclusive
                onChange={handlePerformanceProcessingChange}
                size="small"
                aria-label="performance data processing"
              >
                <ToggleButton value="raw" aria-label="raw data">
                  Raw
                </ToggleButton>
                <ToggleButton value="stationary" aria-label="stationary data">
                  Stationary
                </ToggleButton>
                <ToggleButton value="detrended" aria-label="detrended data">
                  Detrended
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
            <Line data={performanceChartData} />
          </Stack>
        </Grid>
  
        <Grid item xs={12} md={6}>
          <Stack direction="column" spacing={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Publication Counts</Typography>
              <ToggleButtonGroup
                value={publicationProcessing}
                exclusive
                onChange={handlePublicationProcessingChange}
                size="small"
                aria-label="publication data processing"
              >
                <ToggleButton value="raw" aria-label="raw data">
                  Raw
                </ToggleButton>
                <ToggleButton value="stationary" aria-label="stationary data">
                  Stationary
                </ToggleButton>
                <ToggleButton value="detrended" aria-label="detrended data">
                  Detrended
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
            <Line data={publicationChartData} />
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
}

export default SectorVisualization;