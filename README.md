# Sentiment Analysis Web Application

This project is a web application designed to perform sentiment analysis on audio recordings. It can transcribe audio from uploaded files or directly from YouTube links and analyze the sentiment of the transcribed text. The application is split into two main components

## Folders

- `server`: Contains the Flask backend which handles audio processing, transcription, sentiment analysis, and communication with Google Cloud APIs.
- `client`: Contains the Vue.js frontend which provides a user interface for uploading audio files, displaying transcriptions, and showing sentiment analysis results.

## Server (Backend)

The server side is implemented in Python using the Flask framework. It is responsible for:

- Receiving audio files and YouTube URLs from the frontend.
- Transcribing audio to text using Google Cloud Speech-to-Text API.
- Analyzing the sentiment of the transcribed text using Google Cloud Natural Language API.
- Sending the results back to the frontend.

## Client (Frontend)

The frontend is built with Vue.js and provides:

- A user interface for users to upload audio files or enter YouTube links.
- Displays for transcriptions and sentiment analysis results.
- Interactive elements like tables for detailed sentiment breakdown and gauges for overall sentiment visualization.

## Getting Started

To get the project up and running on your local machine for development and testing purposes, follow these steps:

### Prerequisites

- Python 3.8 or higher
- Node.js and npm

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sentiment-analysis-app.git

2. **Set up the backend:**
   ```bash
   cd sentiment-analysis-app/server
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. **Set up the frontend:**
    ```bash
    cd ../client
    npm install

### Running the Application
1. **Start the backend server:**
    ```bash
    cd server
    flask run

2. **Start the frontend development server:**
    ```bash
    cd ../client
    npm run serve

### Google API key
Ensure you set up your own Google Cloud 'key.json' for API access and refer to it in your environment variables to use the application.
