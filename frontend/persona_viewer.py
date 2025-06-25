#!/usr/bin/env python3
"""
Persona Viewer - Streamlit component for viewing and managing email personas.
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any

def format_date(date_str: str) -> str:
    """Format date string for display."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str

def display_persona_card(persona: Dict[str, Any]):
    """Display a persona as a card."""
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Avatar/icon
            st.markdown(f"### {persona['first_name'][0].upper()}")
        
        with col2:
            # Persona info
            st.markdown(f"**{persona['first_name']}** ({persona['persona_type']})")
            st.caption(f"Email: {persona['sender']}")
            
            # Stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Emails", persona['email_count'])
            with col_b:
                st.metric("Topics", len(persona['topics']))
            with col_c:
                st.metric("Labels", len(persona['labels']))
            
            # Topics
            if persona['topics']:
                st.markdown("**Topics:** " + ", ".join(persona['topics']))
            
            # Labels
            if persona['labels']:
                st.markdown("**Labels:** " + ", ".join(persona['labels']))
            
            # Dates
            st.caption(f"First seen: {format_date(persona['first_seen'])}")
            st.caption(f"Last seen: {format_date(persona['last_seen'])}")

def main():
    st.set_page_config(
        page_title="Email Personas",
        page_icon="👤",
        layout="wide"
    )
    
    st.title("👤 Email Personas")
    st.markdown("View and manage personas extracted from email senders.")
    
    # API configuration
    api_url = st.sidebar.text_input("API URL", "http://localhost:8000")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Personas"):
        st.rerun()
    
    try:
        # Fetch personas
        response = requests.get(f"{api_url}/personas", timeout=10)
        
        if response.status_code == 200:
            personas = response.json()
            
            if not personas:
                st.info("No personas found. Process some emails first to create personas.")
                return
            
            # Display personas
            for persona in personas:
                with st.expander(f"{persona['first_name']} - {persona['sender']}", expanded=False):
                    display_persona_card(persona)
        
        else:
            st.error(f"Failed to fetch personas: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the backend is running.")
    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main() 