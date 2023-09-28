import streamlit as st
from streamlit_chat import message

repo_id = "google/flan-t5-xxl"

st.set_page_config(page_title="LLM Pair Programming") 

st.sidebar.title('Welcome to LLM Pair Programming 🤗')

# App title
user_api_key = st.sidebar.text_input(
    label="#### Your PaLM API key 👇",
    placeholder="Paste your PaLM API key",
    type="password")


# selectbox = st.sidebar.selectbox("Select file type",("PDF", "CSV"))

# if selectbox == "PDF":
#     uploaded_file = st.sidebar.file_uploader("upload", type="pdf")
# else:
#     uploaded_file = st.sidebar.file_uploader("upload", type="csv")

uploaded_file = st.sidebar.file_uploader("upload", type="pdf")

# st.sidebar.caption('**Creared by: Sarang Bagul**')
# st.sidebar.subheader('_Streamlit_ is :blue[cool] :sunglasses:')
st.sidebar.subheader('Created by: **_Sarang Bagul_**')


if uploaded_file :
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
        
    # if selectbox == "PDF":
    #     loader = PyPDFLoader(file_path=tmp_file_path)
    # else:
    #     loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")

    loader = PyPDFLoader(file_path=tmp_file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=user_api_key )
    
    try:
        vectors = Chroma.from_documents(documents=docs, embedding=embeddings)
    except InvalidDimensionException:
        Chroma().delete_collection()
        vectors = Chroma.from_documents(documents=docs, embedding=embeddings)
    
    retriever = vectors.as_retriever()
    
    llm = HuggingFaceHub(huggingfacehub_api_token=user_api_key, repo_id=repo_id, model_kwargs={"temperature": 0.1})
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(llm = llm, retriever=retriever, memory=memory)
    
    
    def conversational_chat(query):
        
        result = chain({"question": query})#, "chat_history": st.session_state['history']})
#         st.session_state['history'].append((query, result["answer"]))
        
        return result["answer"]
    
#     if 'history' not in st.session_state:
#         st.session_state['history'] = []

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Welcome to LLM Q&A bot Assistant 🤗. How can I help you ?"}]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    # User-provided prompt
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = conversational_chat(prompt) 
                st.write(response) 
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message) 
