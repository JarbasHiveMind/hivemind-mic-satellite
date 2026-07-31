# Testing

The test suite is a single end-to-end suite under `tests/e2e/`. There is one test directory, no unit-only tests, and no `importorskip` / `skipif` guards. The full HiveMind 2.x stack is a hard `[e2e]` dependency.

## Running the tests

```bash
uv pip install -e .[e2e]
pytest tests/
```

## What the e2e suite exercises

Tests boot a real `hivemind-core` master in-process, through the [hivescope](https://github.com/JarbasHiveMind/hivescope) loopback hub, and drive the satellite's real code over a real `HiveMessageBusClient` across a localhost WebSocket. Only the hardware seams are mocked.

### `test_satellite_hivemind_e2e.py`: real satellite over a real hub

| Test | Path exercised |
|---|---|
| `test_microphone_stream_reaches_hub_binary` | Real `HiveMindMicrophoneClient.run()` capture loop, fed by a fake mic and a fake VAD, streams `HiveMessageType.BINARY` / `RAW_AUDIO` frames to the real hub |
| `test_client_constructs_with_mocked_hardware` | Real client constructs, handshakes with the hub, and binds handlers, with mic/VAD injected and media/PHAL disabled |
| `test_hub_speak_triggers_tts_request` | Hub agent `speak` routed to the peer, through real `handle_speak`, sends a `speak:synth` request back to the hub |
| `test_b64_tts_audio_queued_for_playback` | `speak:b64_audio.response` reaches real `handle_speak_b64`, which decodes the audio and enqueues it on the `PlaybackThread` queue |

### `test_bridge1_conformance.py`: OVOS-BRIDGE-1 / SESSION-1 conformance

This test asserts envelope, source stamping, destination routing, session fidelity, and FIFO ordering against the real hub.

### `test_acl.py`: ACL policy admission

This test checks `allowed_types` denial, skill-blacklist injection, and reserved-session rejection through the hub's policy chain.

## How the hardware is mocked

The satellite touches three hardware seams. Each is replaced in-process with no device, model, or network beyond localhost.

- **Microphone**: a patch replaces `OVOSMicrophoneFactory.create` with a `FakeMicrophone` that yields a fixed run of non-empty chunks, then silence. No ALSA / PortAudio device is opened.
- **VAD**: a patch replaces `OVOSVADFactory.create` with a `FakeVAD` that reports speech for the first N reads, then silence, driving the speech-start → stream → silence-timeout branch of `run()`.
- **Audio playback**: the client is constructed with `enable_media=False`, so no `AudioService` (and no sound device) is created, and `PHAL` is absent. The `PlaybackThread` never starts; the tests inspect queued playback items directly instead of reaching a speaker.

Everything else is genuine production code: the VAD-gated capture loop, encryption, the `HiveMessageBusClient`, the WebSocket transport, the `hivemind-core` listener, the binary protocol, the agent bus, and the policy chain.

## CI

The e2e suite runs on every PR through `.github/workflows/e2e_tests.yml`, which calls the shared `OpenVoiceOS/gh-automations` `build-tests` workflow with `install_extras: e2e` and `test_path: tests/e2e/`. `build_tests.yml` also clean-installs the package across Python 3.10-3.13. `coverage.yml` reports coverage of `hivemind_mic_sat`.

---
[← Deployment](deployment.md) · [Home](index.md) · [Troubleshooting →](troubleshooting.md)
