import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    
    .insight-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f1f5f9, #e2e8f0);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_clean_data():
    """
    Load and clean all datasets with proper error handling
    """
    try:
        # URLs for the datasets
        urls = {
            'business': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/business-YECoODA5KKtmI4IIbwVl24o1PGO6qG.csv',
            'facebook': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Facebook-Jr4NjdoAto7VVJnPQusrGFITUZjrIu.csv',
            'google': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Google-LLSCdcqmXDixSN5WDcgPnYmQn5OiMB.csv',
            'tiktok': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/TikTok-4By8frzMQKKTVVmgEHE2daOuLnbs43.csv'
        }
        
        datasets = {}
        
        # Load business data
        business_df = pd.read_csv(urls['business'])
        business_df['date'] = pd.to_datetime(business_df['date'])
        
        # Clean numeric columns in business data
        numeric_cols = ['total revenue', 'gross profit', 'COGS']
        for col in numeric_cols:
            if col in business_df.columns:
                business_df[col] = pd.to_numeric(business_df[col], errors='coerce')
        
        # Fix column names (remove # symbols and spaces)
        business_df.columns = business_df.columns.str.replace('#', 'num').str.replace(' ', '_')
        datasets['business'] = business_df
        
        # Load and clean marketing data
        marketing_dfs = []
        
        for platform, url in [('facebook', urls['facebook']), ('google', urls['google']), ('tiktok', urls['tiktok'])]:
            df = pd.read_csv(url)
            df['date'] = pd.to_datetime(df['date'])
            df['platform'] = platform.title()
            
            # Clean numeric columns
            numeric_cols = ['impression', 'clicks', 'spend', 'attributed revenue']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate derived metrics
            df['ctr'] = (df['clicks'] / df['impression'] * 100).round(2)
            df['cpc'] = (df['spend'] / df['clicks']).round(2)
            df['roas'] = (df['attributed revenue'] / df['spend']).round(2)
            df['cpm'] = (df['spend'] / df['impression'] * 1000).round(2)
            
            marketing_dfs.append(df)
            datasets[platform] = df
        
        # Combine all marketing data
        marketing_combined = pd.concat(marketing_dfs, ignore_index=True)
        datasets['marketing_combined'] = marketing_combined
        
        return datasets
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_overview_metrics(business_df, marketing_df):
    """
    Create key performance indicators for the overview
    """
    # Business metrics
    total_revenue = business_df['total_revenue'].sum()
    total_orders = business_df['num_of_orders'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_customers = business_df['new_customers'].sum()
    
    # Marketing metrics
    total_spend = marketing_df['spend'].sum()
    total_attributed_revenue = marketing_df['attributed revenue'].sum()
    overall_roas = total_attributed_revenue / total_spend if total_spend > 0 else 0
    total_clicks = marketing_df['clicks'].sum()
    total_impressions = marketing_df['impression'].sum()
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_customers': total_customers,
        'total_spend': total_spend,
        'total_attributed_revenue': total_attributed_revenue,
        'overall_roas': overall_roas,
        'overall_ctr': overall_ctr
    }

def main():
    # Header
    st.markdown(
    "<h1 style='text-align: center; color: #3b82f6;'>📊 Marketing Intelligence Dashboard</h1>",
    unsafe_allow_html=True
)

    
    # Load data
    with st.spinner("Loading and processing data..."):
        datasets = load_and_clean_data()
    
    if datasets is None:
        st.error("Failed to load data. Please check the data sources.")
        return
    
    business_df = datasets['business']
    marketing_df = datasets['marketing_combined']
    
    # Sidebar filters
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Date range filter
    min_date = min(business_df['date'].min(), marketing_df['date'].min())
    max_date = max(business_df['date'].max(), marketing_df['date'].max())
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Platform filter
    platforms = ['All'] + list(marketing_df['platform'].unique())
    selected_platform = st.sidebar.selectbox("Select Platform", platforms)
    
    # State filter
    states = ['All'] + list(marketing_df['state'].unique())
    selected_state = st.sidebar.selectbox("Select State", states)
    
    # Filter data based on selections
    if len(date_range) == 2:
        start_date, end_date = date_range
        business_filtered = business_df[
            (business_df['date'] >= pd.Timestamp(start_date)) & 
            (business_df['date'] <= pd.Timestamp(end_date))
        ]
        marketing_filtered = marketing_df[
            (marketing_df['date'] >= pd.Timestamp(start_date)) & 
            (marketing_df['date'] <= pd.Timestamp(end_date))
        ]
    else:
        business_filtered = business_df
        marketing_filtered = marketing_df
    
    if selected_platform != 'All':
        marketing_filtered = marketing_filtered[marketing_filtered['platform'] == selected_platform]
    
    if selected_state != 'All':
        marketing_filtered = marketing_filtered[marketing_filtered['state'] == selected_state]
    
    # Calculate metrics
    metrics = create_overview_metrics(business_filtered, marketing_filtered)
    
    # Overview Section
    st.header("📈 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${metrics['total_revenue']:,.0f}",
            delta=f"{metrics['overall_roas']:.2f}x ROAS"
        )
    
    with col2:
        st.metric(
            "Total Orders",
            f"{metrics['total_orders']:,.0f}",
            delta=f"${metrics['avg_order_value']:.0f} AOV"
        )
    
    with col3:
        st.metric(
            "Marketing Spend",
            f"${metrics['total_spend']:,.0f}",
            delta=f"{metrics['overall_ctr']:.2f}% CTR"
        )
    
    with col4:
        st.metric(
            "New Customers",
            f"{metrics['total_customers']:,.0f}",
            delta=f"${metrics['total_attributed_revenue']:,.0f} Attributed"
        )
    
    # Key Insights
    st.markdown("""
    <div class="insight-box" style="color:#1f2937;">
        <h4>💡 Key Insights</h4>
        <ul>
            <li><strong>Performance:</strong> Marketing campaigns are generating a {:.2f}x return on ad spend</li>
            <li><strong>Efficiency:</strong> Average click-through rate of {:.2f}% indicates strong audience targeting</li>
            <li><strong>Growth:</strong> Acquired {:,} new customers with an average order value of ${:.0f}</li>
        </ul>
    </div>
    """.format(
        metrics['overall_roas'],
        metrics['overall_ctr'],
        metrics['total_customers'],
        metrics['avg_order_value']
    ), unsafe_allow_html=True)

    
    # Revenue and Marketing Performance
    st.header("💰 Revenue vs Marketing Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily revenue trend
        daily_business = business_filtered.groupby('date').agg({
            'total_revenue': 'sum',
            'num_of_orders': 'sum',
            'new_customers': 'sum'
        }).reset_index()
        
        fig_revenue = px.line(
            daily_business, 
            x='date', 
            y='total_revenue',
            title='Daily Revenue Trend',
            labels={'total_revenue': 'Revenue ($)', 'date': 'Date'}
        )
        fig_revenue.update_traces(line_color='#3b82f6', line_width=3)
        fig_revenue.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    transition_duration=500,
    hovermode="x unified",
    dragmode="pan",
    xaxis=dict(rangeslider=dict(visible=True))  # smooth zoom
)

        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Daily marketing spend vs attributed revenue
        daily_marketing = marketing_filtered.groupby('date').agg({
            'spend': 'sum',
            'attributed revenue': 'sum',
            'clicks': 'sum',
            'impression': 'sum'
        }).reset_index()
        
        fig_marketing = go.Figure()
        fig_marketing.add_trace(go.Scatter(
            x=daily_marketing['date'],
            y=daily_marketing['spend'],
            mode='lines',
            name='Ad Spend',
            line=dict(color='#ef4444', width=3)
        ))
        fig_marketing.add_trace(go.Scatter(
            x=daily_marketing['date'],
            y=daily_marketing['attributed revenue'],
            mode='lines',
            name='Attributed Revenue',
            line=dict(color='#10b981', width=3),
            yaxis='y2'
        ))
        
        fig_marketing.update_layout(
    title='Marketing Spend vs Attributed Revenue',
    xaxis_title='Date',
    yaxis=dict(title='Ad Spend ($)', side='left'),
    yaxis2=dict(title='Attributed Revenue ($)', side='right', overlaying='y'),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(x=0, y=1),
    transition_duration=500,
    hovermode="x unified",
    dragmode="pan",
    xaxis=dict(rangeslider=dict(visible=True))
)

        st.plotly_chart(fig_marketing, use_container_width=True)
    
    # Platform Performance Analysis
    st.header("🎯 Platform Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Platform comparison
        platform_metrics = marketing_filtered.groupby('platform').agg({
            'spend': 'sum',
            'attributed revenue': 'sum',
            'clicks': 'sum',
            'impression': 'sum'
        }).reset_index()
        
        platform_metrics['roas'] = platform_metrics['attributed revenue'] / platform_metrics['spend']
        platform_metrics['ctr'] = platform_metrics['clicks'] / platform_metrics['impression'] * 100
        
        fig_platform = px.bar(
            platform_metrics,
            x='platform',
            y='roas',
            title='Return on Ad Spend by Platform',
            color='roas',
            color_continuous_scale='viridis'
        )
        fig_platform.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_platform, use_container_width=True)
    
    with col2:
        # Spend distribution
        fig_spend = px.pie(
            platform_metrics,
            values='spend',
            names='platform',
            title='Marketing Spend Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_spend.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_spend, use_container_width=True)
    
    # Geographic Performance
    st.header("🗺️ Geographic Performance")
    
    state_performance = marketing_filtered.groupby('state').agg({
        'spend': 'sum',
        'attributed revenue': 'sum',
        'clicks': 'sum',
        'impression': 'sum'
    }).reset_index()
    
    state_performance['roas'] = state_performance['attributed revenue'] / state_performance['spend']
    state_performance['ctr'] = state_performance['clicks'] / state_performance['impression'] * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_state_roas = px.bar(
            state_performance.sort_values('roas', ascending=True),
            x='roas',
            y='state',
            orientation='h',
            title='ROAS by State',
            color='roas',
            color_continuous_scale='RdYlGn'
        )
        fig_state_roas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_state_roas, use_container_width=True)
    
    with col2:
        fig_state_spend = px.bar(
            state_performance.sort_values('spend', ascending=True),
            x='spend',
            y='state',
            orientation='h',
            title='Marketing Spend by State',
            color='spend',
            color_continuous_scale='Blues'
        )
        fig_state_spend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_state_spend, use_container_width=True)
    
    # Campaign Performance Deep Dive
    st.header("🔍 Campaign Performance Deep Dive")
    
    # Top performing campaigns
    campaign_performance = marketing_filtered.groupby(['platform', 'campaign']).agg({
        'spend': 'sum',
        'attributed revenue': 'sum',
        'clicks': 'sum',
        'impression': 'sum'
    }).reset_index()
    
    campaign_performance['roas'] = campaign_performance['attributed revenue'] / campaign_performance['spend']
    campaign_performance['ctr'] = campaign_performance['clicks'] / campaign_performance['impression'] * 100
    
    # Top 10 campaigns by ROAS
    top_campaigns = campaign_performance.nlargest(10, 'roas')
    
    fig_top_campaigns = px.bar(
        top_campaigns,
        x='roas',
        y='campaign',
        orientation='h',
        color='platform',
        title='Top 10 Campaigns by ROAS',
        labels={'roas': 'Return on Ad Spend', 'campaign': 'Campaign'}
    )
    fig_top_campaigns.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_top_campaigns, use_container_width=True)
    
    # Detailed data table
    st.header("📊 Detailed Performance Data")
    
    # Create a comprehensive summary table
    summary_table = campaign_performance.round(2)
    summary_table = summary_table.sort_values('roas', ascending=False)
    
    st.dataframe(
        summary_table,
        use_container_width=True,
        hide_index=True
    )
    
    # Export functionality
    st.header("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Campaign Performance"):
            csv = summary_table.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"campaign_performance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Business Metrics"):
            business_csv = business_filtered.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=business_csv,
                file_name=f"business_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
