# Architecture (Advanced)

This page describes exactly what runs on the satellite device, what crosses the wire, and why the design makes sense for low-power hardware.

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

The entire on-device processing pipeline is:

1. **Microphone plugin** (`OVOSMicrophoneFactory`) — reads raw audio chunks at the configured sample rate.
2. **VAD engine** (`OVOSVADFactory`) — classifies each chunk as speech or silence.
3. **Streaming logic** — when speech starts, each chunk is emitted over the HiveMind connection as a `HiveMessageType.BINARY` message with payload type `HiveMindBinaryPayloadType.RAW_AUDIO`. Streaming continues until 6 seconds of continuous silence have elapsed after the last speech chunk.
4. **PlaybackThread** — a thread that dequeues TTS audio files and plays them via `ovos-audio`.
5. **TTSHandler** — a `BinaryDataCallbacks` subclass that receives binary TTS audio from the hive, writes it to `/tmp/<filename>`, and queues it for playback.

---

## What crosses the wire

### Satellite → Hive (upstream)

- Raw audio chunks as `HiveMessageType.BINARY` / `HiveMindBinaryPayloadType.RAW_AUDIO`.  
  Only chunks during detected voice activity are sent; silence is suppressed by the VAD.

### Hive → Satellite (downstream)

- OVOS bus messages wrapped in `HiveMessageType.BUS`:
  - `recognizer_loop:wakeword` — wakeword detected (logged)
  - `recognizer_loop:record_begin` / `record_end` — STT phase started/ended
  - `recognizer_loop:utterance` — transcription result
  - `recognizer_loop:speech.recognition.unknown` — STT failed
  - `mycroft.audio.play_sound` — play a local sound file
  - `speak` — TTS request (satellite requests audio back)
  - `speak:b64_audio.response` — base64-encoded TTS audio
  - `ovos.utterance.handled` — intent was handled

- Binary TTS audio received via `BinaryDataCallbacks.handle_receive_tts` (satellite requested synthesis via `speak:synth`).

---

## TTS playback path

When the hive sends a `speak` message:

1. The satellite sends back a `speak:synth` request (or `speak:b64_audio` if `prefer_b64=True`).
2. The hive synthesises speech and sends the audio binary (or base64) back.
3. `TTSHandler.handle_receive_tts` writes the audio to `/tmp/<hash>.wav`.
4. The file is queued in `PlaybackThread`.
5. `PlaybackThread` (from `ovos-audio`) plays the file and, if a G2P plugin is configured, generates mouth movement visemes.

---

## Session and identity

- Each satellite has a `NodeIdentity` (stored in `~/.local/share/hivemind-client/identity.json`) with an `access_key`, `password`, `default_master` (host), and optional `site_id`.
- The `site_id` / `--siteid` flag is injected into `message.context` so the hive knows which physical location the audio came from.
- A `Session` is created locally (`FakeBus(session=Session())`) and shared between the internal bus and the playback thread for message routing.

---

## Reconnection

Connection management is handled by `HiveMessageBusClient`. On startup the client calls `connect()` and then waits on `connected_event`. Reconnection behaviour (retry, backoff) is provided by `hivemind-bus-client`.

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
| RAM/CPU on device | Minimal (mic + VAD only) | Low | Moderate–high |
| Network bandwidth | Moderate (raw audio stream) | Moderate (raw audio) | Low (text only) |
| Server dependency | High — server does everything | Medium — wakeword is local | Low — server is optional fallback |
| Privacy | Audio leaves device | Audio leaves device | Only text leaves device |
| Latency | Depends on server RTT + STT speed | Depends on server RTT | Mostly local |

**mic-satellite is the right choice when:**
- Hardware is too constrained for local models (Raspberry Pi Zero, microcontrollers with a companion SBC, embedded Linux)
- You control the server and trust the network
- You want to centralise model management and updates on the hive

**voice-sat is better when:**
- Audio privacy is critical (text only crosses the wire)
- The device has enough RAM/CPU for local STT+TTS
- Low latency matters more than hardware cost

---

## PHAL integration

If `ovos-PHAL` is importable at startup, a `PHAL` instance is created and connected to the HiveMind bus (`self.hm_bus`). This allows hardware plugins (LED rings, buttons, faceplate) to react to bus events forwarded from the hive and to inject hardware-triggered events back to the hive.
