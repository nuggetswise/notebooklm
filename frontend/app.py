import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import os

# Page configuration
st.set_page_config(
    page_title="Email RAG Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .email-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .document-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metadata-item {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.25rem;
    }
    .score-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
    }
    .email-source-card {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    .email-source-card:hover {
        border-color: #007bff;
        box-shadow: 0 2px 8px rgba(0,123,255,0.1);
    }
    .email-source-card.selected {
        border-color: #007bff;
        background-color: #f8f9ff;
    }
    .persona-badge {
        background-color: #6f42c1;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .top-bar {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

@st.cache_data
def get_available_labels():
    """Get available email labels from the API - filtered to substack.com only"""
    try:
        response = requests.get(f"{API_BASE_URL}/labels")
        if response.status_code == 200:
            labels = response.json()["labels"]
            # Filter to only show substack.com
            return [label for label in labels if label == "substack.com"]
        return ["substack.com"]  # Fallback
    except Exception as e:
        st.error(f"Error fetching labels: {e}")
        return ["substack.com"]  # Fallback

@st.cache_data
def get_emails_by_label(label: str, days_back: int = 30):
    """Get emails by label and date range"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        response = requests.get(
            f"{API_BASE_URL}/emails",
            params={"label": label, "since": cutoff_date}
        )
        if response.status_code == 200:
            return response.json()["emails"]
        return []
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        return []

def query_rag(question: str, label: str = None, days_back: int = 30, sender_filter: str = None):
    """Query the RAG system"""
    try:
        # Ensure label is a string or None
        if isinstance(label, list):
            label = label[0] if label else None
        if label == "All":
            label = None
        
        # For substack.com only, always use substack.com label
        if label is None or label == "substack.com":
            label = "substack.com"
        
        payload = {
            "question": question,
            "label": label,
            "days_back": days_back
        }
        
        # Add sender filter if specified
        if sender_filter:
            payload["sender"] = sender_filter
        
        response = requests.post(f"{API_BASE_URL}/query", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error querying RAG: {response.text}\nPayload: {payload}")
            return None
    except Exception as e:
        st.error(f"Error querying RAG: {e}")
        return None

def display_document_card(doc: Dict[str, Any]):
    """Display a document card with metadata"""
    with st.container():
        st.markdown(f"""
        <div class="document-card">
            <h4>📄 {doc.get('subject', 'No Subject')}</h4>
            <div class="metadata-item">📧 From: {doc.get('from', 'Unknown')}</div>
            <div class="metadata-item">📅 Date: {doc.get('date', 'Unknown')}</div>
            <div class="metadata-item">🏷️ Label: {doc.get('label', 'Unknown')}</div>
            <div class="metadata-item">📊 Score: <span class="score-badge">{doc.get('score', 0):.3f}</span></div>
            <hr>
            <p><strong>Content:</strong></p>
            <p>{doc.get('content', 'No content available')[:500]}{'...' if len(doc.get('content', '')) > 500 else ''}</p>
        </div>
        """, unsafe_allow_html=True)

def display_email_source_card(label: str, email_count: int, is_selected: bool = False):
    """Display an email source card"""
    selected_class = "selected" if is_selected else ""
    
    # Create a clickable card using st.button
    if st.button(
        f"📧 {label} ({email_count} emails)",
        key=f"source_{label}",
        help=f"Click to select {label} emails",
        use_container_width=True
    ):
        st.session_state.selected_label = label
        st.rerun()
    
    # Add visual styling for selected state
    if is_selected:
        st.markdown("""
        <style>
        [data-testid="stButton"] button[kind="secondary"] {
            background-color: #f8f9ff !important;
            border-color: #007bff !important;
            color: #007bff !important;
        }
        </style>
        """, unsafe_allow_html=True)

def extract_first_name(sender: str) -> str:
    """Extract first name from sender email or display name."""
    try:
        # Handle "Display Name <email@domain.com>" format
        if '<' in sender and '>' in sender:
            display_name = sender.split('<')[0].strip()
            # Extract first name from display name
            if display_name:
                first_name = display_name.split()[0]
                return first_name.title()
        
        # Handle "email@domain.com" format
        if '@' in sender:
            email_part = sender.split('@')[0]
            # Remove common prefixes and get first name
            email_part = email_part.replace('+', '.').split('.')[0]
            return email_part.title()
        
        return "Unknown"
    except:
        return "Unknown"

def get_sender_first_names(label: str, days_back: int = 30) -> List[str]:
    """Get unique first names of senders for a given label."""
    try:
        emails = get_emails_by_label(label, days_back)
        first_names = []
        for email in emails:
            sender = email.get('sender', '')
            first_name = extract_first_name(sender)
            if first_name not in first_names and first_name != "Unknown":
                first_names.append(first_name)
        return sorted(first_names)
    except Exception as e:
        return []

def main():
    # Initialize selected label if not set
    if 'selected_label' not in st.session_state:
        st.session_state.selected_label = 'All'
    
    # Initialize selected sender if not set
    if 'selected_sender' not in st.session_state:
        st.session_state.selected_sender = None
    
    # Top bar with workspace info and controls
    st.markdown("""
    <div class="top-bar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="main-header" style="margin: 0; font-size: 2rem;">📧 Email RAG Assistant</h1>
                <p style="margin: 0; color: #6c757d;">Chat with your emails using AI</p>
            </div>
            <div style="text-align: right;">
                <button style="background: #007bff; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.25rem; margin-left: 0.5rem;">⚙️ Settings</button>
                <button style="background: #28a745; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.25rem; margin-left: 0.5rem;">📧 Add Email</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout - Email sources on left, Chat on right
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h2 class="email-header">📁 Sender Domains</h2>', unsafe_allow_html=True)
        
        # Get available labels (now sender domains)
        labels = get_available_labels()
        
        # Display sender domains
        for label in labels:
            # Get email count for this domain
            emails = get_emails_by_label(label, 30)
            email_count = len(emails)
            
            # Check if this domain is currently selected
            is_selected = st.session_state.selected_label == label
            
            display_email_source_card(label, email_count, is_selected)
            
            # Show sender first names for substack.com
            if label == "substack.com":
                first_names = get_sender_first_names(label, 30)
                if first_names:
                    st.markdown("**📝 Senders:**")
                    
                    # Show "All Senders" option
                    if st.button("👥 All Senders", key="all_senders", use_container_width=True):
                        st.session_state.selected_sender = None
                        st.rerun()
                    
                    # Show individual sender buttons
                    for name in first_names[:10]:  # Show first 10 names
                        is_selected = st.session_state.selected_sender == name
                        button_text = f"👤 {name}"
                        if is_selected:
                            button_text = f"✅ {name}"
                        
                        if st.button(button_text, key=f"sender_{name}", use_container_width=True):
                            st.session_state.selected_sender = name
                            st.rerun()
                    
                    if len(first_names) > 10:
                        st.markdown(f"<div style='font-size: 0.8rem; color: #999; text-align: center;'>+{len(first_names) - 10} more senders</div>", unsafe_allow_html=True)
                    
                    # Clear filter button
                    if st.session_state.selected_sender:
                        if st.button("🗑️ Clear Filter", key="clear_sender_filter", use_container_width=True):
                            st.session_state.selected_sender = None
                            st.rerun()
                    
                    st.divider()
        
        # Quick filters
        st.subheader("🔍 Quick Filters")
        days_back = st.slider(
            "Days Back",
            min_value=1,
            max_value=365,
            value=30,
            help="Filter emails from the last N days"
        )
        
        # System status
        st.subheader("📊 System Status")
        try:
            status_response = requests.get(f"{API_BASE_URL}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                st.success("✅ Connected")
                # Only show substack.com metrics
                substack_emails = len([e for e in status.get("emails", []) if e.get("label") == "substack.com"])
                st.metric("Substack Emails", substack_emails)
                st.metric("Sender Domain", "substack.com")
            else:
                st.error("❌ Connection Failed")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    with col2:
        st.markdown('<h2 class="email-header">💬 Chat with Your Emails</h2>', unsafe_allow_html=True)
        
        # Show selected email source
        if st.session_state.selected_sender:
            st.info(f"📧 Chatting with emails from: **substack.com** → **{st.session_state.selected_sender}**")
        else:
            st.info(f"📧 Chatting with emails from: **substack.com**")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.container():
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        with st.container():
            question = st.text_area(
                "Ask a question about your emails:",
                placeholder="e.g., What emails did I receive about project updates? or Hey Nate, tell me about AI",
                height=100
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🚀 Send Query", type="primary"):
                    if question.strip():
                        # Add user message to chat
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        # Query RAG system
                        with st.spinner("Searching emails..."):
                            result = query_rag(
                                question, 
                                st.session_state.selected_label if st.session_state.selected_label != 'All' else None,
                                days_back,
                                st.session_state.selected_sender
                            )
                        
                        if result:
                            # Add assistant response to chat
                            response_text = result.get("answer", "No answer available")
                            st.session_state.messages.append({"role": "assistant", "content": response_text})
                            
                            # Store results for display
                            st.session_state.last_results = result
                            
                            # Rerun to update display
                            st.rerun()
                        else:
                            st.error("Failed to get response from RAG system")
            
            with col2:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.messages = []
                    if "last_results" in st.session_state:
                        del st.session_state.last_results
                    st.rerun()
            
            with col3:
                if st.button("📊 Show Sources"):
                    if "last_results" in st.session_state and st.session_state.last_results:
                        results = st.session_state.last_results
                        metadata = results.get("metadata", [])
                        
                        if metadata:
                            st.success(f"Found {len(metadata)} relevant emails")
                            
                            for i, doc in enumerate(metadata):
                                with st.expander(f"Email {i+1}: {doc.get('subject', 'No Subject')}"):
                                    display_document_card(doc)
                        else:
                            st.info("No source emails found")
                    else:
                        st.info("Ask a question first to see source emails")

if __name__ == "__main__":
    main() 