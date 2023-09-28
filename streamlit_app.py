# Importing Libraries
import streamlit as st
import google.generativeai as palm
from google.api_core import client_options as client_options_lib

st.set_page_config(page_title="LLM Pair Programming") 
st.sidebar.title('Pair Programming using LLM')

# App title
user_api_key = st.sidebar.text_input(
    label="#### Your PaLM API key 👇",
    placeholder="Paste your PaLM API key",
    type="password")

palm.configure(api_key=user_api_key, transport="rest")

st.sidebar.subheader('Created by: **_Sarang Bagul_**')

st.header('Welcome to LLM Pair Programming :desktop_computer:')
# st.subheader('Select your coding operation:')

radio = st.radio('Select your coding operation:', ["Generate Code", "Improve existing code", "Simplify Code", "Write Test Cases",
                                             "Debug your Code"])
if user_api_key:
    # Pick the model that generates text
    models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
    model_bison = models[0]
    
    # Helper function to call the PaLM API
    from google.api_core import retry
    @retry.Retry()
    def generate_text(prompt, model=model_bison, temperature=0.0):
        return palm.generate_text(prompt=prompt, model=model, temperature=temperature)
    
    if radio == "Generate Code":
        # Prompt for Scenario 1: Improve existing code
        prompt_template = """
        You are an expert at writing clear, concise, Python code. Write it with list of imported libraries if needed.
    
        {question}
    
        Insert comments for each line of code.
        """
    
    elif radio == "Improve existing code":
        # Prompt for Scenario 1: Improve existing code
        prompt_template = """
        I don't think this code is the best way to do it in Python, can you help me? Write it with list of imported libraries if needed.
    
        {question}
    
        Please explore multiple ways of solving the problem, 
        and tell me which is the most Pythonic
        """
    
    elif radio == "Simplify Code":
        # Prompt for Scenario 2: Simplify code
        prompt_template = """
        Can you please simplify this code in Python? \n
        You are an expert in Pythonic code. 
    
        {question}
    
        Please comment each line in detail, \n
        and explain in detail what you did to modify it, and why.
        """
    
    elif radio == "Write Test Cases":
        # Prompt for Scenario 3: Write test cases
        prompt_template = """
        Can you please create test cases in code for this Python code? Write it with list of imported libraries if needed.
    
        {question}
    
        Explain in detail what these test cases are designed to achieve.
        """
    
    # elif radio == "Make Code More efficient":
    #     # Prompt for Scenario 4: Make code more efficient
    #     prompt_template = """
    #     Can you please make this code more efficient?
    
    #     {question}
    
    #     Explain in detail what you changed and why.
    #     """
    
    else:
        # Prompt for Scenario 5: Debug your code
        prompt_template = """
        Can you please help me to debug this code? Write it with list of imported libraries if needed.
    
        {question}
    
        Explain in detail what you found and why it was a bug in pythonic way.
        """
    
    question = """ """
    txt = st.text_area("Paste your code:", question, height=200)
    
    # Complete Answer
    completion = generate_text(
        prompt = prompt_template.format(question=txt)
    )
    
    if st.button("Result"):
        st.write(completion.result)
