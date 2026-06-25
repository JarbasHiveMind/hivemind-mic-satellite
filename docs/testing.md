# Testing

The test suite is a single end-to-end suite under `tests/e2e/`. There is one
test directory; there are no unit-only tests and no `importorskip` / `skipif`
guards — the full HiveMind 2.x stack is a hard `[e2e]` dependency.

## Running the tests

```bash
uv pip install -e .[e2e]
pytest tests/
```

## What the e2e suite exercises

Tests boot a **real `hivemind-core` master in-process** (via the
[hivescope](https://github.com/JarbasHiveMind/hivescope) loopback hub) and drive
the satellite's **real** code over a **real `HiveMessageBusClient`** across a
localhost WebSocket. Only the *hardware* seams are mocked.

### `test_satellite_hivemind_e2e.py` — real satellite over a real hub

| Test | Path exercised |
|---|---|
| `test_microphone_stream_reaches_hub_binary` | Real `HiveMindMicrophoneClient.run()` capture loop, fed by a fake mic + fake VAD, streams `HiveMessageType.BINARY` / `RAW_AUDIO` frames to the real hub |
| `test_client_constructs_with_mocked_hardware` | Real client constructs, handshakes with the hub, binds handlers, with mic/VAD injected and media/PHAL disabled |
| `test_hub_speak_triggers_tts_request` | Hub agent `speak` routed to the peer → real `handle_speak` → `speak:synth` request sent back to the hub |
| `test_b64_tts_audio_queued_for_playback` | `speak:b64_audio.response` → real `handle_speak_b64` decodes the audio and enqueues it on the `PlaybackThread` queue |

### `test_bridge1_conformance.py` — OVOS-BRIDGE-1 / SESSION-1 conformance

Envelope, source stamping, destination routing, session fidelity, and FIFO
ordering, asserted against the real hub.

### `test_acl.py` — ACL policy admission

`allowed_types` denial, skill-blacklist injection, and reserved-session
rejection through the hub's policy chain.

## How the hardware is mocked

The satellite touches three hardware seams; each is replaced in-process with no
device, model, or network beyond localhost:

- **Microphone** — `OVOSMicrophoneFactory.create` is patched to return a
  `FakeMicrophone` that yields a fixed run of non-empty chunks then silence. No
  ALSA / PortAudio device is opened.
- **VAD** — `OVOSVADFactory.create` is patched to return a `FakeVAD` that reports
  speech for the first N reads then silence, driving the
  speech-start → stream → silence-timeout branch of `run()`.
- **Audio playback** — the client is constructed with `enable_media=False` so no
  `AudioService` (and no sound device) is created, and `PHAL` is absent. The
  `PlaybackThread` is never `start()`-ed; queued playback items are inspected
  directly instead of reaching a speaker.

Everything else — the VAD-gated capture loop, encryption, the
`HiveMessageBusClient`, the WebSocket transport, the `hivemind-core` listener,
binary protocol, agent bus, and policy chain — is genuine production code.

## CI

The e2e suite runs on every PR via `.github/workflows/e2e_tests.yml`, which calls
the shared `OpenVoiceOS/gh-automations` `build-tests` workflow with
`install_extras: e2e` and `test_path: tests/e2e/`. `build_tests.yml` additionally
clean-installs the package across Python 3.10–3.13; `coverage.yml` reports
coverage of `hivemind_mic_sat`.
