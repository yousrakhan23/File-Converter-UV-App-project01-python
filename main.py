import streamlit as st
import pandas as pd
from io import BytesIO
import time

# Configuration
st.set_page_config(
    page_title="📂 File Converter & Cleaner", 
    layout="wide",
    page_icon="📂"
)
st.title("📂 File Converter & Cleaner")
st.write("Upload your CSV and Excel files to clean the data and convert formats effortlessly ✨🎉")

# Sidebar for additional options
with st.sidebar:
    st.header("Settings")
    max_file_size = st.number_input("Maximum file size (MB)", min_value=1, value=10)
    show_full_data = st.checkbox("Show full data preview", value=False)

def handle_file_upload(file):
    """Process individual file upload"""
    try:
        ext = file.name.split(".")[-1].lower()
        
        with st.spinner(f"Processing {file.name}..."):
            # Read file based on extension
            if ext == "csv":
                df = pd.read_csv(file)
            elif ext in ["xlsx", "xls"]:
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file format: {ext}")
                return None
            
            return df
            
    except Exception as e:
        st.error(f"Error reading {file.name}: {str(e)}")
        return None

def process_dataframe(df, file_name):
    """Process and clean the dataframe"""
    with st.expander(f"🔍 {file_name} - Data Processing", expanded=True):
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(20) if not show_full_data else df)
        
        # Missing values handling
        if st.checkbox(f"Fill Missing Values - {file_name}"):
            numeric_cols = df.select_dtypes(include="number").columns
            if not numeric_cols.empty:
                df.fillna(df[numeric_cols].mean(), inplace=True)
                st.success("Missing numeric values filled with mean!")
            else:
                st.warning("No numeric columns found for mean imputation")
            st.dataframe(df.head())
        
        # Column selection
        selected_columns = st.multiselect(
            f"Select Columns - {file_name}", 
            df.columns, 
            default=df.columns.tolist()
        )
        df = df[selected_columns]
        
        # Visualization
        if st.checkbox(f"📊 Show Chart - {file_name}"):
            numeric_cols = df.select_dtypes(include="number")
            if not numeric_cols.empty:
                chart_cols = st.multiselect(
                    f"Select columns to visualize - {file_name}",
                    numeric_cols.columns,
                    default=numeric_cols.columns[:2].tolist()
                )
                if chart_cols:
                    st.bar_chart(df[chart_cols])
            else:
                st.warning("No numeric columns available for visualization")
        
        return df

def convert_and_download(df, file_name, original_ext):
    """Handle file conversion and download"""
    format_choice = st.radio(
        f"Convert {file_name} to:", 
        ["CSV", "Excel"], 
        key=f"format_{file_name}"
    )
    
    if st.button(f"⬇️ Download {file_name} as {format_choice}"):
        try:
            output = BytesIO()
            if format_choice == "CSV":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file_name.replace(original_ext, "csv")
            else:
                df.to_excel(output, index=False)
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file_name.replace(original_ext, "xlsx")
            
            output.seek(0)
            st.download_button(
                "⬇️ Download File", 
                file_name=new_name, 
                data=output, 
                mime=mime,
                key=f"download_{file_name}"
            )
            st.success("File ready for download!")
            
        except Exception as e:
            st.error(f"Error during conversion: {str(e)}")

# Main file processing
files = st.file_uploader(
    "Upload your CSV or Excel file", 
    type=["csv", "xlsx", "xls"], 
    accept_multiple_files=True
)

if files:
    for file in files:
        # Check file size
        file_size = file.size / (1024 * 1024)  # in MB
        if file_size > max_file_size:
            st.warning(f"File {file.name} ({file_size:.2f} MB) exceeds maximum size limit. Skipping...")
            continue
            
        # Process each file in a container
        with st.container(border=True):
            st.subheader(f"Processing: {file.name}")
            
            # Read file
            df = handle_file_upload(file)
            if df is None:
                continue
                
            # Process data
            original_ext = file.name.split(".")[-1].lower()
            processed_df = process_dataframe(df, file.name)
            
            # Conversion and download
            convert_and_download(processed_df, file.name, original_ext)
            
            st.success(f"Processing completed for {file.name}! 🎉")