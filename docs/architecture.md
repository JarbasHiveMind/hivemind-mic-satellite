# Architecture (Advanced)

This page describes exactly what runs on the satellite device, what crosses the wire, and why the design fits low-power hardware.

---

## On-device components

```
Microphone plugin  →  VAD engine  →  HiveMessageBusClient (WebSocket)
                                           ↑
                                     PlaybackThread  ←  TTSHandler
                                           ↑
                                     AudioService (optional media)
                                     PHAL (optional HW abstraction)
```

The on-device processing pipeline works as follows.

1. **Microphone plugin** (`OVOSMicrophoneFactory`) reads raw audio chunks at the configured sample rate.
2. **VAD engine** (`OVOSVADFactory`) classifies each chunk as speech or silence.
3. **Streaming logic** emits each chunk over the HiveMind connection as a `HiveMessageType.BINARY` message with payload type `HiveMindBinaryPayloadType.RAW_AUDIO`, once speech starts. Streaming continues until 6 seconds of continuous silence have passed since the last speech chunk.
4. **PlaybackThread** dequeues TTS audio files and plays them through `ovos-audio`.
5. **TTSHandler**, a `BinaryDataCallbacks` subclass, receives binary TTS audio from the hive, writes it to `/tmp/<filename>`, and queues it for playback.

---

## What crosses the wire

### Satellite to hive (upstream)

- Raw audio chunks as `HiveMessageType.BINARY` / `HiveMindBinaryPayloadType.RAW_AUDIO`. The satellite sends only chunks during detected voice activity; the VAD suppresses silence.

### Hive to satellite (downstream)

- OVOS bus messages wrapped in `HiveMessageType.BUS`:
  - `recognizer_loop:wakeword`: wakeword detected (logged)
  - `recognizer_loop:record_begin` / `record_end`: STT phase started/ended
  - `recognizer_loop:utterance`: transcription result
  - `recognizer_loop:speech.recognition.unknown`: STT failed
  - `mycroft.audio.play_sound`: play a local sound file
  - `speak`: TTS request (satellite requests audio back)
  - `speak:b64_audio.response`: base64-encoded TTS audio
  - `ovos.utterance.handled`: intent was handled

- Binary TTS audio received via `BinaryDataCallbacks.handle_receive_tts` (the satellite requested synthesis through `speak:synth`).

---

## Scaling: homelab vs service

mic-satellite has no local wakeword, so the VAD ships every speech segment to the hive, not just post-activation commands. That keeps the device cheap but turns the upstream into a continuous raw-audio stream, and the server bears the full STT cost for all speech. This works well for a homelab with a few personal devices. It does not scale for a multi-tenant HiveMind-as-a-service offering, because per-client raw-audio streaming costs too much in bandwidth and compute. A [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) device, which streams only after a local wakeword fires, fits a service deployment better. Both delegate STT and TTS to the hive, owned and authenticated; they differ in how much audio crosses the wire, and therefore in how they scale.

## TTS playback path

When the hive sends a `speak` message:

1. The satellite sends back a `speak:synth` request (or `speak:b64_audio` if `prefer_b64=True`).
2. The hive synthesizes speech and sends the audio back as binary or base64.
3. `TTSHandler.handle_receive_tts` writes the audio to `/tmp/<hash>.wav`.
4. The file is queued in `PlaybackThread`.
5. `PlaybackThread`, from `ovos-audio`, plays the file and, if a G2P plugin is configured, generates mouth movement visemes.

---

## Session and identity

- Each satellite has a `NodeIdentity`, stored in `~/.local/share/hivemind-client/identity.json`, with an `access_key`, `password`, `default_master` (host), and an optional `site_id`.
- The `site_id` / `--siteid` flag is injected into `message.context` so the hive knows which physical location the audio came from.
- A `Session` is created locally (`FakeBus(session=Session())`) and shared between the internal bus and the playback thread for message routing.

---

## Reconnection

`HiveMessageBusClient` handles connection management. On startup the client calls `connect()` and then waits on `connected_event`. `hivemind-bus-client` provides reconnection behavior, including retry and backoff.

---

## Sound files

The package ships three local sound files used by `mycroft.audio.play_sound` events from the hive:

```
hivemind_mic_sat/res/snd/acknowledge.mp3
hivemind_mic_sat/res/snd/error.mp3
hivemind_mic_sat/res/snd/start_listening.wav
```

If the URI in a `play_sound` message starts with `snd/`, the satellite resolves it against this bundled resource directory.

---

## Why thin? Trade-offs vs heavier satellites

| Factor | mic-satellite | voice-relay | voice-sat |
|---|---|---|---|
| Local model downloads | None | Wakeword model | Wakeword + STT + TTS models |
| RAM/CPU on device | Minimal (mic + VAD only) | Low | Moderate-high |
| Network bandwidth | Moderate (raw audio stream) | Moderate (raw audio) | Low (text only) |
| Server dependency | High: server does everything | Medium: wakeword is local | Low: server is optional fallback |
| Privacy | Audio leaves device | Audio leaves device | Only text leaves device |
| Latency | Depends on server round-trip time and STT speed | Depends on server round-trip time | Mostly local |

**mic-satellite is the right choice when:**
- Hardware is too constrained for local models (Raspberry Pi Zero, microcontrollers with a companion SBC, embedded Linux)
- You control the server and trust the network
- You want to centralize model management and updates on the hive

**voice-sat is better when:**
- Audio privacy is critical (only text crosses the wire)
- The device has enough RAM/CPU for local STT and TTS
- Low latency matters more than hardware cost

---

## PHAL integration

If `ovos-PHAL` is importable at startup, the satellite creates a `PHAL` instance and connects it to the HiveMind bus (`self.hm_bus`). This lets hardware plugins, such as LED rings, buttons, or a faceplate, react to bus events forwarded from the hive and inject hardware-triggered events back to the hive.

---
[← Configuration](configuration.md) · [Home](index.md) · [Deployment →](deployment.md)
