# 📚 LectureMate

An intelligent AI-powered lecture assistant that helps students understand, summarize, and interact with lecture content through audio transcription, image text extraction, and conversational AI.

## 🌟 Features

- **Audio Transcription**: Convert lecture audio (MP3) to text using Google Cloud Speech API
- **Image Text Extraction**: Extract text from lecture notes images using Google Cloud Vision API
- **AI Chat Assistant**: Interactive chatbot powered by Google Gemini for answering questions about lecture content
- **Lecture Summarization**: Automatic generation of comprehensive lecture summaries
- **Study Notes Creation**: AI-generated study notes with key concepts and definitions
- **Modern UI**: ChatGPT-like interface built with Streamlit

## 🎯 Capabilities

The AI assistant can help you with:
- 📝 Summarizing lecture content from audio and images
- 🔍 Breaking down complex topics into digestible points
- 📚 Creating study notes with key concepts and definitions
- ❓ Answering questions about lecture material
- 💡 Providing examples to illustrate concepts
- 🏷️ Highlighting important terms and relationships
- 📋 Suggesting potential exam questions
- 📅 Helping create study plans

## 🛠️ Setup & Installation

### Prerequisites

1. **Python 3.8+**
2. **Google Cloud Account** with enabled APIs:
   - Google Cloud Speech-to-Text API
   - Google Cloud Vision API
3. **Google AI Studio Account** for Gemini API access

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lecturemate
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit google-cloud-vision google-cloud-speech google-generativeai
   ```

3. **Set up Google Cloud credentials**
   - Create a service account in Google Cloud Console
   - Download the JSON credentials file
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
     ```

4. **Configure Google Gemini API**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Replace the API key in `main.py`:
     ```python
     genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
     ```

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```

2. **Upload lecture materials**
   - Use the sidebar to upload lecture audio (MP3 format)
   - Upload images of lecture notes (JPG, JPEG, PNG)

3. **Process uploads**
   - Click "Process Uploads" to transcribe audio and extract text from images
   - The AI will automatically generate an initial lecture summary

4. **Chat with the AI**
   - Ask questions about the lecture content
   - Request specific summaries or explanations
   - Get study notes and key concepts

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:

```
streamlit>=1.28.0
google-cloud-vision>=3.4.0
google-cloud-speech>=2.21.0
google-generativeai>=0.3.0
```

## 🔧 Configuration

### Environment Variables

```bash
# Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# Optional: Set specific project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### API Configuration

Make sure to replace the hardcoded API key in `main.py` with your actual Gemini API key:

```python
genai.configure(api_key="YOUR_ACTUAL_API_KEY")
```

For production, consider using environment variables:

```python
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

## 🎨 Features Overview

### Audio Processing
- Supports MP3 format
- Automatic punctuation
- English language support (configurable)
- Real-time transcription feedback

### Image Processing
- Document text detection
- Support for handwritten and printed text
- Multiple image formats supported

### AI Chat Interface
- Context-aware responses
- Lecture material integration
- Educational tone and formatting
- Conversation history maintenance

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Credentials**: Store Google Cloud credentials securely
- **Environment Variables**: Use environment variables for sensitive data

## 🐛 Troubleshooting

### Common Issues

1. **Google Cloud API Errors**
   - Ensure APIs are enabled in Google Cloud Console
   - Check credentials file path and permissions
   - Verify billing is enabled for your project

2. **Audio Transcription Issues**
   - Ensure audio file is in MP3 format
   - Check audio quality and clarity
   - Verify file size limits

3. **Image Text Extraction Issues**
   - Use clear, high-resolution images
   - Ensure text is legible in the image
   - Check supported image formats

## 📈 Future Enhancements

- Support for more audio formats (WAV, M4A)
- Multiple language support
- PDF text extraction
- Export functionality for summaries
- Integration with learning management systems
- Offline mode capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review Google Cloud API documentation
3. Create an issue in the repository

## 🙏 Acknowledgments

- Google Cloud APIs for speech and vision services
- Google Gemini for conversational AI
- Streamlit for the web interface framework 