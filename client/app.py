import streamlit as st
import pandas as pd
import requests
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import os

def load_data():
    """Fetches data from the server's /api/reports endpoint."""
    server_url = os.environ.get("SERVER_URL", "http://localhost:8000")
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

def format_start_time(row):
    """Formats the Start Time column."""
    try:
        start_time = datetime.datetime.fromisoformat(row["Start Time"])
        return start_time.strftime('%m/%d/%Y, %H:%M:%S')
    except (ValueError, KeyError):
        return "Invalid Date"

def format_latency(row):
    """Formats the Latency column."""
    if isinstance(row["Latency"], float):
        return f"{row['Latency']:.2f}s"
    return "Invalid Latency"

def format_error(row):
  """Formats the Error column."""
  if row["Error"] is None:
    return ""
  return row["Error"]

def display_data_table(df):
    """Displays the DataFrame in a styled, sortable table with pagination."""

    if df.empty:
        st.warning("No data available.")
        return pd.DataFrame()

    # Format columns
    df['Start Time'] = df.apply(format_start_time, axis=1)
    df['Latency'] = df.apply(format_latency, axis=1)
    df['Error'] = df.apply(format_error, axis=1)


    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable sorting and filtering
    gb.configure_default_column(
      sortable=True,
      filter='agTextColumnFilter',
      resizable=True
    )


    # Customize columns
    gb.configure_column("Name", headerName="Name", width=150)
    gb.configure_column("Input", headerName="Input", wrapText=True, autoHeight=True)
    gb.configure_column("Output", headerName="Output", wrapText=True, autoHeight=True)
    gb.configure_column("Error", headerName="Error", width=250)
    gb.configure_column("Start Time", headerName="Start Time", width=150)
    gb.configure_column("Latency", headerName="Latency", width=100)
    gb.configure_column("Dataset", headerName="Dataset", width=100)
    gb.configure_column("Annotation Queue", headerName="Annotation Queue", width=150)
    gb.configure_column("Tokens", headerName="Tokens", width=80)

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
