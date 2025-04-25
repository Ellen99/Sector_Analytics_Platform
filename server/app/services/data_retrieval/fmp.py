import requests
import pandas as pd

def fetch_sector_performance(sector: str, start_date: str, end_date: str, api_key: str):
    """
    Fetch sector performance data using the FMP Market Sector Performance API

    Args:
        sector (str): Sector name (e.g., 'Health Care', 'Energy')
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
        api_key (str): Your FMP API key

    Returns:
        DataFrame: Daily sector performance data
    """
    print(f"Fetching FMP sector performance data for {sector} from {start_date} to {end_date}")
    
    url = f"https://financialmodelingprep.com/stable/historical-sector-performance"
    # Query parameters
    params = {
        'sector': sector,
        'from': start_date,
        'to': end_date,
        'apikey': api_key
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)

        # Check if request was successful
        if response.status_code == 200:
            data = response.json()

            # Check if we received data
            if not data:
                print(f"No data retrieved for {sector}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Rename averageChange to make it clearer
            df = df.rename(columns={'averageChange': 'daily_return'})

            print(f"Retrieved {len(df)} days of sector performance data")
            return df
        else:
            print(f"Error from API: Status code {response.status_code}")
            print(response.text)
            return pd.DataFrame()

    except Exception as e:
        print(f"Error fetching sector performance data: {e}")
        return pd.DataFrame()


def get_monthly_sector_data(sector, start_year, end_year, api_key):
    """
    Get monthly sector performance data

    Args:
        sector (str): Sector name (e.g., 'Health Care', 'Energy')
        start_year (int): Start year
        end_year (int): End year
        api_key (str): Your FMP API key

    Returns:
        DataFrame: Monthly sector performance data
    """
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

    # Fetch daily data
    daily_data = fetch_sector_performance(sector, start_date, end_date, api_key)

    if daily_data.empty:
        print("No data to process")
        return pd.DataFrame()

    try:
        # Add month_year column for grouping
        daily_data['month_year'] = daily_data['date'].dt.strftime('%Y-%m')
        
        # Check range of daily returns to validate data
        min_return = daily_data['daily_return'].min()
        max_return = daily_data['daily_return'].max()
        print(f"Daily return range: {min_return:.4f} to {max_return:.4f}")
        if max_return > 1 or min_return < -1:
            print("Converting percentage returns to decimal form")
            daily_data['daily_return'] = daily_data['daily_return'] / 100
            
        # Group by month and get first/last day prices or returns
        # For returns, we'll use the cumulative effect of daily returns

        # Calculate the monthly return from daily returns
        # Group by month and calculate the cumulative return
        # If r_1, r_2, ... r_n are daily returns for a month, then
        # monthly return = (1+r_1)*(1+r_2)*...*(1+r_n) - 1

        # Group by month and calculate cumulative return
        monthly_returns = daily_data.groupby('month_year').apply(
            lambda x: (1 + x['daily_return']).prod() - 1
        ).reset_index()
        monthly_returns.columns = ['month_year', 'monthly_return']

        # date column from month_year
        monthly_returns['date'] = pd.to_datetime(monthly_returns['month_year'] + '-01')

        # Calculate next month returns for predictive analysis
        monthly_returns['next_month_return'] = monthly_returns['monthly_return'].shift(-1)

        return monthly_returns

    except Exception as e:
        print(f"Error processing monthly data: {e}")
        return pd.DataFrame()