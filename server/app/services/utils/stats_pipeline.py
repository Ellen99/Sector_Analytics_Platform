import pandas as pd
import numpy as np
from numpy.linalg import norm
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

def check_stationarity(series, series_name):
    """
    Perform Augmented Dickey-Fuller (ADF) test to check stationarity.
    """
    print(f"\nChecking stationarity for {series_name}...")
    result = adfuller(series.dropna())
    print(f"ADF Statistic: {result[0]}")
    print(f"p-value: {result[1]}")
    if result[1] < 0.05:
        print(f"{series_name} is stationary.")
        return True
    else:
        print(f"{series_name} is not stationary.")
        return False

def remove_trends_and_seasonality(series, series_name, period=12):
    """
    Remove trends and seasonality using seasonal decomposition.
    """
    print(f"\nRemoving trends and seasonality for {series_name}...")
    print(series)
    decomposition = seasonal_decompose(series, model='additive', period=period)
    residual = decomposition.resid
    residual = residual.fillna(0)  # Handle NaN values in residuals
    print(f"Trends and seasonality removed for {series_name}.")
    return residual

def perform_granger_causality_test(df, max_lag=10):
    """
    Perform Granger Causality Test.
    """
    print("\nPerforming Granger Causality Test...")
    result = grangercausalitytests(df, max_lag, verbose=True)
    
    summary = {}

    for lag in range(1, max_lag + 1):
        f_test_result = result[lag][0]['ssr_ftest']
        f_stat = round(f_test_result[0], 4)
        p_value = round(f_test_result[1], 4)

        summary[lag] = {
            "f_stat": f_stat,
            "p_value": p_value,
            "significant": "Yes" if p_value < 0.05 else "No"
        }
        
    summary_str = "Granger Causality Test Summary:\n"
    for lag, data in summary.items():
        summary_str += (
            f"Lag {lag}: F-statistic = {data['f_stat']}, "
            f"P-value = {data['p_value']}, "
            f"Significant = {data['significant']}\n"
        )


    return summary_str, summary


def visualize_time_series(series1, series2, labels, lag=0):
    """
    Visualize two time series for comparison.
    """
    if lag != 0:
        series1 = series1.shift(lag)
    combined = pd.concat([series1, series2], axis=1).dropna()
    series1_clean = combined.iloc[:, 0]
    series2_clean = combined.iloc[:, 1]

    series1_norm = (series1_clean - series1_clean.mean()) / series1_clean.std()
    series2_norm = (series2_clean - series2_clean.mean()) / series2_clean.std()

    # series1_norm = (series1 - series1.mean()) / series1.std()
    # series2_norm = (series2 - series2.mean()) / series2.std()

  # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(series1_norm.index, series1_norm, label=f"{labels[0]} (lag {lag})")
    plt.plot(series2_norm.index, series2_norm, label=labels[1])
    plt.title(f"Normalized Time Series Comparison with Lag {lag}")
    plt.xlabel("Date")
    plt.ylabel("Z-score Normalized Values")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
