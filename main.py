import streamlit as st
from google.cloud import vision, speech
import io
import google.generativeai as genai
from datetime import datetime

# Initialize GenAI
genai.configure(api_key=st.secrets["API_KEY"])

# Context prompt for the chatbot - moved from system prompt to be included in user messages
CONTEXT_PROMPT = """You are an intelligent lecture assistant that helps students understand and summarize lecture content. Your capabilities include:

1. Summarizing lecture content from audio transcripts and image text
2. Breaking down complex topics into easily digestible points
3. Creating study notes with key concepts and definitions
4. Answering questions about the lecture material
5. Providing examples to illustrate concepts
6. Highlighting important terms and their relationships
7. Suggesting potential exam questions based on the content
8. Helping students create study plans based on the material

When summarizing lectures, focus on:
- Main topics and key concepts
- Important definitions and terminology
- Relationships between different concepts
- Real-world applications and examples
- Supporting evidence and examples
- Potential areas for further study

Please maintain an educational and supportive tone, and feel free to ask clarifying questions if needed."""

# Custom CSS for ChatGPT-like interface
def apply_custom_css():
    st.markdown("""
        <style>
        .chat-container {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .user-message {
            background-color: #1a73e8;
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 2rem 1rem 4rem;
        }
        
        .bot-message {
            background-color: #f8f9fa;
            color: #000000;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 4rem 1rem 2rem;
            border: 1px solid #e0e0e0;
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .stTextInput>div>div>input {
            border-radius: 1.5rem;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'audio_transcript' not in st.session_state:
        st.session_state.audio_transcript = ""
    if 'document_text' not in st.session_state:
        st.session_state.document_text = ""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""

# Audio transcription function
def transcribe_audio(audio_file):
    client = speech.SpeechClient()
    content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )
    
    with st.spinner("Transcribing audio..."):
        response = client.recognize(config=config, audio=audio)
        
    transcript = " ".join(result.alternatives[0].transcript for result in response.results)
    return transcript

# Document text detection function
def detect_document(image_file):
    client = vision.ImageAnnotatorClient()
    content = image_file.read()
    image = vision.Image(content=content)
    
    with st.spinner("Extracting text from image..."):
        response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(response.error.message)
    
    return response.full_text_annotation.text

# Modified chatbot response function to work with Gemini's format
def get_chatbot_response(conversation_history, user_input):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Initialize chat with just the context prompt
    chat = model.start_chat(history=[])
    
    # Add context about available lecture materials
    context = CONTEXT_PROMPT + "\n\n"
    if st.session_state.audio_transcript or st.session_state.document_text:
        context += "Available lecture materials:\n"
        if st.session_state.audio_transcript:
            context += f"- Audio transcript: {st.session_state.audio_transcript}\n"
        if st.session_state.document_text:
            context += f"- Document text: {st.session_state.document_text}\n"
    
    # Add conversation history as alternating user/model messages
    for msg in conversation_history:
        chat.send_message(msg["content"])
    
    # Enhance user input with context
    enhanced_input = f"""{context}

Based on the lecture materials provided, please address the following: {user_input}

Remember to:
1. Reference specific parts of the lecture when relevant
2. Provide clear explanations with examples
3. Highlight key terms and concepts
4. Make connections between different parts of the material
5. Suggest related topics for further study if appropriate"""
    
    # Get response
    response = chat.send_message(enhanced_input)
    return response.text

def process_initial_summary(audio_transcript="", document_text=""):
    """Generate initial summary with enhanced context"""
    summary_prompt = f"""{CONTEXT_PROMPT}

Please provide a comprehensive summary of the following lecture materials:

Audio Transcript:
{audio_transcript}

Document Text:
{document_text}

Please structure the summary as follows:
1. Main Topics Covered
2. Key Concepts and Definitions
3. Important Relationships and Connections
4. Real-world Applications
5. Key Takeaways
6. Suggested Study Points

Focus on creating a clear, organized summary that will help students understand and review the material effectively."""

    return get_chatbot_response([], summary_prompt)

# Handle message submission
def handle_submit():
    if st.session_state.user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "content": st.session_state.user_input,
            "is_user": True,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        try:
            # Get bot response
            bot_response = get_chatbot_response(
                st.session_state.messages, 
                st.session_state.user_input
            )
            
            # Add bot response
            st.session_state.messages.append({
                "content": bot_response,
                "is_user": False,
                "timestamp": datetime.now().strftime("%H:%M")
            })
        
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
        
        # Clear input
        st.session_state.user_input = ""

# Display chat messages
def display_chat_messages():
    for message in st.session_state.messages:
        if message["is_user"]:
            st.markdown(f'<div class="user-message">{message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', 
                       unsafe_allow_html=True)

# Main app function
def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # App header
    st.title("📚 Lecture Notes Generator")

    # Add introduction
    if not st.session_state.messages:
        st.markdown("""
        Welcome to the Lecture Notes Generator! 👋
        
        I'm your AI lecture assistant, ready to help you:
        - 📝 Summarize lecture content
        - 🔍 Extract key concepts
        - ❓ Answer questions about the material
        - 📚 Create study notes
        - 🎯 Identify important topics
        
        To get started:
        1. Upload your lecture audio and/or images
        2. Click "Process Uploads" to analyze the content
        3. Ask questions about the lecture material
        """)
    
    # Sidebar for file uploads
    with st.sidebar:
        st.header("Upload Files")
        
        # Audio upload
        audio_file = st.file_uploader("Upload Lecture Audio (MP3)", 
                                    type=["mp3"],
                                    key="audio_upload")
        
        # Image upload
        image_file = st.file_uploader("Upload Lecture Notes Image", 
                                    type=["jpg", "jpeg", "png"],
                                    key="image_upload")
        
        # Process uploads button
        if st.button("Process Uploads"):
            st.session_state.processing = True
            
            try:
                # Process audio if uploaded
                if audio_file:
                    st.session_state.audio_transcript = transcribe_audio(audio_file)
                    st.session_state.messages.append({
                        "content": "Audio transcription completed!",
                        "is_user": False,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                
                # Process image if uploaded
                if image_file:
                    st.session_state.document_text = detect_document(image_file)
                    st.session_state.messages.append({
                        "content": "Image text extraction completed!",
                        "is_user": False,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                
                # Generate initial summary
                if st.session_state.audio_transcript or st.session_state.document_text:
                    combined_text = (f"Audio transcript: {st.session_state.audio_transcript}\n"
                                   f"Image text: {st.session_state.document_text}")
                    
                    initial_summary = get_chatbot_response([], 
                        f"Please summarize this lecture material: {combined_text}")
                    
                    st.session_state.messages.append({
                        "content": initial_summary,
                        "is_user": False,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
            
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
            
            finally:
                st.session_state.processing = False
    
    # Main chat interface
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        display_chat_messages()
    
    # Chat input
    st.text_input(
        "Ask a question about the lecture",
        key="user_input",
        on_change=handle_submit
    )

if __name__ == "__main__":
    main()