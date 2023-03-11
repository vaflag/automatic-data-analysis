import streamlit as st
from typing import Dict
import sys
import os
import pandas as pd
#import matplotlib.pyplot as plt
import json
import requests
from io import StringIO

    
dust_input_endpoint = 'https://example.com/api'


def run_app():

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

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)

        url = dust_input_endpoint
        data = {'key': string_data}

        response = requests.post(url, json=data)

        print(response.content)





if __name__ == '__main__':
    run_app()