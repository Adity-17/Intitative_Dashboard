import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

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
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
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
            
            tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Details", "Analysis", "Data Quality"])
            
            with tab1:
                st.markdown("## Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Initiatives", len(df))
                col2.metric("Unique Areas", df['Areas'].nunique() if 'Areas' in df.columns else 0)
                col3.metric("Status Types", df['Possible Outcomes / Status'].nunique() if 'Possible Outcomes / Status' in df.columns else 0)
                
                # Count active sites
                sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
                active_sites = sum(1 for site in sites if site in df.columns and df[site].notna().sum() > 0)
                col4.metric("Active Sites", active_sites)
                
                st.markdown("---")
                
                st.markdown("## Status Distribution")
                if 'Possible Outcomes / Status' in df.columns:
                    status_counts = df['Possible Outcomes / Status'].value_counts()
                    st.bar_chart(status_counts)
                
                st.markdown("## Initiatives by Area")
                if 'Areas' in df.columns:
                    area_counts = df['Areas'].value_counts()
                    st.bar_chart(area_counts)
                
                st.markdown("## Site-wise Initiative Count")
                sites = ['ANK', 'MDP', 'TAR', 'Pithampur', 'External - 1', 'External - 2']
                site_data = []
                for site in sites:
                    if site in df.columns:
                        count = df[site].notna().sum()
                        site_data.append({site: count})
                
                if site_data:
                    site_df = pd.DataFrame([{list(d.keys())[0]: list(d.values())[0] for d in site_data}])
                    st.bar_chart(site_df.T)
            
            with tab2:
                st.markdown("## Detailed Initiatives")
                
                # Add filters
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    if 'Areas' in df.columns:
                        selected_areas = st.multiselect(
                            "Filter by Area",
                            df['Areas'].unique()
                        )
                    else:
                        selected_areas = None
                
                with filter_col2:
                    if 'Possible Outcomes / Status' in df.columns:
                        selected_status = st.multiselect(
                            "Filter by Status",
                            df['Possible Outcomes / Status'].unique()
                        )
                    else:
                        selected_status = None
                
                with filter_col3:
                    search_text = st.text_input("Search Initiative Name")
                
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
                
                # Download button
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Data (CSV)",
                    data=csv,
                    file_name=f"initiatives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
            
            with tab3:
                st.markdown("## Data Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Areas' in df.columns:
                        st.markdown("### Initiatives by Area (Detailed)")
                        area_dist = df['Areas'].value_counts().reset_index()
                        area_dist.columns = ['Area', 'Count']
                        st.dataframe(area_dist, use_container_width=True)
                
                with col2:
                    if 'Possible Outcomes / Status' in df.columns:
                        st.markdown("### Status Summary (Detailed)")
                        status_dist = df['Possible Outcomes / Status'].value_counts().reset_index()
                        status_dist.columns = ['Status', 'Count']
                        st.dataframe(status_dist, use_container_width=True)
                
                st.markdown("---")
                
                # Expected Savings Analysis
                if 'Expected Savings' in df.columns:
                    st.markdown("### Expected Savings Analysis")
                    st.write(df['Expected Savings'].value_counts().head(10))
            
            with tab4:
                st.markdown("## Data Quality Report")
                
                st.markdown("### Missing Values per Column")
                missing_data = df.isnull().sum().reset_index()
                missing_data.columns = ['Column', 'Missing Count']
                missing_data['Missing %'] = (missing_data['Missing Count'] / len(df) * 100).round(2)
                missing_data = missing_data[missing_data['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
                
                if len(missing_data) > 0:
                    st.dataframe(missing_data, use_container_width=True)
                else:
                    st.success("✅ No missing values found!")
                
                st.markdown("---")
                
                st.markdown("### Data Type Summary")
                dtype_summary = df.dtypes.reset_index()
                dtype_summary.columns = ['Column', 'Data Type']
                st.dataframe(dtype_summary, use_container_width=True)
                
                st.markdown("---")
                
                st.markdown("### Duplicate Rows Check")
                duplicate_count = df.duplicated().sum()
                if duplicate_count > 0:
                    st.warning(f"⚠️ Found {duplicate_count} duplicate rows")
                else:
                    st.success("✅ No duplicate rows found!")
        
        else:
            st.error("❌ Cannot proceed with analysis until all required columns are present")
            st.info("Please upload a file with all required columns as shown above")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please ensure you're uploading a valid Excel file (.xlsx or .xls)")

else:
    st.info("👈 Upload an Excel file to get started!")
    
    st.markdown("---")
    st.markdown("## 📝 Expected File Format")
    st.markdown("""
    Your Excel file should contain the following columns:
    
    | Column Name | Description |
    |---|---|
    | Areas | Functional area of the initiative |
    | Site Initiatives | Name of the initiative |
    | Description | Detailed description |
    | Possible Outcomes / Status | Current status |
    | Expected Savings | Expected financial savings |
    | ANK | ANK site indicator |
    | MDP | MDP site indicator |
    | TAR | TAR site indicator |
    | Pithampur | Pithampur site indicator |
    | External - 1 | External site 1 indicator |
    | External - 2 | External site 2 indicator |
    | Remarks | Additional remarks |
    """)
