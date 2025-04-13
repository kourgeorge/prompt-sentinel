import streamlit as st
import pandas as pd
import requests
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import os

def load_data():
    """Fetches data from the server's /api/reports endpoint."""
    server_url = os.environ.get("SERVER_URL", "https://ps-server-lihl.onrender.com")
    api_endpoint = f"{server_url}/api/reports"
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if "reports" in data:
            return pd.DataFrame(data["reports"])
        else:
            st.error("Invalid data format received from the server.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
       st.error(f"Error connecting to the server: {e}")
       return pd.DataFrame()

def format_timestamp(row):
    """Formats the timestamp column."""
    try:
        timestamp = datetime.datetime.fromisoformat(row["timestamp"])
        return timestamp.strftime('%m/%d/%Y, %H:%M:%S')
    except (ValueError, KeyError):
        return "Invalid Date"

def format_secrets(row):
    """Formats the secrets column."""
    secrets = row.get("secrets", [])
    if secrets:
        return ", ".join(secrets)
    return ""

def format_sanitized_output(row):
    """Formats the sanitized output column."""
    sanitized_output = row.get("sanitized_output", "")
    if sanitized_output:
        return sanitized_output
    return ""





def display_data_table(df):
    """Displays the DataFrame in a styled, sortable table with pagination."""

    if df.empty:
        st.warning("No data available.")
        return pd.DataFrame()

    # Format columns
    if 'timestamp' in df.columns:
        df['timestamp'] = df.apply(format_timestamp, axis=1)
    df['secrets'] = df.apply(format_secrets, axis=1)
    df['sanitized_output'] = df.apply(format_sanitized_output, axis=1)


    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable sorting and filtering
    gb.configure_default_column(
      sortable=True,
      filter='agTextColumnFilter',
      resizable=True
    )


    # Customize columns
    gb.configure_column("app_id", headerName="App ID", width=150)
    gb.configure_column("session_id", headerName="Session ID", width=150)
    gb.configure_column("prompt", headerName="Prompt", wrapText=True, autoHeight=True)
    gb.configure_column("secrets", headerName="Secrets", width=250)
    gb.configure_column("sanitized_output", headerName="Sanitized Output", wrapText=True, autoHeight=True)
    gb.configure_column("timestamp", headerName="Timestamp", width=150)

    # Enable pagination
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10)

    gridOptions = gb.build()

    # Display the grid
    AgGrid(
      df,
      gridOptions=gridOptions,
      update_mode=GridUpdateMode.MODEL_CHANGED,
      data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
      fit_columns_on_grid_load=False,
      height=500,
    )

st.title("Reports Database")
data = load_data().fillna('')
display_data_table(data)
