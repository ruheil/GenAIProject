import streamlit as st
from google.cloud import vision, speech
import io
import google.generativeai as genai

# Initialize the Google GenAI model (GenAI)
genai.configure(api_key="AIzaSyDmEojgo55btim7U1XAad5aDcPiiXlJwh0")

# Function to transcribe audio using Google Cloud Speech-to-Text
def transcribe_audio(audio_file):
    client = speech.SpeechClient()

    # Read the audio file uploaded by the user
    content = audio_file.read()

    # Configure audio and recognition settings
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Perform the transcription request
    response = client.recognize(config=config, audio=audio)

    # Extract and return the transcribed text
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript

# Function to detect document text using Google Cloud Vision API
def detect_document(image_file):
    client = vision.ImageAnnotatorClient()

    content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)

    extracted_text = ""
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    extracted_text += word_text + " "

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    return extracted_text

# Function to engage in a conversation with the chatbot
def chatbot_response(conversation_history, task_description, user_input):
    # Initialize the Google GenAI model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Prepare the chat with the task description and user input
    chat = model.start_chat(
        history=[
            {"role": "user", "parts": task_description},
            {"role": "model", "parts": "Sure, I will generate important notes from the provided materials."},
        ]
    )

    # Combine conversation history into the chat
    for history in conversation_history:
        chat.send_message(history['user_input'])  # Add user inputs to the chat history

    # Send the combined text (audio + image transcription) to the chatbot for initial processing
    initial_response = chat.send_message(user_input)

    # Extract initial response text
    initial_notes = initial_response.text

    # Now send the new user input (subsequent conversation)
    subsequent_response = chat.send_message(user_input)

    # Return both the initial notes and subsequent response
    return initial_notes, subsequent_response.text

# Streamlit UI
st.title("Lecture Notes Generator from Audio and Images")

st.write("Upload an audio file (MP3) or an image to help generate lecture notes.")

# File uploader for audio (MP3)
audio_file = st.file_uploader("Upload an MP3 audio file", type=["mp3"])
audio_transcript = ""

# File uploader for image (e.g., handwritten note)
image_file = st.file_uploader("Upload an image file (e.g., handwritten note)", type=["jpg", "png", "jpeg"])
document_text = ""

progress_placeholder = st.empty()
progress_placeholder_2 = st.empty()

# Task description for the chatbot
task_description = (
    "Your task is to summarize lectures to lecture notes. You are provided with both images and audios of lectures, "
    "and your purpose is to help users understand and generate the important notes for them."
)

# Button to start the summarization process
if st.button("Generate Summarization"):

    # Check if neither audio nor image is uploaded
    if not audio_file and not image_file:
        st.error("Please upload at least one audio file (MP3) or an image file to generate summarization.")
    else:
        # Only perform transcription if audio is uploaded
        if audio_file:
            progress_placeholder.text("Transcribing audio...")
            try:
                audio_transcript = transcribe_audio(audio_file)
                progress_placeholder.empty()
                st.subheader("Audio Transcribed Successfully!")
            except Exception as e:
                st.error(f"Error during audio transcription: {e}")

        # Only perform text extraction if image is uploaded
        if image_file:
            progress_placeholder_2.text("Extracting text from the image...")
            try:
                document_text = detect_document(image_file)
                progress_placeholder_2.empty()
                st.subheader("Text Extracted From Image(s) Successfully!")
            except Exception as e:
                st.error(f"Error during document text detection: {e}")

        # If either transcript or document text is available, the chatbot can start processing
        if audio_transcript or document_text:
            combined_text = "Transcripted audio: {" + audio_transcript + "}, Text extracted from images: {" + document_text + "}"
            st.write("Now the AI will summarize the lecture materials.")

            # Conversation history list
            if 'history' not in st.session_state:
                st.session_state['history'] = []

            # Save audio and image text in conversation history
            st.session_state['history'].append({
                'user_input': combined_text
            })

            # Generate initial summary from the uploaded files
            initial_notes, bot_response = chatbot_response(st.session_state['history'], task_description, combined_text)

            # Display the generated initial notes
            st.subheader("Generated Lecture Notes")
            st.write(initial_notes)

            # Display the response from the chatbot
            st.write("AI: ", bot_response)

# Only show the chat history after the summarization button is clicked
if 'history' in st.session_state and st.session_state['history']:
    # User input for chatbot
    user_input = st.text_input("Continue the conversation or ask something about the uploaded files")

    if user_input:
        # Generate chatbot response based on the ongoing conversation
        subsequent_notes, bot_response = chatbot_response(st.session_state['history'], task_description, user_input)

        # Add the user input and bot response to the conversation history
        st.session_state['history'].append({
            'user': 'User',
            'user_input': user_input,
            'bot': 'Bot',
            'bot_response': bot_response
        })

        # Display the updated conversation history
        for chat in st.session_state['history']:
            if 'bot_response' in chat:
                st.write(f"**Bot**: {chat['bot_response']}")
