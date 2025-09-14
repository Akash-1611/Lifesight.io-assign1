import pandas as pd
import numpy as np
from datetime import datetime
import requests

def fetch_data_from_url(url):
    """
    Fetch CSV data from URL with error handling
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(url)
    except Exception as e:
        print(f"Error fetching data from {url}: {str(e)}")
        return None

def clean_business_data(df):
    """
    Clean and prepare business data for analysis
    """
    # Make a copy to avoid modifying original
    cleaned_df = df.copy()
    
    # Convert date column
    cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])
    
    # Clean column names - remove special characters and spaces
    cleaned_df.columns = cleaned_df.columns.str.replace('#', 'num').str.replace(' ', '_')
    
    # Convert numeric columns
    numeric_columns = ['total_revenue', 'gross_profit', 'COGS']
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
    # Handle missing values
    cleaned_df = cleaned_df.fillna(0)
    
    # Calculate additional metrics
    cleaned_df['profit_margin'] = (cleaned_df['gross_profit'] / cleaned_df['total_revenue'] * 100).round(2)
    cleaned_df['avg_order_value'] = (cleaned_df['total_revenue'] / cleaned_df['num_of_orders']).round(2)
    
    # Remove any duplicate dates
    cleaned_df = cleaned_df.drop_duplicates(subset=['date'])
    
    return cleaned_df

def clean_marketing_data(df, platform_name):
    """
    Clean and prepare marketing data for analysis
    """
    # Make a copy to avoid modifying original
    cleaned_df = df.copy()
    
    # Convert date column
    cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])
    
    # Add platform identifier
    cleaned_df['platform'] = platform_name
    
    # Convert numeric columns
    numeric_columns = ['impression', 'clicks', 'spend', 'attributed revenue']
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
    # Handle missing values
    cleaned_df = cleaned_df.fillna(0)
    
    # Calculate derived metrics
    cleaned_df['ctr'] = np.where(
        cleaned_df['impression'] > 0,
        (cleaned_df['clicks'] / cleaned_df['impression'] * 100).round(2),
        0
    )
    
    cleaned_df['cpc'] = np.where(
        cleaned_df['clicks'] > 0,
        (cleaned_df['spend'] / cleaned_df['clicks']).round(2),
        0
    )
    
    cleaned_df['roas'] = np.where(
        cleaned_df['spend'] > 0,
        (cleaned_df['attributed revenue'] / cleaned_df['spend']).round(2),
        0
    )
    
    cleaned_df['cpm'] = np.where(
        cleaned_df['impression'] > 0,
        (cleaned_df['spend'] / cleaned_df['impression'] * 1000).round(2),
        0
    )
    
    # Remove rows with zero impressions (likely invalid data)
    cleaned_df = cleaned_df[cleaned_df['impression'] > 0]
    
    return cleaned_df

def combine_marketing_data(facebook_df, google_df, tiktok_df):
    """
    Combine all marketing platform data into a single dataset
    """
    # Clean each platform's data
    facebook_clean = clean_marketing_data(facebook_df, 'Facebook')
    google_clean = clean_marketing_data(google_df, 'Google')
    tiktok_clean = clean_marketing_data(tiktok_df, 'TikTok')
    
    # Combine all platforms
    combined_df = pd.concat([facebook_clean, google_clean, tiktok_clean], ignore_index=True)
    
    # Sort by date
    combined_df = combined_df.sort_values('date')
    
    return combined_df

def create_unified_dataset(business_df, marketing_df):
    """
    Create a unified dataset combining business and marketing data
    """
    # Aggregate marketing data by date
    daily_marketing = marketing_df.groupby('date').agg({
        'spend': 'sum',
        'attributed revenue': 'sum',
        'clicks': 'sum',
        'impression': 'sum'
    }).reset_index()
    
    # Calculate daily marketing metrics
    daily_marketing['daily_roas'] = np.where(
        daily_marketing['spend'] > 0,
        (daily_marketing['attributed revenue'] / daily_marketing['spend']).round(2),
        0
    )
    
    daily_marketing['daily_ctr'] = np.where(
        daily_marketing['impression'] > 0,
        (daily_marketing['clicks'] / daily_marketing['impression'] * 100).round(2),
        0
    )
    
    # Merge with business data
    unified_df = pd.merge(business_df, daily_marketing, on='date', how='outer')
    
    # Fill missing values
    unified_df = unified_df.fillna(0)
    
    # Calculate correlation metrics
    unified_df['marketing_efficiency'] = np.where(
        unified_df['spend'] > 0,
        (unified_df['total_revenue'] / unified_df['spend']).round(2),
        0
    )
    
    return unified_df

def validate_data_quality(df, dataset_name):
    """
    Validate data quality and print summary statistics
    """
    print(f"\n=== Data Quality Report for {dataset_name} ===")
    print(f"Shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    
    # Check for negative values in key metrics
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            print(f"Warning: {negative_count} negative values in {col}")
    
    return True

if __name__ == "__main__":
    # This script can be run independently for data validation
    print("Data cleaning utilities loaded successfully!")
