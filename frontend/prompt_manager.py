#!/usr/bin/env python3
"""
Prompt Manager - Streamlit component for managing centralized prompts.
"""

import streamlit as st
import requests
import json
from typing import Dict, Any

def main():
    st.set_page_config(
        page_title="Prompt Manager",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Centralized Prompt Manager")
    st.markdown("Manage and test all prompts used in the email RAG system.")
    
    # API configuration
    api_url = st.sidebar.text_input("API URL", "http://localhost:8000")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Prompts"):
        st.rerun()
    
    try:
        # Fetch all prompts
        response = requests.get(f"{api_url}/prompts", timeout=10)
        
        if response.status_code == 200:
            prompts = response.json()
            
            if not prompts:
                st.info("No prompts found.")
                return
            
            # Display prompts in tabs
            tab1, tab2, tab3 = st.tabs(["📋 All Prompts", "✏️ Edit Prompts", "🧪 Test Prompts"])
            
            with tab1:
                st.markdown("### Available Prompts")
                
                for prompt_type, prompt_info in prompts.items():
                    with st.expander(f"{prompt_info['name']} ({prompt_type})", expanded=False):
                        st.markdown(f"**Description:** {prompt_info['description']}")
                        st.markdown(f"**Version:** {prompt_info['version']}")
                        st.markdown(f"**Variables:** {', '.join(prompt_info['variables'])}")
                        
                        st.markdown("**Template:**")
                        st.code(prompt_info['template'], language="text")
            
            with tab2:
                st.markdown("### Edit Prompt Templates")
                
                # Select prompt to edit
                prompt_types = list(prompts.keys())
                selected_prompt = st.selectbox("Select prompt to edit:", prompt_types)
                
                if selected_prompt:
                    prompt_info = prompts[selected_prompt]
                    
                    st.markdown(f"**Editing:** {prompt_info['name']}")
                    
                    # Edit form
                    with st.form(f"edit_{selected_prompt}"):
                        new_template = st.text_area(
                            "Template:",
                            value=prompt_info['template'],
                            height=200,
                            help="Use {variable_name} for placeholders"
                        )
                        
                        new_description = st.text_input(
                            "Description:",
                            value=prompt_info['description']
                        )
                        
                        new_version = st.text_input(
                            "Version:",
                            value=prompt_info['version']
                        )
                        
                        submitted = st.form_submit_button("Update Prompt")
                        
                        if submitted:
                            try:
                                update_response = requests.post(
                                    f"{api_url}/prompts/{selected_prompt}",
                                    json={
                                        'template': new_template,
                                        'description': new_description,
                                        'version': new_version
                                    },
                                    timeout=10
                                )
                                
                                if update_response.status_code == 200:
                                    st.success("✅ Prompt updated successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error updating prompt: {update_response.status_code}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
            
            with tab3:
                st.markdown("### Test Prompt Templates")
                
                # Select prompt to test
                test_prompt_type = st.selectbox("Select prompt to test:", prompt_types, key="test_select")
                
                if test_prompt_type:
                    prompt_info = prompts[test_prompt_type]
                    st.markdown(f"**Testing:** {prompt_info['name']}")
                    
                    # Dynamic form for variables
                    st.markdown("**Provide test values for variables:**")
                    
                    test_vars = {}
                    for var in prompt_info['variables']:
                        if var == 'question':
                            test_vars[var] = st.text_input(f"{var}:", value="What is this email about?", key=f"test_{var}")
                        elif var == 'context_text':
                            test_vars[var] = st.text_area(f"{var}:", value="This is a test email about AI and technology.", key=f"test_{var}")
                        elif var == 'persona_context':
                            test_vars[var] = st.text_area(f"{var}:", value="This email is from Nate. They typically write about AI and Tech.", key=f"test_{var}")
                        elif var == 'subject':
                            test_vars[var] = st.text_input(f"{var}:", value="AI Technology Update", key=f"test_{var}")
                        elif var == 'content':
                            test_vars[var] = st.text_area(f"{var}:", value="Latest developments in artificial intelligence and machine learning.", key=f"test_{var}")
                        elif var == 'sender':
                            test_vars[var] = st.text_input(f"{var}:", value="nate@example.com", key=f"test_{var}")
                        elif var == 'date':
                            test_vars[var] = st.text_input(f"{var}:", value="2025-06-25", key=f"test_{var}")
                        elif var == 'context_summary':
                            test_vars[var] = st.text_area(f"{var}:", value="Relevant emails found about AI and technology.", key=f"test_{var}")
                        elif var in ['first_name', 'email_count_text', 'topics_text', 'labels_text']:
                            if var == 'first_name':
                                test_vars[var] = st.text_input(f"{var}:", value="Nate", key=f"test_{var}")
                            elif var == 'email_count_text':
                                test_vars[var] = st.text_input(f"{var}:", value="They have sent 5 emails before.", key=f"test_{var}")
                            elif var == 'topics_text':
                                test_vars[var] = st.text_input(f"{var}:", value="They typically write about: AI, Tech, Business.", key=f"test_{var}")
                            elif var == 'labels_text':
                                test_vars[var] = st.text_input(f"{var}:", value="Common labels: Newsletter, AI.", key=f"test_{var}")
                        else:
                            test_vars[var] = st.text_input(f"{var}:", key=f"test_{var}")
                    
                    # Test button
                    if st.button("🧪 Test Prompt"):
                        try:
                            # Build query parameters
                            params = {k: v for k, v in test_vars.items() if v}
                            
                            test_response = requests.get(
                                f"{api_url}/prompts/test/{test_prompt_type}",
                                params=params,
                                timeout=10
                            )
                            
                            if test_response.status_code == 200:
                                result = test_response.json()
                                
                                st.success("✅ Prompt test successful!")
                                
                                st.markdown("**Formatted Prompt:**")
                                st.code(result['formatted_prompt'], language="text")
                                
                                st.markdown("**Variables Used:**")
                                st.json(result['variables_used'])
                                
                            else:
                                st.error(f"❌ Error testing prompt: {test_response.status_code}")
                                st.text(test_response.text)
                                
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        
        else:
            st.error(f"Failed to fetch prompts: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the backend is running.")
    except Exception as e:
        st.error(f"Error: {e}")
    
    # System information
    with st.sidebar:
        st.markdown("### System Info")
        st.markdown("**Prompt Types:**")
        st.markdown("""
        - `rag_query` - Basic RAG queries
        - `rag_query_with_persona` - RAG with sender context
        - `persona_context` - Persona information
        - `fallback_response` - Fallback responses
        - `email_summary` - Email summaries
        - `topic_extraction` - Topic detection
        - `sentiment_analysis` - Sentiment analysis
        """)
        
        st.markdown("### Usage")
        st.markdown("""
        1. **View** all prompts in the first tab
        2. **Edit** prompts in the second tab
        3. **Test** prompts with sample data
        4. Changes are applied immediately
        """)

if __name__ == "__main__":
    main() 