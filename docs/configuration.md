# Configuration

---

## CLI flags

All flags are optional. If a flag is omitted, the value is read from the identity file (`~/.local/share/hivemind-client/identity.json`).

| Flag | Type | Default | Description |
|---|---|---|---|
| `--key` | string | identity file | HiveMind access key |
| `--password` | string | identity file | HiveMind password |
| `--host` | string | identity file | HiveMind host (for example `192.168.1.10` or `wss://myhive.example.com`). The client adds `ws://` automatically if you give no scheme. |
| `--port` | int | identity file or `5678` | HiveMind WebSocket port |
| `--siteid` | string | identity file or `unknown` | Location identifier added to `message.context` |

Example: connect to a remote hive with explicit credentials:

```bash
hivemind-mic-sat \
  --key abc123 \
  --password secret \
  --host 192.168.1.10 \
  --port 5678 \
  --siteid living-room
```

---

## Identity file

`hivemind-client set-identity` writes `~/.local/share/hivemind-client/identity.json`. All fields correspond to the CLI flags above. Once set, you can run `hivemind-mic-sat` with no arguments.

---

## OpenVoiceOS configuration file

The satellite uses the same configuration file as all OVOS components:

```
~/.config/mycroft/mycroft.conf
```

All plugin settings live here. The file is JSON.

---

## Microphone plugins

A microphone plugin is required. Set it in `mycroft.conf`:

```json
{
  "microphone": {
    "module": "ovos-microphone-plugin-alsa",
    "ovos-microphone-plugin-alsa": {
      "device": "default"
    }
  }
}
```

### Selecting the audio input device

Find available ALSA devices:

```bash
arecord -l
```

Use the card/device index in the plugin config. Example for card 1, device 0:

```json
{
  "microphone": {
    "module": "ovos-microphone-plugin-alsa",
    "ovos-microphone-plugin-alsa": {
      "device": "hw:1,0"
    }
  }
}
```

### Available microphone plugins

| Plugin | Install | Notes |
|---|---|---|
| `ovos-microphone-plugin-alsa` | `pip install ovos-microphone-plugin-alsa` | Linux ALSA: default |
| `ovos-microphone-plugin-pyaudio` | `pip install ovos-microphone-plugin-pyaudio` | Cross-platform |
| `ovos-microphone-plugin-sounddevice` | `pip install ovos-microphone-plugin-sounddevice` | Alternative cross-platform |

Full list: [OVOS Microphone Plugins](https://openvoiceos.github.io/ovos-technical-manual/mic_plugins/)

---

## VAD plugins

A VAD (voice activity detection) plugin is required. It determines when audio contains speech, and controls when the satellite streams chunks to the hive.

```json
{
  "VAD": {
    "module": "ovos-vad-plugin-silero"
  }
}
```

### Silence threshold

The satellite stops streaming after 6 seconds of continuous silence, hardcoded in the run loop as the `max_silence_duration` value in `hivemind_mic_sat/__init__.py`.

### Available VAD plugins

| Plugin | Install | Notes |
|---|---|---|
| `ovos-vad-plugin-silero` | `pip install ovos-vad-plugin-silero` | Recommended; neural VAD |
| `ovos-vad-plugin-webrtcvad` | `pip install ovos-vad-plugin-webrtcvad` | Lightweight WebRTC VAD |

Full list: [OVOS VAD Plugins](https://openvoiceos.github.io/ovos-technical-manual/vad_plugins/)

---

## Optional plugins

### PHAL (Platform/Hardware Abstraction Layer)

If `ovos-PHAL` is installed, the satellite starts it automatically using the HiveMind bus. PHAL supports hardware integrations such as LED rings, buttons, or display updates on devices like the Mycroft Mark 1/2.

```bash
pip install ovos-PHAL
```

### TTS Transformers

TTS transformers mutate TTS audio before playback, for example changing speed or applying a filter. See [TTS Transformer Plugins](https://openvoiceos.github.io/ovos-technical-manual/audio_service/#transformer-plugins).

### G2P (Grapheme-to-Phoneme)

G2P plugins generate visemes for mouth movement animations, for example on the Mycroft Mk1 faceplate. See [G2P Plugins](https://openvoiceos.github.io/ovos-technical-manual/g2p_plugins/).

### Media Playback / OCP

These plugins enable voice-commanded media playback, for example "play some jazz".

```bash
pip install ovos-ocp-audio-plugin
```

Configure these plugins in `mycroft.conf` under `"Audio"` and `"OCP"`. See [Media Plugins](https://openvoiceos.github.io/ovos-technical-manual/media_plugins/) and [OCP Plugins](https://openvoiceos.github.io/ovos-technical-manual/ocp_plugins/).

---

## TTS audio transport

By default the satellite requests TTS as a binary audio stream from the hive (`speak:synth`). If your hive does not support binary transport, set `prefer_b64=True` in code, or use the `speak:b64_audio` path, which requests base64-encoded WAV audio and decodes it locally. You can select the `prefer_b64` path when you construct `HiveMindMicrophoneClient` programmatically. The CLI always defaults to binary.

---

## Full example config

```json
{
  "microphone": {
    "module": "ovos-microphone-plugin-alsa",
    "ovos-microphone-plugin-alsa": {
      "device": "default"
    }
  },
  "VAD": {
    "module": "ovos-vad-plugin-silero"
  }
}
```

---
[← Getting started](getting-started.md) · [Home](index.md) · [Architecture →](architecture.md)
