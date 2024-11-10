from auth0_component import login_button
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

clientId = os.environ.get('clientId', '0wHhpxzCrBz4q29AD5xSQeE9v7BnfXln')
domain = os.environ.get('domain', 'dev-u4kd3wndapfdk6dr.us.auth0.com')
client_secret = os.environ.get('client_secret', 'GmnRsz6qHzq5dlNlcBlwr2o8ae1LR3f0OllD8iuUMhAYYPJEJmtIs3OzGKYLUL9Y')

st.title('Welcome to Traffictrack')

with st.echo():
    user_info = login_button(clientId=clientId, domain=domain)
    
    if user_info:
        st.write(f'Hi {user_info["nickname"]}')
        st.write(user_info)
    else:
        st.write("Please log in to continue.")
