import requests
import pandas as pd
from datetime import datetime
import time
from app.services.data_retrieval.sector_data import SectorData
from app.services.utils.data_utils import build_openalex_query


def fetch_openalex_data(sector: str, sector_data: SectorData,  start_year: int, end_year: int):
    """
    Fetch publication data from OpenAlex API based on sector and date range
    Returns a DataFrame with monthly publication counts

    Args:
        sector (str): Market sector name
        start_year (int): Start year for the search
        end_year (int): End year for the search

    Returns:
        DataFrame: Monthly publication counts
    
    Returns empty dataframe with correct structure if there's an error
    """
    print(f"Fetching OpenAlex publication data for sector: {sector}")
    
    search_query = build_openalex_query(sector_name=sector, sector_data=sector_data)
    # Initialize dataframe to store monthly counts
    date_range = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq='MS')
    pub_data = pd.DataFrame({
        'date': date_range,
        'count': 0,
        'year_month': [d.strftime('%Y-%m') for d in date_range]
    })

    try:
        # OpenAlex API base URL
        base_url = "https://api.openalex.org/works"
        
        # Process each year-month
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                # Skip future months
                current_date = datetime.now()
                if year > current_date.year or (year == current_date.year and month > current_date.month):
                    continue

                # Format dates for API query
                from_date = f"{year}-{month:02d}-01"

                # Determine last day of month
                if month in [4, 6, 9, 11]:
                    to_date = f"{year}-{month:02d}-30"
                elif month == 2:
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        to_date = f"{year}-{month:02d}-29"  # Leap year
                    else:
                        to_date = f"{year}-{month:02d}-28"
                else:
                    to_date = f"{year}-{month:02d}-31"

                # Parameters for OpenAlex API
                month_str = f"{year}-{month:02d}"
                filter_str = f"from_publication_date:{from_date},to_publication_date:{to_date}"

                params = {
                    'search': search_query,
                    'filter': filter_str,
                    'per_page': 1,
                    'mailto': 'echatikyan@gmail.com'
                }

                try:
                    # Make request to OpenAlex API
                    response = requests.get(base_url, params=params)
                    # print("base_url", base_url)
                    # print("params", params)
                    if response.status_code == 200:
                        data = response.json()
                        count = data['meta']['count']

                        # Update the dataframe
                        month_idx = pub_data[
                            (pub_data['date'].dt.year == year) &
                            (pub_data['date'].dt.month == month)
                        ].index

                        if len(month_idx) > 0:
                            pub_data.loc[month_idx[0], 'count'] = count

                        print(f"Found {count} publications for {year}-{month:02d}")
                    else:
                        print(f"Error from OpenAlex API: {response.status_code}")
                        print(response.text[:200] + "..." if len(response.text) > 200 else response.text)

                    # Sleep for API rate limits
                    time.sleep(0.2)

                except Exception as e:
                    print(f"Error fetching data for {year}-{month:02d}: {e}")
                    continue

        print(f"Successfully retrieved publication data: {len(pub_data)} months")
        return pub_data

    except Exception as e:
        print(f"Error in OpenAlex data collection: {e}")
        return pd.DataFrame(columns=['date', 'count', 'year_month'])