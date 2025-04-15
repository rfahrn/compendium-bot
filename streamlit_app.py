# Add custom CSS with dark mode support
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .subheader {
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Light mode styles */
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
        color: #262730;
    }
    .result-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    
    /* Dark mode styles */
    .stApp.dark .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
    }
    .stApp.dark .result-box {
        background-color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)
