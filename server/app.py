from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech, language_v2
from google.cloud.language_v2 import types as language_types
from google.cloud import storage
from pydub import AudioSegment
from pydub.utils import mediainfo
from pytube import YouTube
import io
import os

app = Flask(__name__)
CORS(app)

# načítanie Google Cloud klient
speech_client = speech.SpeechClient()
language_client = language_v2.LanguageServiceClient()

#nahrávanie do Google bucket
def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    return f"gs://{bucket_name}/{blob_name}"

#speech-to-text nahrávok dlhších ako 60s
def transcribe_long_audio(gcs_uri, language_code):
    """Transcribe long audio files using asynchronous speech recognition."""
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code,
        enable_automatic_punctuation=True
    )
    
    operation = speech_client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)
    
    transcript = ''.join(result.alternatives[0].transcript for result in response.results)
    return transcript

#stiahnutie zvuku z YT videa
def download_youtube_audio(youtube_link):
    yt = YouTube(youtube_link)
    stream = yt.streams.filter(only_audio=True).first()
    default_filename = stream.default_filename
    stream.download(filename=f"{default_filename}.mp4")
    return f"{default_filename}.mp4"

#konverzia nahrávky do formatu wav
def convert_audio_to_wav(filename):
    audio = AudioSegment.from_file(filename)
    audio = audio.set_channels(1)
    mono_audio_filename = filename.replace(".mp4", ".wav")
    audio.export(mono_audio_filename, format="wav")
    os.remove(filename)
    return mono_audio_filename

#speech-to-text pre YT
def transcribe_audio2(file_path, language_code):
    file_length = mediainfo(file_path).get('duration', 0)
    if float(file_length) > 60:
        bucket_name = "sentiment-analysis-audio-bucket"
        gcs_uri = upload_to_bucket("audio_files/" + os.path.basename(file_path), file_path, bucket_name)
        transcript = transcribe_long_audio(gcs_uri, language_code)
    else:
        with io.open(file_path, "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language_code,
            enable_automatic_punctuation=True
        )
        response = speech_client.recognize(config=config, audio=audio)
        transcript = ''.join(result.alternatives[0].transcript for result in response.results)

    return transcript

#analýza sentimentu prepísaného textu
def analyze_text_sentiment(text):
    document = language_types.Document(content=text, type_=language_v2.Document.Type.PLAIN_TEXT)
    response = language_client.analyze_sentiment(request={'document': document})
    document_sentiment = response.document_sentiment

    sentences_sentiment = [
        {"text": sentence.text.content, "score": sentence.sentiment.score, "magnitude": sentence.sentiment.magnitude}
        for sentence in response.sentences
    ]

    return document_sentiment.score, document_sentiment.magnitude, sentences_sentiment

#endpoint prepisu vloženej nahrávky
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    language_code = request.form.get('language', 'en-GB')
    sound = AudioSegment.from_file_using_temporary_files(file)
    sound = sound.set_channels(1)
    mono_audio = io.BytesIO()
    sound.export(mono_audio, format="wav")
    mono_audio.seek(0)
    print(language_code)

    audio = speech.RecognitionAudio(content=mono_audio.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code,
        enable_automatic_punctuation=True
    )

    response = speech_client.recognize(config=config, audio=audio)
    transcript = ''.join(result.alternatives[0].transcript for result in response.results)


    score, magnitude, sentences_sentiment = analyze_text_sentiment(transcript)

    return jsonify({
        "transcript": transcript,
        "overall_sentiment": {
            "score": score,
            "magnitude": magnitude
        },
        "sentences_sentiment": sentences_sentiment
    })

#endpoint prepisu z YT
@app.route('/transcribe_youtube', methods=['POST'])
def transcribe_youtube_video():
    data = request.get_json()
    youtube_link = data.get('youtubeLink')
    language_code = data.get('language', 'en-GB') 
    if not youtube_link:
        return jsonify({"error": "No YouTube link provided"}), 400

    filename = download_youtube_audio(youtube_link)
    wav_filename = convert_audio_to_wav(filename)
    transcript = transcribe_audio2(wav_filename, language_code) 
    os.remove(wav_filename)  # Clean up the WAV file

    score, magnitude, sentences_sentiment = analyze_text_sentiment(transcript)

    return jsonify({
        "transcript": transcript,
        "overall_sentiment": {
            "score": score,
            "magnitude": magnitude
        },
        "sentences_sentiment": sentences_sentiment
    })

if __name__ == '__main__':
    app.run(debug=True)


