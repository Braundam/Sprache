from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import azure.cognitiveservices.speech as speechsdk
 
app = Flask(__name__)
CORS(app, resources={r"/synthesize_speech": {"origins": "*"}})
 
# Azure Speech SDK configuration
speech_key = os.environ.get('SPEECH_KEY')
speech_region = os.environ.get('SPEECH_REGION')
 
# Set up the speech synthesizer
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
 
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/synthesize_speech', methods=['POST'])
def synthesize_speech():
    data = request.get_json()
    text = data.get('text', '')
 
    # Synthesize speech for the provided text
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
 
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return jsonify({'message': 'Speech synthesized successfully'})
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        return jsonify({'error': 'Speech synthesis canceled', 'reason': cancellation_details.reason})
 
if __name__ == '__main__':
    app.run()
