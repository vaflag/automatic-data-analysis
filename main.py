import streamlit as st
from typing import Dict
import sys
import os
import pandas as pd
#import matplotlib.pyplot as plt
import json
import requests
from io import StringIO

#define endpoint    
dust_api_url = 'https://example.com/api'

#1 Upload Csv file
def upload_csv():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Split the string into lines
        lines = string_data.splitlines()

        # Keep at most the first five lines
        lines = lines[:5]

        # Join the lines back into a string
        string_data = '\n'.join(lines)
        data = {'key': string_data}

        # #Can be used wherever a "file-like" object is accepted:
        # dataframe = pd.read_csv(uploaded_file)
        # st.write(dataframe)
        return data
        

#2 Send the data to the API
def send_request(df):
    response = requests.post(dust_api_url, json=df)
    if response.status_code == 200:
        return response.json()
        print(response.content)
    else:
        return None

            
#3  Plot the graphs
def plot_graphs(graphs):
    num_graphs = len(graphs)
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8, num_graphs*4))
    for i, graph in enumerate(graphs):
        exec(graph['plot'])
        ax[i].set_title(graph['title'])
    st.pyplot(fig)



def main():
    st.title("Graph Selector")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    df = upload_csv()
    if df is not None:
        st.write("File uploaded successfully!")
        selected_graphs = []
        response = send_request(df)
        if response is None:
            st.write("Error retrieving response from API")
        else:
            graphs = response['graphs']
            for graph in graphs:
                if 'plot' in graph:
                    if st.checkbox(graph['title']):
                        selected_graphs.append(graph)
            if selected_graphs:
                plot_graphs(selected_graphs)
                if st.button('Next'):
                    st.write("Selected graphs:")
                    for graph in selected_graphs:
                        st.write(graph['title'])
            else:
                st.write("No graphs selected.")
    else:
        st.write("Please upload a CSV file.")

if __name__ == '__main__':
    main()