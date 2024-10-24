# HiveMind Microphone Satellite

OpenVoiceOS Microphone Satellite, connect to [HiveMind Listener](https://github.com/JarbasHiveMind/HiveMind-listener)

A super lightweight alternative to [voice-satellite](https://github.com/JarbasHiveMind/HiveMind-voice-sat), only Microphone and VAD plugins runs on the mic-satellite, voice activity is streamed to `hivemind-listener` and all the processing happens there

> NOTE: `hivemind-listener` is required server side, the default `hivemind-core` does not provide audio streaming capabilities

## Install

Install with pip

```bash
$ pip install git+https://github.com/JarbasHiveMind/hivemind-mic-satellite
```

## Configuration

Microphone Satellite is built on top of [ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager), it uses the usual OpenVoiceOS configuration `~/.config/mycroft/mycroft.conf`

Supported plugins:

| Plugin Type | Description | Required | Link |
|-------------|-------------|----------|------|
| Microphone | Captures voice input | Yes | [Microphone](https://openvoiceos.github.io/ovos-technical-manual/mic_plugins/) |
| VAD | Voice Activity Detection | Yes | [VAD](https://openvoiceos.github.io/ovos-technical-manual/vad_plugins/) |

> NOTE: the mic satellite can not (yet) play media, if you ask OVOS to "play XXX" nothing will happen as the mic-satellite will ignore the received uri
