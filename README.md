# Marketing Intelligence Dashboard

A comprehensive business intelligence dashboard that analyzes marketing performance across multiple platforms (Facebook, Google, TikTok) and correlates it with business outcomes.

## Features

- **Executive Summary**: Key performance indicators and metrics overview
- **Revenue Analysis**: Daily revenue trends and business performance
- **Marketing Performance**: Platform-wise campaign analysis and ROAS tracking
- **Geographic Insights**: State-level performance breakdown
- **Campaign Deep Dive**: Detailed campaign performance analysis
- **Data Export**: Download processed data for further analysis

## Key Metrics Tracked

### Business Metrics
- Total Revenue
- Number of Orders
- Average Order Value
- New Customers
- Gross Profit & COGS
- Profit Margins

### Marketing Metrics
- Return on Ad Spend (ROAS)
- Click-Through Rate (CTR)
- Cost Per Click (CPC)
- Cost Per Mille (CPM)
- Attributed Revenue
- Marketing Spend

## Data Sources

The dashboard processes data from four main sources:
- `business.csv`: Daily business performance data
- `facebook.csv`: Facebook campaign data
- `google.csv`: Google Ads campaign data
- `tiktok.csv`: TikTok campaign data

## Installation & Setup

1. Install required dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Run the dashboard:
\`\`\`bash
streamlit run app.py
\`\`\`

3. Open your browser and navigate to the provided local URL

## Dashboard Sections

### 1. Executive Summary
High-level KPIs and key insights for quick decision making

### 2. Revenue vs Marketing Performance
Correlation analysis between marketing spend and business outcomes

### 3. Platform Performance Analysis
Comparative analysis of Facebook, Google, and TikTok campaigns

### 4. Geographic Performance
State-wise breakdown of marketing effectiveness

### 5. Campaign Deep Dive
Detailed analysis of individual campaign performance

### 6. Data Export
Download processed data for offline analysis

## Technical Implementation

- **Data Processing**: Automated data cleaning and validation
- **Visualizations**: Interactive charts using Plotly
- **Filtering**: Dynamic date range, platform, and geographic filters
- **Performance**: Cached data loading for optimal performance
- **Export**: CSV download functionality for all processed data

## Insights Generated

The dashboard automatically generates insights on:
- Marketing ROI and efficiency
- Best performing platforms and campaigns
- Geographic performance variations
- Revenue correlation with marketing activities
- Customer acquisition trends

## Usage Tips

1. Use the sidebar filters to focus on specific time periods, platforms, or states
2. Hover over charts for detailed data points
3. Export data for deeper analysis in other tools
4. Monitor the executive summary for quick performance overview
5. Use the campaign deep dive for optimization opportunities

Built with ❤️ using Streamlit, Pandas, and Plotly
