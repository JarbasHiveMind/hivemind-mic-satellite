# HiveMind Microphone Satellite

OpenVoiceOS Microphone Satellite, connect to [HiveMind Listener](https://github.com/JarbasHiveMind/HiveMind-listener)

A super lightweight version of [voice-satellite](https://github.com/JarbasHiveMind/HiveMind-voice-sat), only Microphone and VAD plugins runs on the mic-satellite, voice activity is streamed to `hivemind-listener` and all the processing happens there

## Server requirements

> ⚠️ `hivemind-listener` is required server side, the default `hivemind-core` does not provide STT and TTS capabilities.

## Install

Install with pip

```bash
$ pip install hivemind-mic-satellite
```


## Configuration

Voice relay is built on top of [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager), it uses the same OpenVoiceOS configuration `~/.config/mycroft/mycroft.conf`

Supported plugins:

| Plugin Type | Description                         | Required | Link                                                                           |
|-------------|-------------------------------------|----------|--------------------------------------------------------------------------------|
| Microphone  | Captures voice input                | Yes      | [Microphone](https://openvoiceos.github.io/ovos-technical-manual/mic_plugins/) |
| VAD         | Voice Activity Detection            | Yes      | [VAD](https://openvoiceos.github.io/ovos-technical-manual/vad_plugins/)        |
| PHAL        | Platform/Hardware Abstraction Layer | No       | [PHAL](https://openvoiceos.github.io/ovos-technical-manual/PHAL/)              |

> NOTE: the mic satellite can not (yet) play media, if you ask OVOS to "play XXX" nothing will happen as the mic-satellite will ignore the received uri

The regular voice satellite is built on top of [ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener) and is full featured supporting all plugins

This repo needs less resources but it is also **missing** some features

- STT plugin (runs on server)
- TTS plugin (runs on server)
- WakeWord plugin (runs on server)
- Continuous Listening
- Hybrid Listening
- Recording Mode
- Sleep Mode
- Multiple WakeWords
- Audio Transformers plugins
- Dialog Transformers plugins
- TTS Transformers plugins
- Media Playback plugins
- OCP Stream plugins
