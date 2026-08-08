import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Project Tracker Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .subheader {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Title and Description
st.markdown('<div class="header">📊 Project Tracker Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for file upload
with st.sidebar:
    st.title("📁 Upload Data")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload the project initiatives Excel file"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        try:
            st.session_state.df = pd.read_excel(uploaded_file)
            st.success("✅ File uploaded successfully!")
            st.info(f"📈 Total Initiatives: {len(st.session_state.df)}")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    
    st.markdown("---")
    st.markdown("### 📋 File Format Required:")
    st.markdown("""
    Expected columns:
    - Areas
    - Site Initiatives
    - Description
    - Possible Outcomes / Status
    - Expected Savings
    - ANK
    - MDP
    - TAR
    - Pithampur
    - External - 1
    - External - 2
    - Remarks
    """)

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Tab navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary",
        "🎯 Initiatives Details",
        "💰 Financial Analysis",
        "🏭 Site-wise Analysis",
        "📈 Status Overview"
    ])
    
    # ============== TAB 1: EXECUTIVE SUMMARY ==============
    with tab1:
        st.markdown('<div class="subheader">Executive Summary</div>', unsafe_allow_html=True)
        
        # Key Metrics Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Initiatives",
                len(df),
                "All active initiatives",
                delta_color="off"
            )
        
        with col2:
            try:
                total_savings = df['Expected Savings'].astype(str).str.replace(',', '').str.extract('(\d+)').astype(float).sum()
                st.metric(
                    "Total Expected Savings",
                    f"₹{total_savings:,.0f}",
                    "Cumulative savings",
                    delta_color="off"
                )
            except:
                st.metric("Total Expected Savings", "N/A", delta_color="off")
        
        with col3:
            unique_areas = df['Areas'].nunique() if 'Areas' in df.columns else 0
            st.metric(
                "Functional Areas",
                unique_areas,
                "Different areas covered",
                delta_color="off"
            )
        
        with col4:
            sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
            active_sites = sum(1 for site in sites if site in df.columns and df[site].notna().sum() > 0)
            st.metric(
                "Active Sites",
                active_sites,
                f"Out of {len(sites)} sites",
                delta_color="off"
            )
        
        st.markdown("---")
        
        # Status Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Status Distribution")
            try:
                status_col = 'Possible Outcomes / Status'
                if status_col in df.columns:
                    status_data = df[status_col].value_counts().reset_index()
                    status_data.columns = ['Status', 'Count']
                    
                    fig_status = go.Figure(data=[
                        go.Pie(
                            labels=status_data['Status'],
                            values=status_data['Count'],
                            hole=.3,
                            marker=dict(colors=['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6'])
                        )
                    ])
                    fig_status.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig_status, use_container_width=True)
                else:
                    st.warning("Status column not found")
            except Exception as e:
                st.error(f"Error creating status chart: {e}")
        
        with col2:
            st.markdown("### Initiatives by Area")
            try:
                if 'Areas' in df.columns:
                    area_data = df['Areas'].value_counts().reset_index()
                    area_data.columns = ['Area', 'Count']
                    
                    fig_area = px.bar(
                        area_data,
                        x='Area',
                        y='Count',
                        color='Count',
                        color_continuous_scale='Viridis',
                        text='Count'
                    )
                    fig_area.update_traces(textposition='auto')
                    fig_area.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_area, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating area chart: {e}")
        
        st.markdown("---")
        
        # Site-wise Initiative Count
        st.markdown("### Site-wise Initiative Coverage")
        
        sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
        site_counts = []
        
        for site in sites:
            if site in df.columns:
                count = df[site].notna().sum() - df[site].isna().sum()
                site_counts.append({'Site': site, 'Initiatives': max(0, count)})
        
        if site_counts:
            site_df = pd.DataFrame(site_counts)
            fig_sites = px.bar(
                site_df,
                x='Site',
                y='Initiatives',
                color='Initiatives',
                color_continuous_scale='Blues',
                text='Initiatives',
                title='Initiatives by Site'
            )
            fig_sites.update_traces(textposition='auto')
            fig_sites.update_layout(height=400)
            st.plotly_chart(fig_sites, use_container_width=True)
    
    # ============== TAB 2: INITIATIVES DETAILS ==============
    with tab2:
        st.markdown('<div class="subheader">Detailed Initiatives List</div>', unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Areas' in df.columns:
                selected_areas = st.multiselect(
                    "Filter by Area",
                    df['Areas'].unique(),
                    default=None
                )
            else:
                selected_areas = None
        
        with col2:
            if 'Possible Outcomes / Status' in df.columns:
                selected_status = st.multiselect(
                    "Filter by Status",
                    df['Possible Outcomes / Status'].unique(),
                    default=None
                )
            else:
                selected_status = None
        
        with col3:
            search_text = st.text_input("Search Initiatives", "")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_areas and 'Areas' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Areas'].isin(selected_areas)]
        
        if selected_status and 'Possible Outcomes / Status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Possible Outcomes / Status'].isin(selected_status)]
        
        if search_text:
            if 'Site Initiatives' in filtered_df.columns:
                filtered_df = filtered_df[
                    filtered_df['Site Initiatives'].str.contains(search_text, case=False, na=False)
                ]
        
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} initiatives**")
        
        # Display table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600,
            column_config={
                col: st.column_config.TextColumn(width="medium")
                for col in filtered_df.columns
            }
        )
        
        # Download filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"initiatives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # ============== TAB 3: FINANCIAL ANALYSIS ==============
    with tab3:
        st.markdown('<div class="subheader">Financial Analysis</div>', unsafe_allow_html=True)
        
        try:
            # Parse Expected Savings
            def parse_savings(val):
                if pd.isna(val) or val == '':
                    return 0
                if isinstance(val, (int, float)):
                    return float(val)
                val_str = str(val).replace(',', '').replace('₹', '').strip()
                try:
                    return float(val_str.split()[0])
                except:
                    return 0
            
            df['Savings_Value'] = df['Expected Savings'].apply(parse_savings)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total = df['Savings_Value'].sum()
                st.metric("Total Expected Savings", f"₹{total:,.0f}")
            
            with col2:
                avg = df['Savings_Value'].mean()
                st.metric("Average Savings per Initiative", f"₹{avg:,.0f}")
            
            with col3:
                max_val = df['Savings_Value'].max()
                st.metric("Maximum Savings", f"₹{max_val:,.0f}")
            
            st.markdown("---")
            
            # Savings by Area
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Savings by Area")
                if 'Areas' in df.columns:
                    savings_by_area = df.groupby('Areas')['Savings_Value'].sum().reset_index()
                    savings_by_area.columns = ['Area', 'Savings']
                    savings_by_area = savings_by_area.sort_values('Savings', ascending=False)
                    
                    fig = px.bar(
                        savings_by_area,
                        x='Area',
                        y='Savings',
                        color='Savings',
                        color_continuous_scale='Greens',
                        text='Savings',
                        title='Total Savings by Functional Area'
                    )
                    fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='auto')
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Savings Distribution")
                fig_dist = go.Figure(data=[
                    go.Histogram(x=df['Savings_Value'], nbinsx=30, marker_color='#3498db')
                ])
                fig_dist.update_layout(
                    title='Distribution of Savings',
                    xaxis_title='Savings Amount (₹)',
                    yaxis_title='Number of Initiatives',
                    height=400
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            
            st.markdown("---")
            
            # Top initiatives by savings
            st.markdown("### Top 10 Initiatives by Expected Savings")
            top_initiatives = df.nlargest(10, 'Savings_Value')[
                ['Site Initiatives', 'Areas', 'Expected Savings', 'Possible Outcomes / Status']
            ].reset_index(drop=True)
            
            st.dataframe(top_initiatives, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error in financial analysis: {e}")
    
    # ============== TAB 4: SITE-WISE ANALYSIS ==============
    with tab4:
        st.markdown('<div class="subheader">Site-wise Analysis</div>', unsafe_allow_html=True)
        
        sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
        available_sites = [site for site in sites if site in df.columns]
        
        # Site selector
        selected_site = st.selectbox("Select Site", available_sites)
        
        if selected_site:
            st.markdown(f"### {selected_site} - Site Details")
            
            # Site-specific data
            site_data = df[df[selected_site].notna()].copy()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"{selected_site} Initiatives", len(site_data))
            
            with col2:
                if 'Areas' in site_data.columns:
                    areas_count = site_data['Areas'].nunique()
                    st.metric("Functional Areas", areas_count)
            
            with col3:
                try:
                    site_data['Savings'] = site_data['Expected Savings'].apply(
                        lambda x: float(str(x).replace(',', '').replace('₹', '').split()[0]) 
                        if pd.notna(x) and str(x) != '' else 0
                    )
                    total_savings = site_data['Savings'].sum()
                    st.metric("Total Savings", f"₹{total_savings:,.0f}")
                except:
                    st.metric("Total Savings", "N/A")
            
            st.markdown("---")
            
            # Site initiatives by area
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {selected_site} - Initiatives by Area")
                if 'Areas' in site_data.columns:
                    area_dist = site_data['Areas'].value_counts().reset_index()
                    area_dist.columns = ['Area', 'Count']
                    
                    fig = px.pie(
                        area_dist,
                        values='Count',
                        names='Area',
                        title=f'Distribution by Area'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"### {selected_site} - Status Distribution")
                if 'Possible Outcomes / Status' in site_data.columns:
                    status_dist = site_data['Possible Outcomes / Status'].value_counts().reset_index()
                    status_dist.columns = ['Status', 'Count']
                    
                    fig = px.bar(
                        status_dist,
                        x='Status',
                        y='Count',
                        color='Count',
                        color_continuous_scale='Viridis',
                        text='Count'
                    )
                    fig.update_traces(textposition='auto')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown(f"### {selected_site} - Initiatives List")
            st.dataframe(site_data, use_container_width=True, height=400)
        
        st.markdown("---")
        
        # Cross-site comparison
        st.markdown("### Cross-Site Comparison")
        
        comparison_data = []
        for site in available_sites:
            site_initiatives = df[df[site].notna()]
            comparison_data.append({
                'Site': site,
                'Total Initiatives': len(site_initiatives),
                'Areas Covered': site_initiatives['Areas'].nunique() if 'Areas' in df.columns else 0
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        fig_compare = px.bar(
            comparison_df,
            x='Site',
            y=['Total Initiatives', 'Areas Covered'],
            barmode='group',
            title='Site Comparison',
            color_discrete_map={'Total Initiatives': '#3498db', 'Areas Covered': '#e74c3c'}
        )
        fig_compare.update_layout(height=400)
        st.plotly_chart(fig_compare, use_container_width=True)
    
    # ============== TAB 5: STATUS OVERVIEW ==============
    with tab5:
        st.markdown('<div class="subheader">Status Overview & KPIs</div>', unsafe_allow_html=True)
        
        try:
            status_col = 'Possible Outcomes / Status'
            
            if status_col in df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Status Summary Table")
                    status_summary = df[status_col].value_counts().reset_index()
                    status_summary.columns = ['Status', 'Count']
                    status_summary['Percentage'] = (status_summary['Count'] / len(df) * 100).round(2)
                    
                    st.dataframe(
                        status_summary,
                        use_container_width=True,
                        hide_index=True
                    )
                
                with col2:
                    st.markdown("### Status Breakdown")
                    fig = px.pie(
                        status_summary,
                        values='Count',
                        names='Status',
                        title='Percentage Distribution'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Timeline visualization
                st.markdown("### Initiatives by Status and Area")
                
                if 'Areas' in df.columns:
                    status_area = pd.crosstab(df['Areas'], df[status_col])
                    
                    fig = px.bar(
                        status_area.reset_index(),
                        x='Areas',
                        y=list(status_area.columns),
                        title='Status Distribution across Areas',
                        barmode='stack',
                        height=400
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Key insights
                st.markdown("### Key Insights")
                
                insights_col1, insights_col2, insights_col3 = st.columns(3)
                
                with insights_col1:
                    completed = len(df[df[status_col].str.contains('Completed|Done|Closed', case=False, na=False)])
                    completion_rate = (completed / len(df) * 100) if len(df) > 0 else 0
                    st.info(f"✅ Completion Rate: {completion_rate:.1f}%")
                
                with insights_col2:
                    inprogress = len(df[df[status_col].str.contains('In Progress|Ongoing', case=False, na=False)])
                    st.info(f"⏳ In Progress: {inprogress} initiatives")
                
                with insights_col3:
                    pending = len(df[df[status_col].str.contains('Pending|Not Started', case=False, na=False)])
                    st.info(f"📋 Pending: {pending} initiatives")
            
            else:
                st.warning("Status column not found in the data")
        
        except Exception as e:
            st.error(f"Error in status analysis: {e}")
    
    # ============== FOOTER ==============
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
        <p>Project Tracker Dashboard | Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p><small>This dashboard provides executive-level insights into project initiatives across different sites</small></p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("👈 Please upload an Excel file using the sidebar to start the dashboard")
