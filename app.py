import streamlit as st
import os
from document_processor import DocumentProcessor
from ai_assistant import AIAssistant

# Initialize session state
if 'document_text' not in st.session_state:
    st.session_state.document_text = ""
if 'document_summary' not in st.session_state:
    st.session_state.document_summary = ""
if 'document_name' not in st.session_state:
    st.session_state.document_name = ""
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "upload"
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = []
if 'messages' not in st.session_state:
    # This will be deprecated in favor of chat_history
    st.session_state.messages = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

def get_current_chat():
    """Returns the dictionary for the currently active chat."""
    if st.session_state.current_chat_id:
        for chat in st.session_state.chat_history:
            if chat["id"] == st.session_state.current_chat_id:
                return chat
    return None

def start_new_chat():
    """Creates a new chat session and sets it as the current one."""
    new_chat_id = f"chat_{len(st.session_state.chat_history)}"
    st.session_state.chat_history.append({
        "id": new_chat_id,
        "name": f"Chat {len(st.session_state.chat_history) + 1}",
        "messages": [],
        "document_name": None,
        "document_text": None,
    })
    st.session_state.current_chat_id = new_chat_id
    st.rerun()

def reset_document_state():
    """Reset all document-related session state"""
    st.session_state.document_text = ""
    st.session_state.document_summary = ""
    st.session_state.document_name = ""
    st.session_state.current_mode = "upload"
    st.session_state.quiz_questions = []
    st.session_state.quiz_active = False
    st.session_state.current_question_index = 0
    st.session_state.quiz_answers = []
    st.session_state.messages = []

def main():
    st.set_page_config(
        page_title="PDFPaglu",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Override Streamlit default theme variables
    st.markdown(
        """
        <style>
        :root {
            --background-color: #000000;
            --secondary-background-color: #1C1C1E;
            --text-color: #E5E5E7;
            --primary-color: #FFD56B;
        }
        html, body, .main, .block-container, .stApp {
            background-color: #000000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Initialize processors
    doc_processor = DocumentProcessor()
    ai_assistant = AIAssistant()
    
    # Sidebar toggle icon (always visible)
    st.markdown('<div class="sidebar-toggle-container">', unsafe_allow_html=True)
    toggle_label = "☰" if st.session_state.sidebar_collapsed else "✕"
    if st.button(toggle_label, key="sidebar_toggle_btn"):
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply collapsed state via CSS
    if st.session_state.sidebar_collapsed:
        st.markdown("""
            <style>
                [data-testid='stSidebar'] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)

    # Ensure there is at least one chat session
    if not st.session_state.chat_history:
        start_new_chat()

    # Main layout: Sidebar and Chat Area
    with st.sidebar:
        # New chat button
        if st.button("➕ New Chat", use_container_width=True):
            start_new_chat()

        st.markdown("---")
        
        # Chat history via radio buttons
        chat_map = {c.get("name"): c["id"] for c in st.session_state.chat_history}
        chat_names = list(reversed(list(chat_map.keys())))
        
        current_chat = get_current_chat()
        current_chat_name = current_chat.get("name") if current_chat else None
        
        try:
            current_selection_index = chat_names.index(current_chat_name) if current_chat_name else 0
        except ValueError:
            current_selection_index = 0

        selected_chat_name = st.radio(
            "Chat History",
            chat_names,
            index=current_selection_index,
            label_visibility="hidden"
        )
        
        if selected_chat_name:
            selected_chat_id = chat_map[selected_chat_name]
            if st.session_state.current_chat_id != selected_chat_id:
                st.session_state.current_chat_id = selected_chat_id
                st.rerun()

    # Get the current chat object
    current_chat = get_current_chat()

    # Main chat area
    if current_chat:
        if current_chat.get("document_text"):
            mode = current_chat.get("mode")
            if mode == "ask":
                show_qa_mode(ai_assistant, current_chat)
            elif mode == "challenge":
                show_quiz_mode(ai_assistant, current_chat)
            else:
                show_interaction_interface(ai_assistant, current_chat)
        else:
            # If no document is uploaded, show the initial chat screen
            show_initial_view(doc_processor, ai_assistant)

def show_initial_view(doc_processor, ai_assistant):
    """Shows the initial screen with a welcome message and suggestions."""
    st.markdown("""
    <div style="text-align: center; padding-top: 10vh;">
        <h1 style="font-weight: 600;">PDFPaglu</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="suggestion-card">
            <h3>Explain a document</h3>
            <p>Get a quick summary of any uploaded file.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="suggestion-card">
            <h3>Create a quiz</h3>
            <p>Test your knowledge on the document's content.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="suggestion-card">
            <h3>Draft an email</h3>
            <p>Based on the document's key points.</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="suggestion-card">
            <h3>Find key insights</h3>
            <p>Extract the most important information.</p>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("<br><br>", unsafe_allow_html=True)

    show_upload_interface(doc_processor, ai_assistant)

def show_upload_interface(doc_processor, ai_assistant):
    """Display the document upload interface integrated into the chat view."""
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "Upload a PDF or TXT file to begin",
            type=['pdf', 'txt'],
            label_visibility="collapsed"
        )

    if uploaded_file is not None:
        with st.spinner("Processing and summarizing document..."):
            try:
                text = doc_processor.extract_text(uploaded_file)

                if text.strip():
                    current_chat = get_current_chat()
                    if current_chat:
                        current_chat["document_text"] = text
                        current_chat["document_name"] = uploaded_file.name
                        current_chat["name"] = uploaded_file.name # Set chat name to doc name
                        
                        summary = ai_assistant.generate_summary(text)
                        
                        current_chat["messages"].append(
                            {"role": "assistant", "content": f"I have finished reading `{uploaded_file.name}`."}
                        )
                        current_chat["messages"].append(
                            {"role": "assistant", "content": f"**Here is a short summary:**\n\n{summary}"}
                        )
                    st.rerun()
                else:
                    st.error("Could not extract text from the document. Please try a different file.")
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")

def show_interaction_interface(ai_assistant, chat_session):
    """Display the main chat interface for interaction."""
    
    # Display messages if not in a specific mode yet
    if "mode" not in chat_session:
        for message in chat_session["messages"]:
            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                st.markdown(message["content"])

    # Mode selection
    st.markdown("""
    <div class="content-card">
        <h2>Choose Your Interaction Mode</h2>
        <p>Select how you'd like to interact with your document.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Ask Anything", use_container_width=True):
            chat_session["mode"] = "ask"
            st.rerun()
            
    with col2:
        if st.button("🧠 Challenge Me", use_container_width=True):
            chat_session["mode"] = "challenge"
            with st.spinner("Generating quiz questions..."):
                quiz_questions = ai_assistant.generate_quiz(chat_session["document_text"])
                if quiz_questions:
                    chat_session["quiz_questions"] = quiz_questions
                    chat_session["current_question_index"] = 0
                    chat_session["quiz_answers"] = []
                else:
                    st.error("I was unable to generate a quiz for this document. Please try a different document or ask questions in 'Ask Anything' mode.")
                    chat_session["mode"] = None # Reset mode
            st.rerun()

def show_qa_mode(ai_assistant, chat_session):
    """Handles the 'Ask Anything' mode."""
    st.markdown(f"### 💬 Ask Anything: {chat_session['document_name']}")
    
    # Display existing messages
    for message in chat_session["messages"]:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):
        # Add user message to chat history
        chat_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = ai_assistant.answer_question(
                    chat_session["document_text"], 
                    prompt
                )
                st.markdown(response)
        
        # Add AI response to chat history
        chat_session["messages"].append({"role": "assistant", "content": response})

def show_quiz_mode(ai_assistant, chat_session):
    """Handles the 'Challenge Me' mode."""
    st.markdown(f"### 🧠 Challenge Me: {chat_session['document_name']}")

    quiz_questions = chat_session.get("quiz_questions", [])
    if not quiz_questions:
        st.warning("No quiz questions available. Please try re-entering challenge mode.")
        return

    question_index = chat_session.get("current_question_index", 0)

    if question_index < len(quiz_questions):
        current_q = quiz_questions[question_index]
        
        st.markdown(f"**Question {question_index + 1}/{len(quiz_questions)}:**")
        st.markdown(f"<div class='question-box'>{current_q['question']}</div>", unsafe_allow_html=True)
        
        user_answer = st.text_area("Your answer:", key=f"answer_{question_index}")

        if st.button("Submit Answer", key=f"submit_{question_index}"):
            if user_answer.strip():
                with st.spinner("Evaluating your answer..."):
                    feedback = ai_assistant.evaluate_answer(
                        chat_session["document_text"],
                        current_q['question'],
                        user_answer,
                        current_q['answer']
                    )
                    st.markdown("---")
                    st.markdown(f"**Feedback:**\n\n{feedback}")

                    chat_session["quiz_answers"].append({
                        "question": current_q['question'],
                        "user_answer": user_answer,
                        "feedback": feedback
                    })
                    
                    # Move to the next question
                    chat_session["current_question_index"] += 1
                    st.rerun()
            else:
                st.warning("Please enter your answer before submitting.")

    else:
        st.success("You have completed the challenge! 🎉")
        st.balloons()
        
        st.markdown("### Your Results:")
        for i, answer_data in enumerate(chat_session["quiz_answers"]):
            with st.expander(f"Question {i+1}: {answer_data['question']}"):
                st.write(f"**Your Answer:** {answer_data['user_answer']}")
                st.markdown(f"**Feedback:**\n\n{answer_data['feedback']}")

if __name__ == "__main__":
    main()
