[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/JarbasHiveMind/hivemind-mic-satellite)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/hivemind-mic-satellite)](https://pypi.org/project/hivemind-mic-satellite/)

# HiveMind Microphone Satellite

**The thinnest HiveMind satellite — Microphone + VAD only. All speech processing happens on the hive.**

Audio is streamed from this device to a [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core) server running [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol). The server handles wakeword detection, STT, intent, and TTS synthesis; the satellite receives the synthesized speech audio and plays it back locally. No local STT or TTS models are needed — ideal for cheap, low-power hardware such as a Raspberry Pi Zero.

---

## Satellite spectrum — where does processing happen?

| Satellite | Mic | VAD | Wakeword | STT | TTS | Best for |
|---|---|---|---|---|---|---|
| [HiveMind-cli](https://github.com/JarbasHiveMind/HiveMind-cli) | — | — | — | — | — | Text-only (keyboard/script) |
| **hivemind-mic-satellite** (this repo) | local | local | **server** | **server** | **server** | Cheapest HW / homelab; no local models |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | local | local | local | **server** | **server** | Local wakeword; scales as a service |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | local | local | local | local | local | Full local stack, sends text |

---

## Server requirements

> **Important:** The default `hivemind-core` does not include audio processing.  
> You need [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) installed server-side to enable server-side wakeword, STT, and TTS.

---

## Why mic-satellite — and when not to

mic-satellite exists for one reason: **device resources**. With only a microphone and VAD on-device, it runs on the cheapest hardware (a Raspberry Pi Zero, a recycled phone) with zero local models. Everything else — wakeword, STT, intent, TTS — is **owned by the hive** and gated behind the same access-key authentication as the rest of the mesh. The hive operator decides the engines, models, and voice, uniformly; a satellite cannot override them. (Same ownership model as [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) — see its docs for the "HiveMind as a service" framing.)

**The trade-off, and the limit.** Because there is no local wakeword, the satellite streams **every** detected voice segment upstream (VAD-gated, but not gated by a wakeword). That continuous audio stream is bandwidth-heavy and puts the full STT load on the server for *all* speech, not just commands. It is the right call for a **homelab with a handful of personal devices**, where on-device resources are the binding constraint. It does **not** scale for **HiveMind-as-a-service** across many tenants — streaming raw audio per client is too costly. For a scalable, service-style deployment, prefer [voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay): local wakeword means audio only leaves the device after activation.

---

## Install

```bash
pip install hivemind-mic-satellite
```

Requires Python ≥ 3.10.

---

## 60-second quickstart

**1. On the hive (server) — create an access key for this device:**

```bash
hivemind-core add-client --name my-mic-sat
# note the access_key and password printed
```

**2. On the satellite device — set the identity:**

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

The satellite shares the standard OpenVoiceOS config file `~/.config/mycroft/mycroft.conf`.  
At minimum you need a microphone plugin and a VAD plugin:

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
| VAD | Yes | Voice activity detection (when to stream) |
| PHAL | No | Platform/hardware abstraction (e.g. LEDs, buttons) |
| TTS Transformers | No | Mutate TTS audio before playback |
| G2P | No | Visemes / mouth movement (e.g. Mycroft Mk1) |
| Media Playback | No | "Play Metallica"-style media commands |
| OCP Plugins | No | URL playback (YouTube, etc.) |

---

## Features not present (handled server-side)

- STT (speech-to-text) — runs on server
- TTS (text-to-speech) synthesis — runs on server
- Wakeword detection — runs on server
- Continuous listening / hybrid listening / sleep mode / recording mode
- Multiple wakewords
- Audio / dialog transformer plugins

---

## Documentation

Full zero-to-hero documentation is in [docs/](docs/):

- [Overview & satellite spectrum](docs/index.md)
- [Getting started](docs/getting-started.md)
- [Configuration reference](docs/configuration.md)
- [Architecture (advanced)](docs/architecture.md)
- [Deployment (systemd, Raspberry Pi)](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## Related

| Project | Role |
|---|---|
| [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core) | The hive — manages connected satellites |
| [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) | Server-side audio processing (required) |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | Satellite with local wakeword |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | Full local stack satellite |
| [HiveMind-cli](https://github.com/JarbasHiveMind/HiveMind-cli) | Text-only satellite |
| [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager) | Plugin framework (mic, VAD, PHAL, …) |

---

## License

Apache-2.0 — see [LICENSE](LICENSE).
