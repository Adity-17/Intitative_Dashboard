import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Project Tracker", layout="wide")

st.markdown("# 📊 Project Tracker Dashboard")

with st.sidebar:
    st.title("📁 Upload Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File uploaded successfully!")
        
        # Clean columns
        df.columns = df.columns.str.strip()
        
        tab1, tab2, tab3 = st.tabs(["Overview", "Details", "Analysis"])
        
        with tab1:
            st.markdown("## Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Initiatives", len(df))
            col2.metric("Unique Areas", df['Areas'].nunique() if 'Areas' in df.columns else 0)
            col3.metric("Status Count", df['Possible Outcomes / Status'].nunique() if 'Possible Outcomes / Status' in df.columns else 0)
            col4.metric("Unique Sites", 6)  # Fixed 6 sites
            
            st.markdown("## Status Distribution")
            if 'Possible Outcomes / Status' in df.columns:
                status_counts = df['Possible Outcomes / Status'].value_counts()
                st.bar_chart(status_counts)
            
            st.markdown("## Initiatives by Area")
            if 'Areas' in df.columns:
                area_counts = df['Areas'].value_counts()
                st.bar_chart(area_counts)
        
        with tab2:
            st.markdown("## Detailed Initiatives")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"initiatives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        
        with tab3:
            st.markdown("## Data Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                if 'Areas' in df.columns:
                    st.markdown("### Initiatives by Area")
                    area_dist = df['Areas'].value_counts()
                    st.write(area_dist)
            
            with col2:
                if 'Possible Outcomes / Status' in df.columns:
                    st.markdown("### Status Summary")
                    status_dist = df['Possible Outcomes / Status'].value_counts()
                    st.write(status_dist)
    
    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("👈 Upload an Excel file to get started!")
