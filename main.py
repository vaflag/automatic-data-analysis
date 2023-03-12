import json
import os
import plotly.express as px
from io import StringIO
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env file
plt.ioff()


def upload_csv():
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            pass
        with col2:
            st.markdown("<h3 style='color: black;'>" +
                        "Fetch data from Segment" + "</h3>", unsafe_allow_html=True)
            st.image('https://images.ctfassets.net/h6ufgtwb6nv1/k6BFb1F9uVFQKOQqStRDD/ed1b10765a5350d9cd950dbf67631338/SegmentLogo_Square_Green_RGB.png', width=40)
            st.button("Load Segment data")
        with col3:
            st.markdown("<h3 style='color: black;'>" +
                        "Upload a CSV 📂" + "</h3>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader('Add your file here')
        with col4:
            pass
    
    # uploaded_file = st.file_uploader("Choose a file")
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


def plot_graph(data, graph_code, graph_title):
    exec(graph_code)
    st.markdown("<h5 style='text-align: center; color: grey;'>" +
                graph_title + "</h3>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Analytics 🪄",
        layout="wide"
    )
    st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: black; font-size: 100px; margin-top: 100px;'>Let your data speak to you🎙</h1>",
                unsafe_allow_html=True)
    st.set_option("deprecation.showPyplotGlobalUse", False)
    st.markdown('#')
    data = upload_csv()

    if data is not None:
        with st.spinner('Loading...'):
            graphs = get_graphs(data)
        counter = 0
        while counter < len(graphs):
            with st.container():
                columns = st.columns(min(3, len(graphs) - counter))
                for column in columns:
                    with column:
                        chart_drawn = False
                        while (counter < len(graphs) and not (chart_drawn)):
                            code = graphs[counter]['plot']
                            title = graphs[counter]['title']
                            print('\n\n------------------\n\n')
                            try:
                                plot_graph(data, code, title)
                                chart_drawn = True
                            except Exception as e:
                                print(e)
                                pass
                            counter += 1


if __name__ == "__main__":
    main()
