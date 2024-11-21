#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import ttest_1samp

def extract_financial_metrics(ticker, start_date, end_date, I):
    #Daily Data
    # Step 1: Download historical data for the stock
    data = yf.download(ticker, start=start_date, end=end_date)
    
    #Retrieve Dividends Information
    div = yf.Ticker(ticker).history(start=start_date, end=end_date)
    div_sum = div['Dividends'].sum()
    
    # Step 2: Calculate daily returns
    data['Daily Return'] = data['Adj Close'].pct_change()
    
    # Step 3: Calculate the required metrics
    arithmetic_average = data['Daily Return'].mean()
    geometric_average = np.exp(np.log1p(data['Daily Return']).mean()) - 1
    median_return = data['Daily Return'].median()
    std_dev_return = data['Daily Return'].std()
    
    # Return including Dividends
    p0 = data['Adj Close'][ticker].iloc[0]
    p1 = data['Adj Close'][ticker].iloc[-1]
    Total_value = p1 + div_sum
    Total_return = (Total_value / p0)
    average_daily_r_with_d = (Total_return)**(1 / len(data)) - 1
    
    # Return excluding Dividends
    average_daily_r_wo_d = (p1 / p0)**(1 / len(data)) - 1
    
    # Downside risk: Only consider negative returns
    downside_returns = data['Daily Return'][data['Daily Return'] < 0]
    downside_risk = np.sqrt(np.mean(np.square(downside_returns)))
    
    # Correlation with S&P 500
    sp500 = yf.download('^GSPC', start=start_date, end=end_date)
    sp500['SP500 Daily Return'] = sp500['Adj Close'].pct_change()
    correlation_sp500 = data['Daily Return'].corr(sp500['SP500 Daily Return'])
    
    # T-Statistic
    t_statistic, _ = ttest_1samp(data['Daily Return'].dropna(), 0)
    
    # Sharpe Ratio (Assume risk-free rate is 0 for simplicity)
    simplified_sharpe_ratio = arithmetic_average / std_dev_return
    
    # Number of Positive and Negative Periods
    num_positive_periods = (data['Daily Return'] > 0).sum()
    num_negative_periods = (data['Daily Return'] < 0).sum()
    percentage_positive = num_positive_periods / (num_negative_periods + num_positive_periods)
    
    # Beta calculation (covariance with market / variance of market)
    beta = data['Daily Return'].cov(sp500['SP500 Daily Return']) / sp500['SP500 Daily Return'].var()
    
    # Simulate $10,000 investment
    initial_investment = 10000
    final_value = (initial_investment / p0) * p1
    final_value1 = (initial_investment / p0) * Total_value
    
    min_daily_return = data['Daily Return'].min()
    max_daily_return = data['Daily Return'].max()

    if I == 'D':
        # Step 4: Print the calculated metrics
        print(f"Ticker: \033[1m{ticker}\033[0m\n")
        print(f"\033[1mData on a Daily Basis\033[0m\n")
        print(f"Arithmetic Average: {arithmetic_average:.4%}")
        print(f"Geometric Average: {geometric_average:.4%}")
        print(f"Median Return: {median_return:.4%}\n")
        print(f"Total dividends received: ${div_sum:.2f}")
        print(f"Average daily return excluding dividends: {average_daily_r_wo_d:.4%}")
        print(f"Average daily return including dividends: {average_daily_r_with_d:.4%}\n")
        print(f"Standard Deviation of Return: {std_dev_return:.4%}")
        print(f"Downside Risk: {downside_risk:.4%}")
        print(f"Simplified Sharpe Ratio: {simplified_sharpe_ratio:.4f}\n")
        print(f"Correlation with S&P 500: {correlation_sp500:.4f}")
        print(f"T-Statistic: {t_statistic:.4f}")
        print(f"Beta: {beta:.4f}\n")
        print(f"Number of Positive Periods: {num_positive_periods}")
        print(f"Number of Negative Periods: {num_negative_periods}")
        print(f"From {start_date} to {end_date}, {ticker} had {percentage_positive:.2%} of positive days.\n")
        print(f"Investing $10,000 in {start_date} becomes ${final_value:,.2f} in {end_date} --W/o dividends--")
        print(f"Investing $10,000 in {start_date} becomes ${final_value1:,.2f} in {end_date} --W/ dividends--\n")
        print(f"Minimum Daily Return: {min_daily_return:.4%}")
        print(f"Maximum Daily Return: {max_daily_return:.4%}\n")

    # Monthly Data
    # Resample to monthly data
    monthly_data = data['Adj Close'].resample('ME').last()
    monthly_returns = monthly_data.pct_change().dropna()
    
    sp500_monthly = sp500['Adj Close'].resample('ME').last()
    sp500_monthly_returns = sp500_monthly.pct_change().dropna()

    # Step 2: Calculate the required metrics
    arithmetic_average = monthly_returns[ticker].mean()
    geometric_average = np.exp(np.log1p(monthly_returns[ticker]).mean()) - 1
    median_return = monthly_returns[ticker].median()
    std_dev_return = monthly_returns[ticker].std()
    
    # Downside risk: Only consider negative returns
    downside_returns = monthly_returns[monthly_returns[ticker] < 0]
    downside_risk = np.sqrt(np.mean(np.square(downside_returns)))
    
    # Return excluding Dividends
    average_monthly_r_wo_d = (p1 / p0)**(1 / (len(data)/12)) - 1
    
    # Return including dividends
    average_monthly_r_with_d = (Total_return)**(1 / (len(data)/12)) - 1

    # Correlation with S&P 500
    correlation_sp500 = monthly_returns[ticker].corr(sp500_monthly_returns['^GSPC'])

    # T-Statistic
    t_statistic, _ = ttest_1samp(monthly_returns[ticker].dropna(), 0)
    
    # Sharpe Ratio (Assume risk-free rate is 0 for simplicity)
    simplified_sharpe_ratio = arithmetic_average / std_dev_return
    
    # Number of Positive and Negative Periods
    num_positive_periods = (monthly_returns[ticker] > 0).sum()
    num_negative_periods = (monthly_returns[ticker] < 0).sum()
    percentage_positive = num_positive_periods / (num_positive_periods + num_negative_periods)

    # Beta calculation (covariance with market / variance of market)
    beta = monthly_returns[ticker].cov(sp500_monthly_returns['^GSPC']) / sp500_monthly_returns['^GSPC'].var()
    
    # Calculate max and min annual returns
    max_monthly_return = monthly_returns[ticker].max()
    min_monthly_return = monthly_returns[ticker].min()
    
    if I == 'M':
        # Step 4: Print the calculated metrics
        print(f"Ticker: \033[1m{ticker}\033[0m\n")
        print(f"\033[1mData on a Monthly Basis\033[0m\n")
        print(f"Arithmetic Average: {arithmetic_average:.4%}")
        print(f"Geometric Average: {geometric_average:.4%}")
        print(f"Median Return: {median_return:.4%}\n")
        print(f"Total dividends received: ${div_sum:.2f}")
        print(f"Average monthly return excluding dividends: {average_monthly_r_wo_d:.4%}")
        print(f"Average monthly return including dividends: {average_monthly_r_with_d:.4%}\n")
        print(f"Standard Deviation of Return: {std_dev_return:.4%}")
        print(f"Downside Risk: {downside_risk:.4%}")
        print(f"Simplified Sharpe Ratio: {simplified_sharpe_ratio:.4f}\n")
        print(f"Correlation with S&P 500: {correlation_sp500:.4f}")
        print(f"T-Statistic: {t_statistic:.4f}")
        print(f"Beta: {beta:.4f}\n")
        print(f"Number of Positive Periods: {num_positive_periods}")
        print(f"Number of Negative Periods: {num_negative_periods}")
        print(f"From {start_date} to {end_date}, {ticker} had {percentage_positive:.2%} of positive years\n")
        print(f"Investing $10,000 in {start_date} becomes ${final_value:,.2f} in {end_date} --W/o dividends--")
        print(f"Investing $10,000 in {start_date} becomes ${final_value1:,.2f} in {end_date} --W/ dividends--\n")
        print(f"Maximum Monthly Return: {max_monthly_return:.4%}")
        print(f"Minimum Monthly Return: {min_monthly_return:.4%}\n")

    # Annual Data
    # Resample to annual data
    annual_data = data['Adj Close'].resample('YE').last()
    annual_returns = annual_data.pct_change().dropna()
    
    sp500_annual = sp500['Adj Close'].resample('YE').last()
    sp500_annual_returns = sp500_annual.pct_change().dropna()

    # Step 2: Calculate the required metrics
    arithmetic_average = annual_returns[ticker].mean()
    geometric_average = np.exp(np.log1p(annual_returns[ticker]).mean()) - 1
    median_return = annual_returns[ticker].median()
    std_dev_return = annual_returns[ticker].std()
    
    # Downside risk: Only consider negative returns
    downside_returns = annual_returns[annual_returns[ticker] < 0]
    downside_risk = np.sqrt(np.mean(np.square(downside_returns)))
    
    # Return excluding Dividends
    average_annual_r_wo_d = (p1 / p0)**(1 / (len(data)/252)) - 1
    
    # Return including dividends
    average_annual_r_with_d = (Total_return)**(1 / (len(data)/252)) - 1

    # Correlation with S&P 500
    correlation_sp500 = annual_returns[ticker].corr(sp500_annual_returns['^GSPC'])

    # T-Statistic
    t_statistic, _ = ttest_1samp(annual_returns[ticker].dropna(), 0)
    
    # Sharpe Ratio (Assume risk-free rate is 0 for simplicity)
    simplified_sharpe_ratio = arithmetic_average / std_dev_return
    
    # Number of Positive and Negative Periods
    num_positive_periods = (annual_returns[ticker] > 0).sum()
    num_negative_periods = (annual_returns[ticker] < 0).sum()
    percentage_positive = num_positive_periods / (num_positive_periods + num_negative_periods)

    # Beta calculation (covariance with market / variance of market)
    beta = annual_returns[ticker].cov(sp500_annual_returns['^GSPC']) / sp500_annual_returns['^GSPC'].var()
 
    # Calculate max and min annual returns
    max_annual_return = annual_returns[ticker].max()
    min_annual_return = annual_returns[ticker].min()
    
    if I == 'Y':
        # Step 4: Print the calculated metrics
        print(f"Ticker: \033[1m{ticker}\033[0m\n")
        print(f"\033[1mData on a Yearly Basis\033[0m\n")
        print(f"Arithmetic Average: {arithmetic_average:.4%}")
        print(f"Geometric Average: {geometric_average:.4%}")
        print(f"Median Return: {median_return:.4%}\n")
        print(f"Total dividends received: ${div_sum:.2f}")
        print(f"Average daily return excluding dividends: {average_annual_r_wo_d:.4%}")
        print(f"Average annual return including dividends: {average_annual_r_with_d:.4%}\n")
        print(f"Standard Deviation of Return: {std_dev_return:.4%}")
        print(f"Downside Risk: {downside_risk:.4%}")
        print(f"Simplified Sharpe Ratio: {simplified_sharpe_ratio:.4f}\n")
        print(f"Correlation with S&P 500: {correlation_sp500:.4f}")
        print(f"T-Statistic: {t_statistic:.4f}")
        print(f"Beta: {beta:.4f}\n")
        print(f"Number of Positive Periods: {num_positive_periods}")
        print(f"Number of Negative Periods: {num_negative_periods}")
        print(f"From {start_date} to {end_date}, {ticker} had {percentage_positive:.2%} of positive years.\n")
        print(f"Investing $10,000 in {start_date} becomes ${final_value:,.2f} in {end_date} --W/o dividends--")
        print(f"Investing $10,000 in {start_date} becomes ${final_value1:,.2f} in {end_date} --W/ dividends--\n")
        print(f"Maximum Annual Return: {max_annual_return:.4%}")
        print(f"Minimum Annual Return: {min_annual_return:.4%}")

