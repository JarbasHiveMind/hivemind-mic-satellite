# Getting Started

This guide takes you from zero to a working microphone satellite in a few minutes.

---

## Prerequisites

### On the satellite device

- Python 3.10 or later
- A working microphone (USB or built-in)
- A speaker or audio output device
- Network access to the hive

### On the server (the hive)

- [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core) installed and running
- [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol) installed: this adds server-side audio processing (wakeword, STT, TTS)

Without `hivemind-audio-binary-protocol`, the server cannot process the streamed audio and the satellite does not work.

---

## Step 1: Install the satellite

```bash
pip install hivemind-mic-satellite
```

Verify the install:

```bash
hivemind-mic-sat --help
```

---

## Step 2: Create an access key on the hive

On the machine running `hivemind-core`, add a client entry for this satellite:

```bash
hivemind-core add-client --name my-mic-satellite
```

The command prints an `access_key` and a `password`. Keep both. You need them in the next step.

---

## Step 3: Configure the identity on the satellite

**Option A: store credentials in the identity file (recommended for persistent use):**

```bash
hivemind-client set-identity \
  --key <access_key> \
  --password <password> \
  --host <hive-ip-or-hostname>
```

The identity is written to `~/.config/hivemind/_identity.json`. The `hivemind-mic-sat` command reads it automatically on startup.

**Option B: pass credentials on the command line:**

```bash
hivemind-mic-sat \
  --key <access_key> \
  --password <password> \
  --host <hive-ip-or-hostname> \
  --port 5678
```

---

## Step 4: Install microphone and VAD plugins

The satellite requires a microphone plugin and a VAD plugin. Install at least one of each:

```bash
# Microphone: ALSA (Linux default)
pip install ovos-microphone-plugin-alsa

# VAD: Silero (recommended)
pip install ovos-vad-plugin-silero
```

Then set them in `~/.config/mycroft/mycroft.conf`:

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

See [configuration.md](configuration.md) for more plugin options and audio device selection.

---

## Step 5: Run

```bash
hivemind-mic-sat
```

Expected startup output:

```
== connected to HiveMind
Listener Loop Started
```

Speak near the microphone. The satellite streams audio to the hive once it detects voice activity. When the hive finishes processing and sends back TTS audio, the satellite plays it through the local speaker.

---

## Verify it works

1. Start the satellite. You should see `connected to HiveMind` and `Listener Loop Started`.
2. Say the configured wakeword (set on the server side).
3. Check the log. It should show `Speech start, initiating audio transmission`, then `UTTERANCE: ...` when the hive returns the transcript, and `SPEAK: ...` when the hive sends the response.
4. Confirm you hear the TTS response played through the speaker.

---

## Next steps

- [Configuration reference](configuration.md): tune microphone, VAD, audio device
- [Deployment](deployment.md): run as a systemd service, Raspberry Pi Zero setup
- [Troubleshooting](troubleshooting.md): if something does not work

---
[Home](index.md) · [Configuration →](configuration.md)
