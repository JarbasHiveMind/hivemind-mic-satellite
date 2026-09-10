"""HIVEMIND-AUDIO-1 §5: a sender MUST include the fields its tag requires
for the receiver to act; for RAW_AUDIO that is sample_rate and sample_width.
§2: the receiver falls back to 16000 Hz / 16-bit only when metadata is absent,
so the satellite must forward the mic's real values instead of leaving them out.
"""
from hivemind_bus_client.message import HiveMessage, HiveMessageType
from hivemind_bus_client.serialization import HiveMindBinaryPayloadType

from hivemind_mic_sat import HiveMindMicrophoneClient


class FakeTransformers:
    plugins = []


class FakeMic:
    sample_rate = 44100
    sample_width = 2
    chunk_size = 4096

    def __init__(self, client):
        self._client = client
        self._chunks = [b"\x01" * 10, b"\x00" * 10]

    def start(self):
        pass

    def stop(self):
        pass

    def read_chunk(self):
        if self._chunks:
            return self._chunks.pop(0)
        self._client.running = False
        return None


class FakeVAD:
    def __init__(self):
        self._calls = 0

    def is_silence(self, chunk):
        self._calls += 1
        # first chunk is speech, second is silence
        return self._calls > 1


class FakePlayback:
    def start(self):
        pass


class FakeHmBus:
    def __init__(self):
        self.emitted = []

    def emit(self, message, binary_type=HiveMindBinaryPayloadType.UNDEFINED):
        self.emitted.append((message, binary_type))


def _make_client():
    client = HiveMindMicrophoneClient.__new__(HiveMindMicrophoneClient)
    client.mic = FakeMic(client)
    client.vad = FakeVAD()
    client.playback = FakePlayback()
    client.audio_transformers = FakeTransformers()
    client.hm_bus = FakeHmBus()
    client.phal = None
    return client


def test_raw_audio_frames_carry_mic_sample_rate_and_width():
    client = _make_client()

    client.run()

    # both the speech chunk and the trailing silence chunk are streamed
    # while still "in speech" (silence only ends the stream once it exceeds
    # the configured max_silence_duration), so both frames must carry
    # the mic's real metadata.
    assert len(client.hm_bus.emitted) == 2
    for message, binary_type in client.hm_bus.emitted:
        assert isinstance(message, HiveMessage)
        assert message.msg_type == HiveMessageType.BINARY
        assert binary_type == HiveMindBinaryPayloadType.RAW_AUDIO
        assert message.metadata == {"sample_rate": 44100, "sample_width": 2}
