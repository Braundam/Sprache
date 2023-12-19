from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import azure.cognitiveservices.speech as speechsdk
import asyncio

app = Flask(__name__)
CORS(app, resources={r"/start_speech_recognition": {"origins": "*"}})

# Azure Speech SDK configuration
speech_key = os.environ.get('SPEECH_KEY')
speech_region = os.environ.get('SPEECH_REGION')

async def recognize_from_microphone_async():
    loop = asyncio.get_event_loop()

    def recognize():
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_recognition_language = "de-De"

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Speak into your microphone.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            return "No speech could be recognized: {}".format(speech_recognition_result.no_match_details)
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            return "Speech Recognition canceled: {}".format(cancellation_details.reason)
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                return "Error details: {}".format(cancellation_details.error_details)

    result = await loop.run_in_executor(None, recognize)
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_speech_recognition', methods=['GET'])
def start_speech_recognition():
    result = asyncio.run(recognize_from_microphone_async())
    return jsonify({'message': result})

if __name__ == '__main__':
    app.run()


