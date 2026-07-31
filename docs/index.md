# HiveMind Microphone Satellite: Documentation

hivemind-mic-satellite is the smallest HiveMind satellite. Only a microphone plugin and a VAD (voice activity detection) plugin run on the device. When the VAD detects voice activity, the satellite streams raw audio chunks over the HiveMind WebSocket connection to the server. The server performs wakeword detection, speech-to-text, intent processing, and text-to-speech synthesis, and the satellite receives the synthesized TTS audio and plays it back locally.

The hive owns wakeword, STT, and TTS, and gates them behind its access-key authentication: the hive operator chooses the engines and voice, not the device. mic-satellite is the choice for limited device resources: cheap hardware, no local models. Its limit follows from having no local wakeword: it streams all detected voice activity, which uses more bandwidth and suits a homelab with personal devices rather than HiveMind-as-a-service at scale. For a service-style deployment, [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) gates audio behind a local wakeword and scales better.

No local speech models are required. The device works as a microphone and speaker attached to the hive.

---

## Satellite spectrum: where does processing happen?

| Satellite | Mic | VAD | Wakeword | STT | TTS | Best for |
|---|---|---|---|---|---|---|
| [HiveMind-cli](https://github.com/JarbasHiveMind/HiveMind-cli) | n/a | n/a | n/a | n/a | n/a | Text-only (keyboard/script) |
| **hivemind-mic-satellite** (this repo) | local | local | server | server | server | Cheapest hardware / homelab; no local models |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | local | local | local | server | server | Local wakeword; scales as a service |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | local | local | local | local | local | Full local stack, sends text |

---

## Pages

- [Getting started](getting-started.md): prerequisites, install, pairing, first run
- [Configuration](configuration.md): CLI flags, config file, plugins, audio devices
- [Architecture](architecture.md): on-device path, protocol, TTS playback, design trade-offs
- [Deployment](deployment.md): systemd, autostart, Raspberry Pi Zero hardware notes
- [Testing](testing.md): the e2e suite, how hardware is mocked, running tests
- [Troubleshooting](troubleshooting.md): common failure modes and fixes

---

## Quick links

- [GitHub repository](https://github.com/JarbasHiveMind/hivemind-mic-satellite)
- [PyPI package](https://pypi.org/project/hivemind-mic-satellite/)
- [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core)
- [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) (required server-side)
