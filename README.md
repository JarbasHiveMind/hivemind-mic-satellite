# HiveMind Microphone Satellite

OpenVoiceOS Microphone Satellite, connect to [HiveMind Listener](https://github.com/JarbasHiveMind/HiveMind-listener)

A super lightweight version of [voice-satellite](https://github.com/JarbasHiveMind/HiveMind-voice-sat), only Microphone and VAD plugins runs on the mic-satellite, voice activity is streamed to `hivemind-listener` and all the processing happens there

> NOTE: `hivemind-listener` is required server side, the default `hivemind-core` does not provide audio streaming capabilities

## Install

Install dependencies (if needed)

```bash
sudo apt-get install -y libpulse-dev libasound2-dev
```

Install with pip

```bash
$ pip install git+https://github.com/JarbasHiveMind/hivemind-mic-satellite
```


## Configuration

Voice relay is built on top of [ovos-simple-listener](https://github.com/TigreGotico/ovos-simple-listener), it uses the same OpenVoiceOS configuration `~/.config/mycroft/mycroft.conf`

Supported plugins:

| Plugin Type | Description | Required | Link |
|-------------|-------------|----------|------|
| Microphone | Captures voice input | Yes | [Microphone](https://openvoiceos.github.io/ovos-technical-manual/mic_plugins/) |
| VAD | Voice Activity Detection | Yes | [VAD](https://openvoiceos.github.io/ovos-technical-manual/vad_plugins/) |

> NOTE: the mic satellite can not (yet) play media, if you ask OVOS to "play XXX" nothing will happen as the mic-satellite will ignore the received uri
