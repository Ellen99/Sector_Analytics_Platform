import os
from flask import Blueprint, request, jsonify
import pandas as pd
from app.services.utils.stats_pipeline import check_stationarity, remove_trends_and_seasonality, perform_granger_causality_test
from app.services.utils.granger_interpreter import interpret_results_with_gpt
from app.services.data_retrieval.sector_data import SectorData
from app.services.utils.data_utils import build_openalex_query
from app.services.data_retrieval.openalex import fetch_openalex_data
from app.services.data_retrieval.fmp import get_monthly_sector_data

from datetime import datetime
main = Blueprint('main', __name__)

json_path = os.getenv("SECTOR_JSON_PATH", "./app/data/sectors.json")
api_key = os.getenv("FMP_API_KEY")
sector_data = SectorData(json_path)

sector_descriptions = sector_data.get_all_descriptions()

@main.route('/api/sector-names', methods=['GET'])
def get_sector_names():
    return jsonify({"sectors": list(sector_descriptions.keys())})

@main.route('/api/sector-data_old', methods=['GET'])
def get_sector_data_old():
    sector = request.args.get("sector")
    start_year = int(request.args.get("start_year", 2018))
    end_year = int(request.args.get("end_year", 2024))

    if not sector or not api_key:
        return jsonify({"error": "Missing required parameters: 'sector' and 'api_key'"}), 400

    try:
        # Fetch sector performance data
        performance_df = get_monthly_sector_data(sector, start_year, end_year, api_key)
        performance_df = performance_df.fillna(0)
        print("perf", performance_df)
        # Fetch publication data
        publication_df = fetch_openalex_data(sector=sector, sector_data=sector_data, start_year=start_year, end_year=end_year)
        publication_df = publication_df.fillna(0)

        if performance_df.empty and publication_df.empty:
            return jsonify({"message": "No data found for given parameters."}), 404

        return jsonify({
            "sector": sector,
            "start_year": start_year,
            "end_year": end_year,
            "performance_data": performance_df.to_dict(orient="records"),
            "publication_data": publication_df.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/api/sector-performance', methods=['GET'])
def get_sector_performance():
    sector = request.args.get("sector")
    start_year = int(request.args.get("start_year", 2018))
    end_year = int(request.args.get("end_year", 2024))
    # api_key = request.args.get("api_key")
    print("key", api_key)
    if not sector or not api_key:
        return jsonify({"error": "Missing required parameters: 'sector' and 'api_key'"}), 400

    try:
        df = get_monthly_sector_data(sector, start_year, end_year, api_key)

        if df.empty:
            return jsonify({"message": "No data found for given parameters."}), 404

        return jsonify({
            "sector": sector,
            "start_year": start_year,
            "end_year": end_year,
            "monthly_data": df.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/api/publications", methods=["GET"])
def get_publication_data():
    sector = request.args.get("sector")
    start_year = int(request.args.get("start_year", 2023))
    end_year = int(request.args.get("end_year", datetime.now().year))

    if not sector:
        return jsonify({"error": "Missing required parameter: sector"}), 400

    try:
        # sector_data = SectorData(json))  # Assuming you have a static mapping or JSON loader
        df = fetch_openalex_data(sector=sector, sector_data=sector_data, start_year=start_year, end_year=end_year)

        return jsonify({
            "sector": sector,
            "start_year": start_year,
            "end_year": end_year,
            "publication_counts": df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/api/hello")
def hello():
    return jsonify({"message": "Welcome to the Market Sector data analyzer website!"})

@main.route('/api/sector-description', methods=['GET'])
def get_sector_description():
    sector = request.args.get('sector')
    if sector in sector_descriptions:
        return jsonify({"name": sector, "description": sector_descriptions[sector]})
    else:
        return jsonify({"error": "Sector not found"}), 404
    
@main.route('/api/get-sectors', methods=['GET'])
def get_sectors():
    return jsonify(sector_descriptions)

@main.route('/api/sector-queries', methods=['GET'])
def get_sector_queries():
    queries = {}
    for sector in sector_data.get_all_sectors():
        encoded_query = build_openalex_query(sector, sector_data)
        queries[sector] = encoded_query
    return jsonify(queries)


@main.route('/api/granger-analysis', methods=['GET'])
def granger_analysis():
    """
    Perform Granger causality analysis and interpret results using GPT.
    """
    sector = request.args.get("sector")
    start_year = int(request.args.get("start_year", 2023))
    end_year = int(request.args.get("end_year", datetime.now().year))

    if not sector:
        return jsonify({"error": "Missing required parameters: 'sector'"}), 400

    try:
        # Step 1: Fetch performance and publication data
        performance_df = get_monthly_sector_data(sector, start_year, end_year, api_key)
        publication_df = fetch_openalex_data(sector=sector, sector_data=sector_data, start_year=start_year, end_year=end_year)

        # Step 2: Align data
        performance_df['month_year'] = pd.to_datetime(performance_df['month_year'])
        publication_df['year_month'] = pd.to_datetime(publication_df['year_month'])
        merged_df = pd.merge(
            performance_df[['month_year', 'monthly_return']],
            publication_df[['year_month', 'count']],
            left_on='month_year',
            right_on='year_month',
            how='inner'
        ).drop(columns=['year_month']).rename(columns={'count': 'publication_count'})

        # Step 3: Check stationarity
        is_stationary_perf = check_stationarity(merged_df['monthly_return'], "Monthly Return")
        is_stationary_pub = check_stationarity(merged_df['publication_count'], "Publication Count")

        # Step 4: Make data stationary if needed
        if not is_stationary_perf:
            merged_df['stationary_monthly_return'] = merged_df['monthly_return'].diff().dropna()
        else:
            merged_df['stationary_monthly_return'] = merged_df['monthly_return']

        if not is_stationary_pub:
            merged_df['stationary_publication_count'] = merged_df['publication_count'].diff().dropna()
        else:
            merged_df['stationary_publication_count'] = merged_df['publication_count']

        # Step 5: Remove trends and seasonality
        merged_df['detrended_monthly_return'] = remove_trends_and_seasonality(
            merged_df['stationary_monthly_return'].dropna(), "Monthly Return"
        )
        merged_df['detrended_publication_count'] = remove_trends_and_seasonality(
            merged_df['stationary_publication_count'].dropna(), "Publication Count"
        )

        # Step 6: Perform Granger causality test
        causality_df = merged_df[['detrended_monthly_return', 'detrended_publication_count']].dropna()
        granger_results, summary = perform_granger_causality_test(causality_df, max_lag=5)


        # Step 7: Interpret results using GPT
        gpt_prompt = f"Interpret the following Granger Causality test results:\n{granger_results}"
        gpt_interpretation = interpret_results_with_gpt(gpt_prompt)

        # Step 8: Return results
        return jsonify({
            "sector": sector,
            "start_year": start_year,
            "end_year": end_year,
            "granger_results": summary,
            "gpt_interpretation": gpt_interpretation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    """
    The function `get_sector_data` fetches sector data, performs Granger causality analysis, and returns
    comprehensive information including processed performance and publication data, statistical analysis
    results, correlation analysis, and GPT interpretation.
    :return: The function `get_sector_data` returns a JSON response containing various processed data
    and analysis results related to a specified sector. The returned data includes sector information,
    keyword data, performance data, publication data, processed performance and publication data,
    statistical information such as mean and variance, correlations, Granger causality test results,
    best lag value, raw and lagged correlations, comparison data, GPT interpretation of
    """
@main.route('/api/sector-data', methods=['GET'])
def get_sector_data():
    """
    Fetch sector data, perform Granger causality analysis, and return comprehensive information.
    """
    sector = request.args.get("sector")
    start_year = int(request.args.get("start_year", 2018))
    end_year = int(request.args.get("end_year", 2023))

    if not sector:
        return jsonify({"error": "Missing required parameters: 'sector'"}), 400

    try:
        sector_keywords = sector_data.get_keywords(sector)
        # Step 1: Fetch performance and publication data
        performance_df = get_monthly_sector_data(sector, start_year, end_year, api_key)
        publication_df = fetch_openalex_data(sector=sector, sector_data=sector_data, start_year=start_year, end_year=end_year)

        # Fill missing values
        performance_df = performance_df.fillna(0)
        publication_df = publication_df.fillna(0)

        if performance_df.empty and publication_df.empty:
            return jsonify({"message": "No data found for given parameters."}), 404

        # Step 2: Align data
        print("performance", performance_df)
        print("publication", publication_df)
        merged_df = pd.merge(
            performance_df[['month_year', 'monthly_return']],
            publication_df[['year_month', 'count']],
            left_on='month_year',
            right_on='year_month',
            how='inner'
        ).drop(columns=['year_month']).rename(columns={'count': 'publication_count'})

        # Step 3: Calculate statistical data
        stats = {
            "performance_mean": merged_df['monthly_return'].mean(),
            "performance_variance": merged_df['monthly_return'].var(),
            "publication_mean": merged_df['publication_count'].mean(),
            "publication_variance": merged_df['publication_count'].var(),
            "correlation": merged_df['monthly_return'].corr(merged_df['publication_count']),
        }

        # Step 4: Check stationarity
        is_stationary_perf = check_stationarity(merged_df['monthly_return'], "Monthly Return")
        is_stationary_pub = check_stationarity(merged_df['publication_count'], "Publication Count")

        # Step 5: Make data stationary if needed
        if not is_stationary_perf:
            merged_df['stationary_monthly_return'] = merged_df['monthly_return'].diff().dropna()
        else:
            merged_df['stationary_monthly_return'] = merged_df['monthly_return']

        if not is_stationary_pub:
            merged_df['stationary_publication_count'] = merged_df['publication_count'].diff().dropna()
        else:
            merged_df['stationary_publication_count'] = merged_df['publication_count']

        # Step 6: Remove trends and seasonality
        merged_df['detrended_monthly_return'] = remove_trends_and_seasonality(
            merged_df['stationary_monthly_return'].dropna(), "Monthly Return"
        )
        merged_df['detrended_publication_count'] = remove_trends_and_seasonality(
            merged_df['stationary_publication_count'].dropna(), "Publication Count"
        )

        # Step 7: Perform Granger causality test
        causality_df = merged_df[['detrended_monthly_return', 'detrended_publication_count']].dropna()
        granger_results, summary = perform_granger_causality_test(causality_df, max_lag=5)

        # Find the best lag based on lowest p-value
        best_lag = 1  # Default
        lowest_p_value = 1.0
        for lag, result in summary.items():
            if result['p_value'] < lowest_p_value and result['significant'] == 'Yes':
                lowest_p_value = result['p_value']
                best_lag = int(lag)
                
        # Prepare normalized and lagged comparison series
        series1 = merged_df['detrended_monthly_return']
        series2 = merged_df['detrended_publication_count']

        # Apply lag to series1 (typically performance data)
        if best_lag != 0:
            series1_lagged = series1.shift(best_lag)
        else:
            series1_lagged = series1

        # Combine series
        combined = pd.concat([series1_lagged, series2], axis=1).dropna()

        if not combined.empty:
            series1_clean = combined.iloc[:, 0]
            series2_clean = combined.iloc[:, 1]
            
            # Normalize both series
            series1_norm = (series1_clean - series1_clean.mean()) / series1_clean.std()
            series2_norm = (series2_clean - series2_clean.mean()) / series2_clean.std()
            
            # Create comparison data for the frontend
            comparison_data = []
            for date, value1, value2 in zip(series1_norm.index, series1_norm, series2_norm):
                if isinstance(date, pd.Timestamp):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = str(date)
                    
                comparison_data.append({
                    'date': date_str,
                    'performance': float(value1),
                    'publication': float(value2)
                })
        else:
            comparison_data = []

        # Create lagged publication series for PEARSON correlation analysis
        valid_data = merged_df[['detrended_monthly_return', 'detrended_publication_count']].dropna()
        if len(valid_data) > 0:
            if best_lag > 0:
                # Create a copy to avoid SettingWithCopyWarning
                valid_data_copy = valid_data.copy()
                # Shift publication data forward by best_lag
                valid_data_copy['lagged_publication'] = valid_data_copy['detrended_publication_count'].shift(-best_lag)
                # Drop NaN values created by the shift
                valid_data_copy = valid_data_copy.dropna()
                
                # Calculate Pearson correlation between original performance and lagged publication
                if len(valid_data_copy) > 1:  # Need at least 2 points for correlation
                    lagged_correlation = valid_data_copy['detrended_monthly_return'].corr(valid_data_copy['lagged_publication'])
                    lagged_correlation_formatted = round(lagged_correlation, 3)
                else:
                    lagged_correlation_formatted = "Insufficient data after lag"
            else:
                # If best lag is 0, use the regular correlation
                lagged_correlation = valid_data['detrended_monthly_return'].corr(valid_data['detrended_publication_count'])
                lagged_correlation_formatted = round(lagged_correlation, 3)
        else:
            lagged_correlation_formatted = "Insufficient data"

        # Add both raw and lagged correlations to the response
        stats["raw_correlation"] = round(stats["correlation"], 3)
        stats["lagged_correlation"] = lagged_correlation_formatted


        # Step 8: Interpret results using GPT
        gpt_prompt = f"Interpret the following Granger Causality test results for market sector {sector}:\n{granger_results}"
        gpt_interpretation = interpret_results_with_gpt(gpt_prompt)
        
        # Create processed data outputs
        # For performance data
        processed_performance = []
        for index, row in merged_df.iterrows():
            data_point = {
                'month_year': row['month_year'],
                'raw': row['monthly_return'],
            }
            # Only add if the value exists
            if 'stationary_monthly_return' in merged_df.columns and not pd.isna(row.get('stationary_monthly_return')):
                data_point['stationary'] = row['stationary_monthly_return']
            if 'detrended_monthly_return' in merged_df.columns and not pd.isna(row.get('detrended_monthly_return')):
                data_point['detrended'] = row['detrended_monthly_return']
            processed_performance.append(data_point)
            
        # For publication data
        processed_publications = []
        for index, row in merged_df.iterrows():
            data_point = {
                'year_month': row['month_year'],
                'raw': row['publication_count'],
            }
            # Only add if the value exists
            if 'stationary_publication_count' in merged_df.columns and not pd.isna(row.get('stationary_publication_count')):
                data_point['stationary'] = row['stationary_publication_count']
            if 'detrended_publication_count' in merged_df.columns and not pd.isna(row.get('detrended_publication_count')):
                data_point['detrended'] = row['detrended_publication_count']
            processed_publications.append(data_point)

        return jsonify({
            "sector": sector,
            "start_year": start_year,
            "end_year": end_year,
            "sector_keywords": sector_keywords,
            "performance_data": performance_df.to_dict(orient="records"),  # Keep original for backward compatibility
            "publication_data": publication_df.to_dict(orient="records"),  # Keep original for backward compatibility
            "processed_performance": processed_performance,
            "processed_publications": processed_publications,
            "best_lag": best_lag,
            "raw_correlation": stats["raw_correlation"],
            "lagged_correlation": stats["lagged_correlation"],
            "comparison_data": comparison_data,
            "gpt_interpretation": gpt_interpretation,
            "granger_results": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
