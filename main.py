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
        df = pd.read_csv(stringio)
        return df


def send_request(df):
    # Json sample
    sample = df.head().to_json(orient="records")
    res = requests.post(
        url="https://dust.tt/api/v1/apps/BenderV/67b0f56f46/runs",
        headers={
            "Authorization": "Bearer sk-83fa1f2fe42be11a814021401360f383",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "config": {
                    "CODES": {
                        "use_cache": False,
                        "model_id": "gpt-3.5-turbo-0301",
                        "provider_id": "openai",
                    },
                    "QUESTIONS": {
                        "use_cache": False,
                        "model_id": "code-davinci-002",
                        "provider_id": "openai",
                    },
                    "DESCRIPTION": {
                        "use_cache": False,
                        "model_id": "code-davinci-002",
                        "provider_id": "openai",
                    },
                },
                "specification_hash": "ab4cc0f801fc9654fea77fdf0eeaf4e7fcef3c7c221270ae89f4769c8140302c",
                "inputs": [{"data": sample}],
                "blocking": True,
            }
        ),
    )
    if res.status_code == 200:
        response = res.json()
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
    st.title("Graph Selector")
    st.set_option("deprecation.showPyplotGlobalUse", False)
    df = upload_csv()
    if df is not None:
        st.write("File uploaded successfully!")
        selected_graphs = []
        graphs = send_request(df)
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
