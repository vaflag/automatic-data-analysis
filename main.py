import json
import os
import sys
import textwrap
from io import StringIO
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
import altair as alt

from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env file


def upload_csv():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        # Transform to a pandas dataframe
        data = pd.read_csv(stringio)
        return data


def get_graphs(data):
    # Json sample
    data_sample = json.loads(data.head().to_json(orient="records"))
    url = os.environ.get('DUST_APP_URL')
    hash = os.environ.get('DUST_APP_HASH')
    auth = 'Bearer ' + os.environ.get('DUST_APP_TOKEN')
    headers = {
        'Authorization': auth,
        'Content-Type': 'application/json'
    }
    data = {
        "specification_hash": hash,
        "config": {"CODES": {"provider_id": "openai", "model_id": "gpt-3.5-turbo-0301", "use_cache": True}, "CATEGORY": {"provider_id": "openai", "model_id": "code-davinci-002", "use_cache": True}, "SUGGESTIONS": {"provider_id": "openai", "model_id": "code-davinci-002", "use_cache": True}},
        'blocking': True,
        'inputs': [{'data': data_sample}]
    }
    response = requests.post(
        url,
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        response = response.json()
        return response["run"]["results"][0][0]["value"]



def plot_graph(data, graph_code):
    exec(graph_code)


def main():
    st.set_page_config(layout="wide")
    st.title("Graph Selector")
    # st.set_option("deprecation.showPyplotGlobalUse", False)
    data = upload_csv()

    if data is not None:
      graphs = get_graphs(data)
      counter = 0
      while counter < len(graphs):
        with st.container():
          columns = st.columns(min(3, len(graphs) - counter))
          for column in columns:
            with column:
              code = graphs[counter]['plot']
              print('\n\n------------------\n\n')
              print(code)
              try:
                plot_graph(data, code)
              except Exception as e:
                st.write(e)
              counter += 1
      return

      for i in range(len(graphs) / 3):
        with st.container():
          columns = st.columns(3)
          for column in columns:
             with column:
              code="""
# Convert the data to a pandas dataframe
df = pd.DataFrame(data)

# Convert the Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# Group the data by Date and calculate the sum of Weekly_Sales
df = df.groupby('Date')['Weekly_Sales'].sum().reset_index()

# Plot the graph
st.title('Weekly sales trend over time')
st.line_chart(df.set_index('Date'))
"""           
              try:
                plot_graph(data, code)
              except:
                st.write("Error")
              
      

    return

    if data is not None:
        st.write("File uploaded successfully!")
        selected_graphs = []
        graphs = get_graphs(data)

        for graph in graphs:
            code = graph['plot']

            print(code)
            exec(code)
            return
        return
        """
        if graphs is None:
            st.write("Error retrieving response from API")
        else:
            for graph in graphs:
                
                if "plot" in graph:
                    if st.checkbox(graph["title"]):
                        selected_graphs.append(graph)
            if selected_graphs:
                plot_graphs(df, selected_graphs)
                if st.button("Next"):
                    st.write("Selected graphs:")
                    for graph in selected_graphs:
                        st.write(graph["title"])
            else:
                st.write("No graphs selected.")
                """
    else:
        st.write("Please upload a CSV file.")


if __name__ == "__main__":
    main()
