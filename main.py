import json
import os
import plotly.express as px
from io import StringIO
from typing import Dict
from dotenv import load_dotenv

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
import altair as alt

from graph_gen import get_graph_from_text

# Loads environment variables from .env file
load_dotenv()
plt.ioff()


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
    url = os.environ.get("DUST_APP_URL")
    hash = os.environ.get("DUST_APP_HASH")
    auth = "Bearer " + os.environ.get("DUST_APP_TOKEN")
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    data = {
        "specification_hash": hash,
        "config": {
            "CODES": {
                "provider_id": "openai",
                "model_id": "gpt-3.5-turbo-0301",
                "use_cache": True,
            },
            "CATEGORY": {
                "provider_id": "openai",
                "model_id": "code-davinci-002",
                "use_cache": True,
            },
            "SUGGESTIONS": {
                "provider_id": "openai",
                "model_id": "code-davinci-002",
                "use_cache": True,
            },
        },
        "blocking": True,
        "inputs": [{"data": data_sample}],
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response = response.json()
        return response["run"]["results"][0][0]["value"]


def plot_graph(data, graph_code, graph_title):
    exec(graph_code)
    st.subheader(graph_title)


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
                        code = graphs[counter]["plot"]
                        title = graphs[counter]["title"]
                        print("\n\n------------------\n\n")
                        print(code)
                        try:
                            plot_graph(data, code, title)
                        except Exception as e:
                            st.write(e)
                        counter += 1

    text_input = st.text_input(
        "Input any new analysis needed", "No text given"
    )
    df = pd.read_csv("data/google_website_data.csv")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    if text_input != "No text given":
        res_code = get_graph_from_text(text_input)
        columns = st.columns(2)
        for col in columns[:1]:
            with col:
                exec(res_code)


if __name__ == "__main__":
    main()
