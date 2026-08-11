import streamlit as st
import requests
import os
from datetime import datetime
import json
import base64

# Page configuration
st.set_page_config(page_title="RAG Chatbot", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []
if "selected_document" not in st.session_state:
    st.session_state.selected_document = None
if "waiting" not in st.session_state:
    st.session_state.waiting = False
if "pending_q" not in st.session_state:
    st.session_state.pending_q = None
if st.session_state.uploaded_documents:
    st.session_state.document_uploaded = True

# Sidebar
st.sidebar.title("🤖 RAG Chatbot")

# Navigation in sidebar
st.sidebar.write("---")
if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.page = "home"

if st.session_state.document_uploaded or st.session_state.uploaded_documents:
    if st.sidebar.button("💬 Chat", use_container_width=True):
        st.session_state.page = "chat"
    if st.sidebar.button("🗃 Documents", use_container_width=True):
        st.session_state.page = "uploaded_documents"
    if st.sidebar.button("📜 History", use_container_width=True):
        st.session_state.page = "history"
    

# New Chat button
st.sidebar.write("---")
if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.current_chat = []
    st.session_state.page = "chat"

# Display current user
if st.session_state.user_name:
    st.sidebar.write(f"**User:** {st.session_state.user_name}")

st.sidebar.write("---")
st.markdown(
        """
        <style>
            [data-testid="stTextInputRootElement"]:focus-within{
                border-color: white !important;
            }
            [data-testid="stBaseButton-secondary"]{
            background:#8700B8;
            color: white }

            .chat-container {display: flex; flex-direction: column; gap: 10px;}
            .chat-bubble {padding: 14px 18px; border-radius: 18px; max-width: 50%; width: fit-content; line-height: 1.4;color: white}
            .user-bubble {background: #6303C9; margin-left: auto; text-align: right;}
            .bot-bubble {background: #8700B8; margin-right: auto; text-align: left;}
            .chat-timestamp {font-size: 0.75rem; color: white; margin-top: 4px;}

            [data-testid="stSelectbox"]>div:first-child: focus-within{
                    border-color:#8700B8 !important}

            [data-testid="stChatInput"]>div:focus-within {
                border-color: white !important ;
            }
            [data-testid="stChatInput"]>div:focus-within [data-testid="stChatInputSubmitButton"]{
                background-color: #8700B8 !important;} 
            [data-testid="stChatInput"]>div:focus-within [data-testid="stChatInputSubmitButton"] svg{
                    fill: #FFFFFF !important; 
                }
            [data-testid="stChatInputStopButton"]{
                background-color: #8700B8 !important;} 

            .dots span{
                animation: blink 1.4s infinite;
                display: inline-block;
            }
            .dots span:nth-child(2){
                animation-delay: 0.2s;
            }
            .dots span:nth-child(3){
                animation-delay: 0.4s;
            } 

            @keyframes blink{
                0% ,80% , 100%{
                    opacity: 0.2;}
                40%{
                    opacity: 1}
            }    

        </style>
        """, unsafe_allow_html=True
    )

# PAGE 1: HOME PAGE
if st.session_state.page == "home":
    st.title("🤖 RAG Chatbot")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("## Welcome to RAG Chatbot!")
        st.write("""
        This is an intelligent chatbot powered by Retrieval-Augmented Generation (RAG).
        
        **Features:**
        - 📄 Upload and view your documents
        - 💬 Chat with AI about your documents
        - 📜 View complete chat history
        - 🔄 Start new conversations anytime
        """)
    
    with col2:
        st.write("## Get Started")
        
        # User Name Input
        user_name = st.text_input("Enter your name:", value=st.session_state.user_name)
        if user_name:
            st.session_state.user_name = user_name
        
        # Document Upload
        st.write("### Upload Document")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
        status = st.empty()
        if uploaded_file is not None:
            existing_names = [doc["name"] for doc in st.session_state.uploaded_documents]
            if uploaded_file.name not in existing_names:
                status.info("📤 Uploading document...")

                try:
                    upload_f = uploaded_file.getvalue()
                    upload_url = "https://liekdagux0.execute-api.ap-southeast-2.amazonaws.com/data" # need to change
                    headers = {"filename": os.path.basename(uploaded_file.name)}
                    files = {"file": (uploaded_file.name, upload_f, uploaded_file.type)}
                    response = requests.post(upload_url, files=files, headers=headers)

                    if response.status_code == 200:
                        st.session_state.document_uploaded = True
                        st.session_state.document_id = uploaded_file.name
                        st.session_state.uploaded_documents.append({
                            "name": uploaded_file.name,
                            "uploaded_at": datetime.now(),
                            "file": upload_f
                        })
                        if not st.session_state.selected_document:
                            st.session_state.selected_document = uploaded_file.name
                        st.session_state.chat_history.append({
                            "timestamp": datetime.now(),
                            "chat": []
                        })
                        status.empty()
                        status.success(f"✅ Document '{uploaded_file.name}' uploaded successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ Error uploading document: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Error uploading document: {str(e)}")
            else:
                status.info(f"📄 Document '{uploaded_file.name}' is already uploaded.")

        if st.session_state.uploaded_documents:
            st.write("### Uploaded Documents")
            for doc in st.session_state.uploaded_documents:
                st.write(f"- {doc['name']}")

        if st.session_state.uploaded_documents:
            if st.button("Start Chatting"):
                st.session_state.page = "chat"
                st.rerun()

            if st.button("View Documents"):
                st.session_state.page = "uploaded_documents"
                st.rerun()

# PAGE 2: CHAT PAGE
elif st.session_state.page == "chat":

    if not st.session_state.uploaded_documents:
        st.error("Please upload a document first!")
        if st.button("Go to Home"):
            st.session_state.page = "home"
            st.rerun()
    else:
        st.title("💬 Chat with Your Document")
        
        if st.session_state.user_name:
            st.write(f"**Chatting as:** {st.session_state.user_name}")

        doc_names = [doc["name"] for doc in st.session_state.uploaded_documents]
        previous_selection = st.session_state.selected_document or doc_names[0]
        if previous_selection not in doc_names:
            previous_selection = doc_names[0]
        selected_document = st.selectbox("Select document to chat with:", doc_names, index=doc_names.index(previous_selection))
        if selected_document != st.session_state.selected_document:
            st.session_state.current_chat = []
            st.session_state.waiting = False
        st.session_state.selected_document = selected_document
        st.session_state.document_id = selected_document
        st.write(f"**Selected document:** {selected_document}")

        # Chat display area
        st.write("---")

        # Display current chat in conversation format
        if st.session_state.current_chat:
            st.write("### Conversation")
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for exchange in st.session_state.current_chat:
                if exchange["role"] == "user":
                    st.markdown(
                        f'<div class="chat-bubble user-bubble">{exchange["content"]}'
                        f'<div class="chat-timestamp">You • {exchange["timestamp"].strftime("%H:%M:%S")}</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                elif exchange["role"] == "assistant":
                    st.markdown(
                        f'<div class="chat-bubble bot-bubble">{exchange["content"]}'
                        f'<div class="chat-timestamp">Bot • {exchange["timestamp"].strftime("%H:%M:%S")}</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
            loading_block = st.empty()
        else:
            st.info("Start a conversation by asking a question below!")
        
        # Input area
        st.write("---")
        st.write("### Ask a Question")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.chat_input("Enter your question:", key="question_input", submit_mode="stop" ,accept_audio=True)
                    
        with col2:
            end_chat_button = st.button("End Chat", use_container_width=True)
        
        if end_chat_button:
            st.session_state.page = "home"
            st.session_state.current_chat = []
            st.rerun()
        
        if user_question:
            # Add user message to chat
            st.session_state.current_chat.append({
                "role": "user",
                "content": user_question.text,
                "timestamp": datetime.now()
            })
            st.session_state.pending_q = user_question.text
            st.session_state.waiting = True
            st.rerun()            

        if st.session_state.waiting :
            loading_block.markdown(
                """
                <div class = "chat-bubble bot-bubble">
                    <span class="dots">
                        <span>.</span><span>.</span><span>.</span>
                    </span>
                </div>
                """, unsafe_allow_html=True,
            )
            
            try:
                chat_url = "https://gs5tzxijk3.execute-api.ap-southeast-2.amazonaws.com/chat" #chat api
                history = [[msg["role"], msg["content"]] for msg in st.session_state.current_chat if msg["role"] in ("user", "assistant")]
                payload = {
                    "question": st.session_state.pending_q,
                    "history": history,
                    "filename": os.path.basename(st.session_state.selected_document or st.session_state.document_id)
                }
                response = requests.post(chat_url, json=payload)
                response.raise_for_status()
                try:
                    bot_response = response.json().get("answer", response.text)
                except ValueError:
                    bot_response = response.text

                loading_block.empty()

                st.session_state.current_chat.append({
                    "role": "assistant",
                    "content": bot_response,
                    "timestamp": datetime.now()
                })
                    
                if st.session_state.chat_history:
                    st.session_state.chat_history[-1]["chat"] = st.session_state.current_chat
                    
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error getting response: {str(e)}")
            finally:
                st.session_state.waiting = False
                st.rerun()

#New Page
elif st.session_state.page == "uploaded_documents":
    st.title("📄 Uploaded Documents")
    
    if not st.session_state.uploaded_documents:
        st.info("No documents uploaded yet. Please upload a document first!")
    else:
        for idx, doc in enumerate(st.session_state.uploaded_documents):
            with st.expander(f"Document {idx + 1} - {doc['name']} (Uploaded at: {doc['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')})"):
                st.write(f"**Document Name:** {doc['name']}")
                pdf_base64 = base64.b64encode(doc["file"]).decode("utf-8")
                pdf_display = f"""
                <iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600px" type="application/pdf">
                </iframe>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)

                if st.button(f"Select '{doc['name']}' for Chatting", key=f"select_doc_{idx}"):
                    st.session_state.selected_document = doc["name"]
                    st.session_state.document_id = doc["name"]
                    st.session_state.current_chat = []
                    st.session_state.page = "chat"
                    st.rerun()

# PAGE 3: CHAT HISTORY PAGE
elif st.session_state.page == "history":
    st.title("📜 Chat History")
    
    if not st.session_state.chat_history:
        st.info("No chat history yet. Start a conversation first!")
    else:
        for idx, session in enumerate(st.session_state.chat_history):
            with st.expander(f"Chat Session {idx + 1} - {session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
                if session["chat"]:
                    for exchange in session["chat"]:
                        if exchange["role"] == "user":
                            st.write(f"**You ({exchange['timestamp'].strftime('%H:%M:%S')}):**")
                            st.write(exchange["content"])
                            st.write("")
                        else:
                            st.write(f"**Bot ({exchange['timestamp'].strftime('%H:%M:%S')}):**")
                            st.write(exchange["content"])
                            st.write("---")
                else:
                    st.write("*Empty session*")
    
    # Export chat history
    if st.session_state.chat_history:
        st.write("---")
        if st.button("📥 Download Chat History as JSON"):
            history_json = json.dumps(
                [{
                    "timestamp": session["timestamp"].isoformat(),
                    "chat": session["chat"]
                } for session in st.session_state.chat_history],
                indent=2,
                default=str
            )
            st.download_button(
                label="Download History",
                data=history_json,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
