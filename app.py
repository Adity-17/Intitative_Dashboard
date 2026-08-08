import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

st.set_page_config(page_title="Project Tracker", layout="wide")

st.markdown("# 📊 Project Tracker Dashboard")

# Define expected columns
EXPECTED_COLUMNS = [
    'Areas',
    'Site Initiatives',
    'Description',
    'Possible Outcomes / Status',
    'Expected Savings',
    'ANK',
    'MDP',
    'TAR',
    'Pithampur',
    'External - 1',
    'External - 2',
    'Remarks'
]

with st.sidebar:
    st.title("📁 Upload Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # Try to read the file - support both Excel and CSV
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            # For Excel files, use engine='openpyxl' only if available, otherwise use default
            try:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            except:
                try:
                    df = pd.read_excel(uploaded_file, engine='xlrd')
                except:
                    df = pd.read_excel(uploaded_file)
        
        st.success("✅ File uploaded successfully!")
        
        # Clean columns
        df.columns = df.columns.str.strip()
        
        # ==================== DATA VALIDATION ====================
        st.markdown("---")
        st.markdown("## 📋 Data Validation Report")
        
        # Check for missing headers
        actual_columns = set(df.columns)
        expected_columns_set = set(EXPECTED_COLUMNS)
        
        missing_columns = expected_columns_set - actual_columns
        extra_columns = actual_columns - expected_columns_set
        
        # Create validation results container
        validation_col1, validation_col2, validation_col3 = st.columns(3)
        
        with validation_col1:
            st.metric("Total Columns Found", len(df.columns))
        
        with validation_col2:
            st.metric("Expected Columns", len(EXPECTED_COLUMNS))
        
        with validation_col3:
            st.metric("Missing Columns", len(missing_columns))
        
        # Display validation status
        if missing_columns:
            st.error("⚠️ **Missing Required Columns Detected!**")
            st.markdown("### ❌ Missing Headers:")
            for col in sorted(missing_columns):
                st.markdown(f"- `{col}`")
            
            st.info("""
            **Please ensure your Excel file contains all required columns:**
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
        else:
            st.success("✅ All required columns are present!")
        
        if extra_columns:
            st.warning("⚠️ **Extra Columns Detected** (not in standard format):")
            for col in sorted(extra_columns):
                st.markdown(f"- `{col}`")
        
        st.markdown("---")
        
        # ==================== COLUMN SUMMARY ====================
        st.markdown("## 📊 Column Details")
        
        col_detail_col1, col_detail_col2 = st.columns(2)
        
        with col_detail_col1:
            st.markdown("### ✅ Present Columns:")
            for col in sorted(actual_columns):
                non_null_count = df[col].notna().sum()
                null_count = df[col].isna().sum()
                st.markdown(f"""
                **{col}**
                - Data Type: `{df[col].dtype}`
                - Non-null: {non_null_count}
                - Null: {null_count}
                """)
        
        with col_detail_col2:
            if missing_columns:
                st.markdown("### ❌ Missing Columns:")
                for col in sorted(missing_columns):
                    st.markdown(f"- `{col}`")
                
                st.warning("⚠️ These columns need to be added to your Excel file")
            else:
                st.markdown("### ✅ All Columns Complete")
                st.success("Your file is properly formatted!")
        
        st.markdown("---")
        
        # ==================== PROCEED WITH ANALYSIS (if no missing columns) ====================
        if not missing_columns:
            st.markdown("## 📈 Dashboard Tabs")
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📋 Details", "📈 Analysis", "🔍 Data Quality"])
            
            with tab1:
                st.markdown("## Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📍 Total Initiatives", len(df))
                
                with col2:
                    unique_areas = df['Areas'].nunique() if 'Areas' in df.columns else 0
                    st.metric("🏢 Unique Areas", unique_areas)
                
                with col3:
                    status_types = df['Possible Outcomes / Status'].nunique() if 'Possible Outcomes / Status' in df.columns else 0
                    st.metric("🎯 Status Types", status_types)
                
                with col4:
                    # Count active sites
                    sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
                    active_sites = sum(1 for site in sites if site in df.columns and df[site].notna().sum() > 0)
                    st.metric("🏭 Active Sites", active_sites)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("## Status Distribution")
                    if 'Possible Outcomes / Status' in df.columns:
                        status_counts = df['Possible Outcomes / Status'].value_counts()
                        st.bar_chart(status_counts)
                
                with col2:
                    st.markdown("## Initiatives by Area")
                    if 'Areas' in df.columns:
                        area_counts = df['Areas'].value_counts()
                        st.bar_chart(area_counts)
                
                st.markdown("---")
                
                st.markdown("## Site-wise Initiative Count")
                sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
                site_counts = {}
                
                for site in sites:
                    if site in df.columns:
                        count = df[site].notna().sum()
                        site_counts[site] = count
                
                if site_counts:
                    site_df = pd.DataFrame(list(site_counts.items()), columns=['Site', 'Initiatives'])
                    st.bar_chart(site_df.set_index('Site'))
            
            with tab2:
                st.markdown("## Detailed Initiatives")
                
                # Add filters
                st.markdown("### 🔍 Filters")
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    if 'Areas' in df.columns:
                        selected_areas = st.multiselect(
                            "Filter by Area",
                            sorted(df['Areas'].unique())
                        )
                    else:
                        selected_areas = None
                
                with filter_col2:
                    if 'Possible Outcomes / Status' in df.columns:
                        selected_status = st.multiselect(
                            "Filter by Status",
                            sorted(df['Possible Outcomes / Status'].unique())
                        )
                    else:
                        selected_status = None
                
                with filter_col3:
                    search_text = st.text_input("🔎 Search Initiative Name")
                
                # Apply filters
                filtered_df = df.copy()
                
                if selected_areas and 'Areas' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Areas'].isin(selected_areas)]
                
                if selected_status and 'Possible Outcomes / Status' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Possible Outcomes / Status'].isin(selected_status)]
                
                if search_text and 'Site Initiatives' in filtered_df.columns:
                    filtered_df = filtered_df[
                        filtered_df['Site Initiatives'].str.contains(search_text, case=False, na=False)
                    ]
                
                st.markdown(f"**Showing {len(filtered_df)} of {len(df)} initiatives**")
                st.dataframe(filtered_df, use_container_width=True, height=500)
                
                st.markdown("---")
                
                # Download button
                col_down1, col_down2, col_down3 = st.columns(3)
                
                with col_down1:
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"initiatives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with tab3:
                st.markdown("## Data Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Areas' in df.columns:
                        st.markdown("### Initiatives by Area (Detailed)")
                        area_dist = df['Areas'].value_counts().reset_index()
                        area_dist.columns = ['Area', 'Count']
                        st.dataframe(area_dist, use_container_width=True, hide_index=True)
                        
                        st.markdown("#### Bar Chart")
                        st.bar_chart(area_dist.set_index('Area'))
                
                with col2:
                    if 'Possible Outcomes / Status' in df.columns:
                        st.markdown("### Status Summary (Detailed)")
                        status_dist = df['Possible Outcomes / Status'].value_counts().reset_index()
                        status_dist.columns = ['Status', 'Count']
                        st.dataframe(status_dist, use_container_width=True, hide_index=True)
                        
                        st.markdown("#### Bar Chart")
                        st.bar_chart(status_dist.set_index('Status'))
                
                st.markdown("---")
                
                # Expected Savings Analysis
                if 'Expected Savings' in df.columns:
                    st.markdown("### Expected Savings Analysis")
                    
                    # Try to parse savings
                    def parse_savings(val):
                        try:
                            if pd.isna(val) or val == '':
                                return 0
                            val_str = str(val).replace('₹', '').replace(',', '').strip()
                            return float(val_str.split()[0])
                        except:
                            return 0
                    
                    df['Savings_Parsed'] = df['Expected Savings'].apply(parse_savings)
                    
                    col_sav1, col_sav2, col_sav3 = st.columns(3)
                    with col_sav1:
                        st.metric("💰 Total Savings", f"₹{df['Savings_Parsed'].sum():,.0f}")
                    with col_sav2:
                        st.metric("📊 Avg Savings", f"₹{df['Savings_Parsed'].mean():,.0f}")
                    with col_sav3:
                        st.metric("📈 Max Savings", f"₹{df['Savings_Parsed'].max():,.0f}")
                    
                    st.markdown("#### Top 10 Initiatives by Savings")
                    top_10 = df.nlargest(10, 'Savings_Parsed')[['Site Initiatives', 'Areas', 'Expected Savings']]
                    st.dataframe(top_10, use_container_width=True, hide_index=True)
            
            with tab4:
                st.markdown("## Data Quality Report")
                
                st.markdown("### 📊 Missing Values per Column")
                missing_data = df.isnull().sum().reset_index()
                missing_data.columns = ['Column', 'Missing Count']
                missing_data['Missing %'] = (missing_data['Missing Count'] / len(df) * 100).round(2)
                missing_data = missing_data.sort_values('Missing Count', ascending=False)
                
                if missing_data['Missing Count'].sum() > 0:
                    st.dataframe(missing_data, use_container_width=True, hide_index=True)
                    st.bar_chart(missing_data.set_index('Column')['Missing Count'])
                else:
                    st.success("✅ No missing values found!")
                
                st.markdown("---")
                
                st.markdown("### 📋 Data Type Summary")
                dtype_summary = df.dtypes.reset_index()
                dtype_summary.columns = ['Column', 'Data Type']
                st.dataframe(dtype_summary, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                st.markdown("### 🔄 Duplicate Rows Check")
                duplicate_count = df.duplicated().sum()
                if duplicate_count > 0:
                    st.warning(f"⚠️ Found {duplicate_count} duplicate rows")
                    st.dataframe(df[df.duplicated(keep=False)], use_container_width=True)
                else:
                    st.success("✅ No duplicate rows found!")
                
                st.markdown("---")
                
                st.markdown("### 📈 Row and Column Statistics")
                stats_col1, stats_col2 = st.columns(2)
                
                with stats_col1:
                    st.metric("Total Rows", len(df))
                
                with stats_col2:
                    st.metric("Total Columns", len(df.columns))
        
        else:
            st.error("❌ Cannot proceed with analysis until all required columns are present")
            st.info("Please upload a file with all required columns as shown above")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Troubleshooting Tips:")
        st.markdown("""
        1. Ensure the file is a valid Excel (.xlsx, .xls) or CSV file
        2. Check that column names match exactly as expected
        3. Make sure there's no hidden formatting in the file
        4. Try converting to CSV and uploading again
        5. Use Excel to verify the file isn't corrupted
        """)

else:
    st.info("👈 Upload an Excel or CSV file to get started!")
    
    st.markdown("---")
    st.markdown("## 📝 Expected File Format")
    st.markdown("""
    Your Excel/CSV file should contain the following columns:
    
    | Column Name | Description | Example |
    |---|---|---|
    | Areas | Functional area | Operations, Finance, HR |
    | Site Initiatives | Name of initiative | Process Automation |
    | Description | Detailed description | Automation of manual processes |
    | Possible Outcomes / Status | Current status | In Progress, Completed |
    | Expected Savings | Expected financial savings | 500000 or ₹500,000 |
    | ANK | ANK site indicator | Active, Planned |
    | MDP | MDP site indicator | Active, Planned |
    | TAR | TAR site indicator | Active, Planned |
    | Pithampur | Pithampur site indicator | Active, Planned |
    | External - 1 | External site 1 indicator | Active, Planned |
    | External - 2 | External site 2 indicator | Active, Planned |
    | Remarks | Additional remarks | On track, Delayed |
    """)
    
    st.markdown("---")
    st.markdown("## ✅ Installation Requirements")
    st.code("""
    pip install streamlit pandas numpy
    """)
