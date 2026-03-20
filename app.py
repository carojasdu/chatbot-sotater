import os

import streamlit as st
from dotenv import load_dotenv

from ui.chat import render_chat_tab
from ui.documents import render_documents_tab
from ui.sidebar import render_sidebar

load_dotenv()

st.set_page_config(page_title="Sotater", page_icon="🔬", layout="wide")

# Validate required API keys
missing_keys = []
if not os.getenv("ANTHROPIC_API_KEY"):
    missing_keys.append("ANTHROPIC_API_KEY")
if not os.getenv("TAVILY_API_KEY"):
    missing_keys.append("TAVILY_API_KEY")

if missing_keys:
    st.error(
        f"Missing API keys: {', '.join(missing_keys)}. "
        "Create a `.env` file based on `.env.example`."
    )
    st.stop()

project_name = render_sidebar()

if project_name is None:
    st.markdown("## Welcome to Sotater")
    st.markdown(
        "Create a new project from the sidebar to start exploring "
        "state-of-the-art research on any topic."
    )
else:
    chat_tab, docs_tab = st.tabs(["Chat", "Documents"])

    with chat_tab:
        render_chat_tab(project_name)

    with docs_tab:
        render_documents_tab(project_name)
