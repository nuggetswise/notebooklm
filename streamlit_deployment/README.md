
# Email RAG Assistant - Streamlit Deployment

This is a standalone Streamlit app for the Email RAG Assistant.

## Setup

1. Upload this directory to Streamlit Cloud
2. Set the following environment variables in Streamlit Cloud:
   - `COHERE_API_KEY`: Your Cohere API key
   - `GMAIL_EMAIL`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: Your Gmail app password

## Features

- Email RAG system focused on substack.com emails
- Sender-based filtering
- Persona-aware responses
- Multi-pane notebook-style interface

## Data

The app uses a SQLite database stored in the `data/` directory.
