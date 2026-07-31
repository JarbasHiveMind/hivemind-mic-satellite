[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/JarbasHiveMind/hivemind-mic-satellite)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/hivemind-mic-satellite)](https://pypi.org/project/hivemind-mic-satellite/)

# HiveMind Microphone Satellite

hivemind-mic-satellite is the smallest HiveMind satellite. It runs only a microphone plugin and a VAD (voice activity detection) plugin on the device.

Audio streams from this device to a [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core) server that runs [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol). The server handles wakeword detection, speech-to-text, intent processing, and text-to-speech synthesis. The satellite receives the synthesized speech audio and plays it back locally. No local STT or TTS models are needed, so the satellite can run on cheap, low-power hardware such as a Raspberry Pi Zero.

---

## Satellite spectrum: where does processing happen?

| Satellite | Mic | VAD | Wakeword | STT | TTS | Best for |
|---|---|---|---|---|---|---|
| [HiveMind-cli](https://github.com/JarbasHiveMind/HiveMind-cli) | n/a | n/a | n/a | n/a | n/a | Text-only (keyboard/script) |
| **hivemind-mic-satellite** (this repo) | local | local | server | server | server | Cheapest hardware / homelab; no local models |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | local | local | local | server | server | Local wakeword; scales as a service |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | local | local | local | local | local | Full local stack, sends text |

---

## Server requirements

The default `hivemind-core` does not include audio processing. Install [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) on the server to enable server-side wakeword, STT, and TTS.

---

## Why mic-satellite, and when not to use it

mic-satellite exists for one reason: device resources. With only a microphone and VAD on-device, it runs on cheap hardware, such as a Raspberry Pi Zero or a recycled phone, with no local models. The hive owns everything else: wakeword, STT, intent, and TTS. It gates them behind the same access-key authentication as the rest of the mesh. The hive operator chooses the engines, models, and voice for every connected satellite. A satellite cannot override them. This is the same ownership model as [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay). See its docs for the "HiveMind as a service" framing.

There is a trade-off. Because there is no local wakeword, the satellite streams every detected voice segment upstream (gated by VAD, not by a wakeword). This continuous audio stream uses more bandwidth and puts the full STT load on the server for all speech, not just commands. This works well for a homelab with a handful of personal devices, where on-device resources are the binding constraint. It does not scale for HiveMind-as-a-service across many tenants, because streaming raw audio per client costs too much. For a service-style deployment, prefer [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay): a local wakeword means audio leaves the device only after activation.

---

## Install

```bash
pip install hivemind-mic-satellite
```

Requires Python 3.10 or later.

---

## Quickstart

**1. On the hive (server): create an access key for this device:**

```bash
hivemind-core add-client --name my-mic-sat
# note the access_key and password printed
```

**2. On the satellite device: set the identity:**

```bash
hivemind-client set-identity \
  --key <access_key> \
  --password <password> \
  --host <hive-host-or-ip>
```

**3. Run:**

```bash
hivemind-mic-sat
```

Or pass credentials directly without storing them:

```bash
hivemind-mic-sat --key <key> --password <password> --host <host> --port 5678
```

---

## Minimal configuration

The satellite shares the standard OpenVoiceOS config file `~/.config/mycroft/mycroft.conf`. At minimum you need a microphone plugin and a VAD plugin:

```json
{
  "microphone": {
    "module": "ovos-microphone-plugin-alsa"
  },
  "VAD": {
    "module": "ovos-vad-plugin-silero"
  }
}
```

See [docs/configuration.md](docs/configuration.md) for all options, plugin selection, and audio device tuning.

---

## Supported plugins

| Plugin type | Required | Purpose |
|---|---|---|
| Microphone | Yes | Captures audio from hardware |
| VAD | Yes | Detects voice activity, decides when to stream |
| PHAL | No | Platform/hardware abstraction (for example LEDs, buttons) |
| TTS Transformers | No | Mutate TTS audio before playback |
| G2P | No | Visemes for mouth movement (for example Mycroft Mk1) |
| Media Playback | No | Media commands such as "play Metallica" |
| OCP Plugins | No | URL playback (YouTube and similar) |

---

## Features handled server-side, not on this device

- STT (speech-to-text)
- TTS (text-to-speech) synthesis
- Wakeword detection
- Continuous listening, hybrid listening, sleep mode, recording mode
- Multiple wakewords
- Audio and dialog transformer plugins

---

## Documentation

Full documentation is in [docs/](docs/):

- [Overview and satellite spectrum](docs/index.md)
- [Getting started](docs/getting-started.md)
- [Configuration reference](docs/configuration.md)
- [Architecture (advanced)](docs/architecture.md)
- [Deployment (systemd, Raspberry Pi)](docs/deployment.md)
- [Testing (e2e suite, mocked hardware)](docs/testing.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## Related

| Project | Role |
|---|---|
| [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core) | The hive, manages connected satellites |
| [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) | Server-side audio processing (required) |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | Satellite with local wakeword |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | Full local stack satellite |
| [HiveMind-cli](https://github.com/JarbasHiveMind/HiveMind-cli) | Text-only satellite |
| [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager) | Plugin framework (microphone, VAD, PHAL, and more) |

---

## License

Apache-2.0: see [LICENSE](LICENSE).
