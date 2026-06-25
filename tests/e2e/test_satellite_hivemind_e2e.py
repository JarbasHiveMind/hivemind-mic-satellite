"""REAL satellite-side end-to-end tests for hivemind-mic-satellite.

These exercise the satellite's **real** ``HiveMindMicrophoneClient`` against a
**real** hivemind-core hub over a localhost WebSocket:

    fake mic + fake VAD  (mocked hardware)
        -> real HiveMindMicrophoneClient.run() VAD-gated capture loop
        -> HiveMessageType.BINARY / RAW_AUDIO on the satellite's REAL
           HiveMessageBusClient
        -> real WebSocket -> real hivemind-core hub -> binary protocol

and the reverse TTS legs:

    hub agent emits `speak` routed to the satellite peer
        -> real WebSocket -> satellite's REAL HiveMessageBusClient
        -> real HiveMindMicrophoneClient.handle_speak -> requests TTS upstream

    `speak:b64_audio.response` reaches the client
        -> real handle_speak_b64 -> decodes audio -> queued on PlaybackThread

Everything between the satellite client and the hub is the genuine production
``HiveMessageBusClient`` + hivemind-core stack over a localhost WebSocket
(hivescope's loopback hub). Only the *hardware* seams are mocked: the microphone
and VAD plugin factories return in-process fakes, and ``AudioService`` (media
playback) is disabled so no sound device is touched. The ``PlaybackThread`` is
never ``start()``-ed, so playback is observed by inspecting its queue instead of
hitting a speaker. There is no importorskip / skipif — the full 2.x stack is a
hard ``[e2e]`` dependency.
"""
import time
from queue import Queue
from unittest.mock import patch

import pybase64
import pytest
from ovos_bus_client.message import Message
from ovos_plugin_manager.utils.tts_cache import hash_sentence
from hivemind_bus_client.serialization import HiveMindBinaryPayloadType

from hivescope.topology import TopologyBuilder
from hivescope.assertions import assert_binary_delivered

import hivemind_mic_sat
from hivemind_mic_sat import HiveMindMicrophoneClient


pytestmark = pytest.mark.timeout(60)


# ---------------------------------------------------------------------------
# Mocked hardware — in-process fakes for the mic / VAD seams. The real
# HiveMindMicrophoneClient builds these via OVOSMicrophoneFactory /
# OVOSVADFactory in __init__, so patching the factories injects the fakes
# without any real plugin, device, or model.
# ---------------------------------------------------------------------------

class FakeMicrophone:
    """Microphone that yields a fixed number of non-empty chunks then silence."""

    sample_rate = 16000
    sample_width = 2
    chunk_size = 1600  # 100 ms at 16 kHz

    def __init__(self, n_speech_chunks=3):
        self._remaining = n_speech_chunks
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def read_chunk(self):
        time.sleep(0.005)
        if self._remaining > 0:
            self._remaining -= 1
            return b"\x01\x02" * (self.chunk_size // 2)
        return b"\x00" * self.chunk_size

    def stop(self):
        self.stopped = True


class FakeVAD:
    """VAD that reports speech for the first ``n_speech`` queries then silence,
    driving the client's speech-start -> stream -> silence-timeout path."""

    def __init__(self, n_speech=3):
        self._remaining = n_speech

    def is_silence(self, chunk):
        if self._remaining > 0:
            self._remaining -= 1
            return False
        return True


# ---------------------------------------------------------------------------
# Loopback hub + real satellite client helpers.
# ---------------------------------------------------------------------------

def _hub_with_satellite(allowed_types):
    """Boot a real loopback hub and pre-register one satellite key."""
    b = TopologyBuilder()
    m = b.add_master("M0", use_loopback=True)
    m.register_satellite("sat-key", password="sat-pass",
                         allowed_types=allowed_types)
    b.start_all()
    return b, m


def _host_port(url):
    bare = url.replace("ws://", "").replace("wss://", "").rstrip("/")
    host, port = bare.split(":")
    return "ws://" + host, int(port)


def _make_client(url, mic, vad, prefer_b64=False):
    """Construct the REAL HiveMindMicrophoneClient against the loopback hub with
    mocked mic/VAD and media playback disabled.

    Patches the OVOS plugin factories so __init__ injects the fakes, and patches
    PHAL out so no hardware service is started.
    """
    host, port = _host_port(url)
    with patch.object(hivemind_mic_sat.OVOSMicrophoneFactory, "create", return_value=mic), \
         patch.object(hivemind_mic_sat.OVOSVADFactory, "create", return_value=vad):
        client = HiveMindMicrophoneClient(
            enable_media=False,  # no AudioService -> no sound device
            prefer_b64=prefer_b64,
            key="sat-key", password="sat-pass",
            host=host, port=port,
            useragent="mic-sat-e2e", self_signed=False,
        )
    deadline = time.time() + 15
    while time.time() < deadline and not client.hm_bus.handshake_event.is_set():
        time.sleep(0.1)
    assert client.hm_bus.handshake_event.is_set(), \
        "satellite handshake did not complete"
    return client


# ---------------------------------------------------------------------------
# Inbound: real VAD-gated capture loop -> real hub binary protocol.
# ---------------------------------------------------------------------------

def test_microphone_stream_reaches_hub_binary():
    """The real run() loop, fed by a fake mic + fake VAD reporting speech,
    streams HiveMessageType.BINARY / RAW_AUDIO chunks to the real hub over a
    real WebSocket.

    Only the mic/VAD hardware is faked; the capture loop, encryption,
    HiveMessageBusClient, and hub binary protocol are all production code.
    """
    b, m = _hub_with_satellite(["recognizer_loop:utterance", "speak"])
    client = None
    import threading
    try:
        mic = FakeMicrophone(n_speech_chunks=3)
        vad = FakeVAD(n_speech=3)
        client = _make_client(m.network_protocol.url, mic, vad)
        time.sleep(1)  # let the encrypted HELLO register the peer
        assert len(m.connected_peers()) == 1, \
            f"expected 1 connected peer, got {m.connected_peers()}"

        # shorten the silence window so the loop stops streaming quickly
        run_thread = threading.Thread(target=client.run, daemon=True)
        run_thread.start()

        # wait for RAW_AUDIO to land at the hub
        deadline = time.time() + 10
        while time.time() < deadline and not m.binary_protocol.calls:
            time.sleep(0.05)

        client.running = False
        run_thread.join(timeout=5)

        assert m.binary_protocol.calls, \
            "no RAW_AUDIO binary frames reached the hub"
        assert_binary_delivered(m, count=len(m.binary_protocol.calls))
        # all recorded binary calls are RAW_AUDIO microphone input
        assert all(
            c.bin_type == HiveMindBinaryPayloadType.RAW_AUDIO
            for c in m.binary_protocol.calls
        ), "hub received non-RAW_AUDIO binary frames"
        assert mic.started, "mic.start() was never called by run()"
    finally:
        if client is not None:
            try:
                client.stop()
            except Exception:
                pass
            client.hm_bus.close()
        b.stop_all()


def test_client_constructs_with_mocked_hardware():
    """The REAL HiveMindMicrophoneClient constructs against the real HiveMind bus
    with mocked mic/VAD and media disabled, binds its event handlers, and the
    bus completes a real handshake with the hub.

    Proves the satellite's own client class works on the 2.x stack without any
    real audio hardware.
    """
    b, m = _hub_with_satellite(["recognizer_loop:utterance"])
    client = None
    try:
        client = _make_client(
            m.network_protocol.url,
            FakeMicrophone(), FakeVAD(),
        )
        time.sleep(1)
        assert len(m.connected_peers()) == 1
        # the mic/VAD fakes were injected by the patched factories
        assert isinstance(client.mic, FakeMicrophone)
        assert isinstance(client.vad, FakeVAD)
        # media disabled -> no AudioService, no PHAL hardware service
        assert client.audio is None
        assert client.phal is None
    finally:
        if client is not None:
            client.hm_bus.close()
        b.stop_all()


# ---------------------------------------------------------------------------
# Outbound: real hub `speak` -> real client handle_speak -> TTS request upstream.
# ---------------------------------------------------------------------------

def test_hub_speak_triggers_tts_request():
    """A `speak` emitted by the hub agent and routed to the satellite peer
    arrives on the satellite's real bus and the real handle_speak emits a
    `speak:synth` (or `speak:b64_audio`) request back to the hub over the real
    WebSocket.

    This is the hub -> satellite -> hub TTS-negotiation leg, all production code
    apart from the mocked mic/VAD.
    """
    b, m = _hub_with_satellite(["recognizer_loop:utterance", "speak",
                                "speak:synth"])
    client = None
    try:
        client = _make_client(
            m.network_protocol.url,
            FakeMicrophone(), FakeVAD(),
        )
        time.sleep(1)
        assert len(m.connected_peers()) == 1
        peer = m.connected_peers()[0]

        # the hub agent should observe the synth request the client sends back
        seen = []
        m.agent_protocol.bus.on("speak:synth", seen.append)

        m.agent_protocol.bus.emit(Message(
            "speak",
            {"utterance": "it is sunny", "lang": "en-US"},
            {"destination": [peer]},
        ))

        deadline = time.time() + 10
        while time.time() < deadline and not seen:
            time.sleep(0.05)

        assert seen, "client never sent a TTS synth request back to the hub"
        assert seen[0].data["utterance"] == "it is sunny"
    finally:
        if client is not None:
            client.hm_bus.close()
        b.stop_all()


# ---------------------------------------------------------------------------
# Outbound: b64 TTS audio -> real handle_speak_b64 -> queued for playback.
# ---------------------------------------------------------------------------

def test_b64_tts_audio_queued_for_playback():
    """A `speak:b64_audio.response` carrying base64 audio drives the real
    handle_speak_b64: it decodes the payload to a temp wav and enqueues it on
    the client's PlaybackThread queue.

    The PlaybackThread is never start()-ed, so nothing reaches a speaker — the
    queued item is the observable, hardware-free outcome of the production code
    path.
    """
    b, m = _hub_with_satellite(["recognizer_loop:utterance", "speak"])
    client = None
    try:
        client = _make_client(
            m.network_protocol.url,
            FakeMicrophone(), FakeVAD(),
        )
        # drain any queued items the real handlers may have enqueued
        client.playback.queue = Queue()

        utt = "hello from the hive"
        raw = b"RIFFfake-wav-bytes"
        payload = {
            "utterance": utt,
            "audio": pybase64.b64encode(raw).decode("utf-8"),
            "lang": "en-US",
        }
        # invoke the REAL handler exactly as the bus callback would
        client.handle_speak_b64(Message("speak:b64_audio.response", payload))

        item = client.playback.queue.get(timeout=5)
        wav = item[0]
        assert wav == f"/tmp/{hash_sentence(utt)}.wav"
        with open(wav, "rb") as f:
            assert f.read() == raw, "decoded audio did not match the b64 payload"
    finally:
        if client is not None:
            client.hm_bus.close()
        b.stop_all()
