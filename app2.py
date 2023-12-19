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

    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_translation_config.speech_recognition_language="de-DE"

    target_language="en"
    speech_translation_config.add_target_language(target_language)

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    translation_recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_translation_config, audio_config=audio_config)

    print("Speak into your microphone.")
    translation_recognition_result = translation_recognizer.recognize_once_async().get()

    if translation_recognition_result.reason == speechsdk.ResultReason.TranslatedSpeech:
        recognized_text = translation_recognition_result.text
        translation = translation_recognition_result.translations[target_language]
        return recognized_text, translation
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized: {}".format(translation_recognition_result.no_match_details)
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        return "Speech Recognition canceled: {}".format(cancellation_details.reason)
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            return "Error details: {}".format(cancellation_details.error_details)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_speech_recognition', methods=['GET'])
def start_speech_recognition():
    result = asyncio.run(recognize_from_microphone_async())
    return jsonify({'recognized_text': result[0], 'translation': result[1]})

if __name__ == '__main__':
    app.run()

