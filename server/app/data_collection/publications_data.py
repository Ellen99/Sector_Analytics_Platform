import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def fetch_pubmed_data(query, start_date, end_date, max_results=1000):
    """
    Fetch publication data from PubMed API for a specific query and date range
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Get publication IDs
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "mindate": start_date,
        "maxdate": end_date,
        "retmax": max_results,
        "retmode": "json",
        "sort": "date"
    }
    
    response = requests.get(search_url, params=search_params)
    search_results = response.json()
    
    if 'esearchresult' not in search_results or 'idlist' not in search_results['esearchresult']:
        return pd.DataFrame()
    
    id_list = search_results['esearchresult']['idlist']
    
    if not id_list:
        return pd.DataFrame()
    
    # Fetch publication details
    publications = []
    
    # Process in batches to avoid API limits
    batch_size = 100
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i+batch_size]
        
        summary_url = f"{base_url}esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(batch_ids),
            "retmode": "json"
        }
        
        summary_response = requests.get(summary_url, params=summary_params)
        summary_results = summary_response.json()
        
        if 'result' not in summary_results:
            continue
            
        for pub_id in batch_ids:
            if pub_id in summary_results['result']:
                pub_data = summary_results['result'][pub_id]
                pub_date = pub_data.get('pubdate', '')
                
                try:
                    # Try to parse the date
                    date_obj = datetime.strptime(pub_date, '%Y %b %d')
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                except:
                    try:
                        # Try with just year and month
                        date_obj = datetime.strptime(pub_date, '%Y %b')
                        formatted_date = date_obj.strftime('%Y-%m')
                    except:
                        try:
                            # Try with just year
                            date_obj = datetime.strptime(pub_date, '%Y')
                            formatted_date = date_obj.strftime('%Y')
                        except:
                            formatted_date = pub_date
                
                publications.append({
                    'id': pub_id,
                    'title': pub_data.get('title', ''),
                    'date': formatted_date,
                    'journal': pub_data.get('fulljournalname', ''),
                    'authors': ', '.join(author.get('name', '') for author in pub_data.get('authors', []) if author.get('name')),
                })
        
        # Be nice to the API
        time.sleep(1)
    
    return pd.DataFrame(publications)

def get_monthly_publication_counts(query, start_year, end_year):
    """
    Get monthly counts of publications for a specific query and year range
    """
    start_date = f"{start_year}/01/01"
    end_date = f"{end_year}/12/31"
    
    df = fetch_pubmed_data(query, start_date, end_date)
    
    if df.empty:
        return pd.DataFrame()
    
    # Convert date strings to datetime objects
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['date'])
    
    # Create a monthly count
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    monthly_counts = df.groupby('year_month').size().reset_index(name='count')
    monthly_counts['date'] = pd.to_datetime(monthly_counts['year_month'] + '-01')
    monthly_counts = monthly_counts.sort_values('date')
    
    return monthly_counts

if __name__ == "__main__":
    # Example: Fetch healthcare/biotech related publications
    healthcare_query = "(healthcare OR medicine OR biotech OR pharmaceutical OR drug OR therapy) AND journal article[pt]"
    monthly_data = get_monthly_publication_counts(healthcare_query, 2015, 2024)
    
    if not monthly_data.empty:
        monthly_data.to_csv("healthcare_publications_monthly.csv", index=False)
        print(f"Saved {len(monthly_data)} months of publication data")
    else:
        print("No data retrieved")