import asyncio
import os

from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ringochat-python-fbf8c9597cc9.json"


def transcribe_streaming(stream_file):
    """Streams transcription of the given audio file."""
    import io

    client = speech.SpeechClient()

    with io.open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
        sample_rate_hertz=8000,
        language_code="en-US",
        model= 'phone_call'
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )

    print(responses)

    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        print(response.speech_event_type)
        for result in response.results:
            print("Finished: {}".format(result.is_final))
            print("Stability: {}".format(result.stability))
            alternatives = result.alternatives
            # The alternatives are ordered from most likely to least.
            for alternative in alternatives:
                print("Confidence: {}".format(alternative.confidence))
                print(u"Transcript: {}".format(alternative.transcript))

transcribe_streaming('audio.wav')