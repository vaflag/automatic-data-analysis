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


def upload_csv():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        # Transform to a pandas dataframe
        data = pd.read_csv(stringio)
        return data


def send_request(data):
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


# 3  Plot the graphs
def plot_graphs(df, graphs):
    num_graphs = len(graphs)
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8, num_graphs * 4))
    for i, graph in enumerate(graphs):
        code = textwrap.dedent(graph["plot"])
        # remove the ```python and ``` from the code
        code = code[10:-3]
        print(code)
        exec(code)
        ax[i].set_title(graph["title"])
    st.pyplot(fig)


def main():
    st.set_page_config(layout="wide")
    st.title("Graph Selector")
    st.set_option("deprecation.showPyplotGlobalUse", False)
    data = upload_csv()
    if data is not None:
        st.write("File uploaded successfully!")
        selected_graphs = []
        graphs = send_request(data)
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
    else:
        st.write("Please upload a CSV file.")


if __name__ == "__main__":
    main()
