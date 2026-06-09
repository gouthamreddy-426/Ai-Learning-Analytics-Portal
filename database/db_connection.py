"""
Database connection module.
Provides a singleton Supabase client used across the application.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

load_dotenv()

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    global _supabase_client

    if _supabase_client is None:

        # Streamlit Cloud
        if "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]

        # Local .env
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_KEY are missing"
            )

        _supabase_client = create_client(url, key)

    return _supabase_client
