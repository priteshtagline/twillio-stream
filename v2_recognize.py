import io
import os
from uuid import uuid4

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ringochat-python-fbf8c9597cc9.json"


def transcribe_streaming_v2(project_id, recognizer_id, audio_file):
    # Instantiates a client
    client = SpeechClient()

    request = cloud_speech.CreateRecognizerRequest(
        parent=f"projects/{project_id}/locations/global",
        recognizer_id=recognizer_id,
        recognizer=cloud_speech.Recognizer(
            language_codes=["en-US"], model="latest_long"
        ),
    )

    # Creates a Recognizer
    operation = client.create_recognizer(request=request)
    recognizer = operation.result()

    # Reads a file as bytes
    with io.open(audio_file, "rb") as f:
        content = f.read()

    # In practice, stream should be a generator yielding chunks of audio data
    chunk_length = len(content) // 5
    stream = [
        content[start: start + chunk_length]
        for start in range(0, len(content), chunk_length)
    ]
    audio_requests = (
        cloud_speech.StreamingRecognizeRequest(audio=audio) for audio in stream
    )

    recognition_config = cloud_speech.RecognitionConfig(
        auto_decoding_config={})
    streaming_config = cloud_speech.StreamingRecognitionConfig(
        config=recognition_config
    )
    config_request = cloud_speech.StreamingRecognizeRequest(
        recognizer=recognizer.name, streaming_config=streaming_config
    )

    def requests(config, audio):
        yield config
        for message in audio:
            yield message

    # Transcribes the audio into text
    responses_iterator = client.streaming_recognize(
        requests=requests(config_request, audio_requests)
    )
    responses = []
    for response in responses_iterator:
        responses.append(response)
        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))

    return responses


recognizer_id = "recognizer-" + str(uuid4())


transcribe_streaming_v2("ringochat", recognizer_id, "audio.wav")
