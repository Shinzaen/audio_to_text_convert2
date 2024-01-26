import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from google.cloud import speech_v1p1beta1
from google.api_core.exceptions import GoogleAPICallError
from dotenv import load_dotenv
import uuid
from pydub import AudioSegment
from pydub.utils import mediainfo

# .env 파일 로드
load_dotenv(verbose=True)

app = Flask(__name__)
socketio = SocketIO(app)
ffmpeg_path = os.getenv("FFMPEG_PATH")

# ffmpeg 경로 지정
AudioSegment.converter = ffmpeg_path + "/ffmpeg"

# 파일을 저장할 디렉토리 설정
UPLOAD_FOLDER = '/home/crsst222/audio_to_text/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def transcribe_audio(file_path):
    try:
        # API 키를 사용하여 SpeechClient를 생성합니다.
        client = speech_v1p1beta1.SpeechClient()
    except GoogleAPICallError as e:
        print("Google API 호출 오류:", e)
        return "오디오 처리 중 오류가 발생했습니다", 500

    # .m4a 파일을 .wav 파일로 변환
    wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'
    print(f"Converting to WAV: {file_path} -> {wav_file_path}")
    audio = AudioSegment.from_file(file_path, format="m4a")
    audio.export(wav_file_path, format="wav")

    # 오디오 및 인식 설정을 구성합니다.
    wav_info = mediainfo(wav_file_path)
    sample_rate_hertz = int(wav_info['sample_rate'])
    channels = int(wav_info['channels'])
    
    config = speech_v1p1beta1.RecognitionConfig(
        encoding=speech_v1p1beta1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate_hertz,
        audio_channel_count=channels,  # Updated to dynamically get the number of channels
        language_code="en-US",
        alternative_language_codes=["ko-KR"]
    )

    try:
        # 음성을 텍스트로 변환합니다.
        with open(wav_file_path, "rb") as audio_file:
            content = audio_file.read()
        response = client.recognize(config=config, audio={"content": content})
    except GoogleAPICallError as e:
        print("Google API 호출 오류:", e)
        return "오디오 처리 중 오류가 발생했습니다", 500

    # 응답에서 트랜스크립트를 추출합니다.
    transcripts = [result.alternatives[0].transcript for result in response.results]
    return transcripts

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "파일이 없습니다", 400

    file = request.files["file"]

    if file.filename == "":
        return "선택된 파일이 없습니다", 400

    # 파일의 확장자가 .wav가 아닌 경우, .wav로 변경합니다.
    if not file.filename.endswith('.wav'):
        file.filename = file.filename.rsplit('.', 1)[0] + '.wav'

    # 파일을 저장할 경로를 UUID를 사용하여 만듭니다.
    unique_filename = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename + '.wav')

    # 파일을 저장
    file.save(file_path)

    # transcribe_audio 함수를 호출하고 트랜스크립트를 가져옵니다.
    transcripts = transcribe_audio(file_path=file_path)

    # 트랜스크립트를 JSON 형식으로 반환합니다.
    return jsonify({"transcripts": transcripts})

@socketio.on('message')
def handle_message(msg):
    print('Received message: ' + msg)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80, use_reloader=False)

