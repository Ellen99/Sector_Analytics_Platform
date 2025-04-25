# 📈 Sector Analytics Platform

**Predictive Insights from Scientific Literature to Market Sectors**

A web application for analyzing the relationship between academic publications and market sector performance using time series analysis and Granger causality tests.

## Overview

This application allows users to explore the potential causal relationships between academic research activity and financial market performance across various sectors. It integrates market data with research publication metrics to provide insights into how research might predict or follow market movements.

Key features:
- Time series visualization with multiple processing methods (raw, stationary, detrended)
- Granger causality tests to identify potential leading/lagging relationships
- Pearson correlation analysis with and without optimal time lag
- AI-powered interpretation of statistical results
- Interactive charts with normalized comparison view

## System Architecture

The application follows a client-server architecture:

- **Backend**: Flask-based Python API that retrieves market and publication data, performs time series analysis, and returns processed results
- **Frontend**: React application with Chart.js for data visualization and Material UI components

---
## Data Sources

- **Scientific Publications**: Metadata extracted from PubMed, including publication dates, keywords, and abstracts.
- **Financial Data**: Sector-specific stock performance metrics obtained from financial APIs such as Yahoo Finance.

---
## 🚀 Getting Started: Setup and Installation

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- Docker Compose

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/Ellen99/Sector_Analytics_Platform.git
   cd Sector_Analytics_Platform
   ```

2. Create Client environment file:

   ```bash
   # Create .env file in the client directory
   cd client
   touch .env
   ```
   Add the following environment variables:
   ```
   REACT_APP_API_URL=http://localhost:5050
   ```

3. Create Server environment file:
   ```bash
   # Create .env file in the server/app directory
   cd server/app
   touch .env
   ```
   Add the following environment variables:
   ```
   FRONTEND_ORIGIN=http://localhost:3000
   SECTOR_JSON_PATH=./app/data/sectors.json
   MAIL_TO_FOR_OPEN_ALEX_API=your-email@example.com
   FMP_API_KEY=your_fmp_api_key_here
   OPEN_AI_API_KEY=your_open_ai_api_key_here
   ```

4. Start the application:
   ```bash
   docker compose up
   ```

5. Access the application at `http://localhost:3000`

## Backend API

The backend provides several endpoints for data retrieval and analysis:

### GET `/api/sector-info`

Fetches sector data, performs Granger causality analysis, and returns comprehensive information.

**Query Parameters:**
- `sector` (required): The market sector to analyze
- `start_year` (optional): Start year for analysis (default: 2018)
- `end_year` (optional): End year for analysis (default: 2023)

**Response:**
```json
{
  "sector": "Technology",
  "start_year": 2018,
  "end_year": 2023,
  "sector_keywords": ["artificial intelligence", "machine learning", ...],
  "performance_data": [...],
  "publication_data": [...],
  "processed_performance": [...],
  "processed_publications": [...],
  "best_lag": 1,
  "comparison_data": [...],
  "raw_correlation": 0.321,
  "lagged_correlation": 0.567,
  "gpt_interpretation": "The analysis shows...",
  "granger_results": {...}
}
```

## Frontend Components

### SectorVisualization

The main visualization component that displays:
- Sector keywords used for publication search
- AI interpretation of the Granger causality results
- Summary of Granger causality test statistics
- Correlation analysis comparing raw and lagged correlations
- Normalized comparison chart with optimal lag
- Individual charts for sector performance and publication counts
- Processing toggle buttons for data transformation (raw, stationary, detrended)

## Time Series Analysis

The application performs several analysis steps:

1. **Data Collection**: Gathers market performance and academic publication data
2. **Stationarity Testing**: Checks if time series are stationary using Augmented Dickey-Fuller test
3. **Detrending**: Removes trends and seasonality from time series
4. **Granger Causality Testing**: Identifies if one time series helps predict another
5. **Correlation Analysis**: Calculates Pearson correlation with and without optimal lag
6. **Visualization**: Provides interactive charts for exploring the data and results

## Development

### Adding a New Sector

To add support for a new market sector:

1. Update the sector mapping in the backend to include keywords related to the new sector
2. Add the sector to the frontend dropdown options

### Extending the Analysis

The modular design allows for extending the analysis capabilities:

- Add new statistical tests in the `server/app/services/utils` directory
- Enhance visualization options in the React components
- Integrate additional data sources by creating new data fetcher modules


## Acknowledgments

- OpenAlex API for academic publication data
- Financial Markets API for sector performance data
- Chart.js for data visualization
- Material UI for the user interface components