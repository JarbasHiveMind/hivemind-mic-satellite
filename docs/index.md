# HiveMind Microphone Satellite — Documentation

**hivemind-mic-satellite** is the thinnest HiveMind satellite. Only a Microphone plugin and a VAD (Voice Activity Detection) plugin run on the device. When voice activity is detected, raw audio chunks are streamed over the HiveMind WebSocket connection to the server, which performs wakeword detection, speech-to-text, intent processing, and text-to-speech synthesis. The satellite receives the synthesised TTS audio and plays it back locally.

Wakeword, STT, and TTS are **owned by the hive** and sit behind its access-key authentication — the hive operator chooses the engines and voice, not the device. mic-satellite is the **resource** choice (cheapest hardware, no local models). Note its limit: with no local wakeword it streams *all* detected voice activity, which is bandwidth-heavy and suits a **homelab with personal devices** rather than **HiveMind-as-a-service** at scale. For a service-style deployment, [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) gates audio behind a local wakeword and scales better.

No local speech models are required. The device is essentially a smart microphone with a speaker attached to the hive.

---

## Satellite spectrum — where does processing happen?

| Satellite | Mic | VAD | Wakeword | STT | TTS | Best for |
|---|---|---|---|---|---|---|
| [HiveMind-cli](https://github.com/JarbasHiveMind/HiveMind-cli) | — | — | — | — | — | Text-only (keyboard/script) |
| **hivemind-mic-satellite** (this repo) | local | local | **server** | **server** | **server** | Cheapest HW / homelab; no local models |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | local | local | local | **server** | **server** | Local wakeword; scales as a service |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | local | local | local | local | local | Full local stack, sends text |

---

## Pages

- [Getting started](getting-started.md) — prerequisites, install, pairing, first run
- [Configuration](configuration.md) — CLI flags, config file, plugins, audio devices
- [Architecture](architecture.md) — on-device path, protocol, TTS playback, design trade-offs
- [Deployment](deployment.md) — systemd, autostart, Raspberry Pi Zero hardware notes
- [Dependencies](dependencies.md) — runtime + e2e deps and the bus-client 2.x story
- [Testing](testing.md) — the e2e suite, how hardware is mocked, running tests
- [Troubleshooting](troubleshooting.md) — common failure modes and fixes

---

## Quick links

- [GitHub repository](https://github.com/JarbasHiveMind/hivemind-mic-satellite)
- [PyPI package](https://pypi.org/project/hivemind-mic-satellite/)
- [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core)
- [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) (required server-side)
