# Troubleshooting

---

## Connection issues

### `RuntimeError: NodeIdentity not set`

The satellite requires `key`, `password`, and `host` to connect. Either:
- Run `hivemind-client set-identity --key ... --password ... --host ...`
- Or pass `--key`, `--password`, and `--host` directly on the command line

### Cannot connect / WebSocket error

1. Confirm `hivemind-core` is running on the server and listening on the expected port (default `5678`).
2. Check that the host and port are correct:
   ```bash
   hivemind-mic-sat --host 192.168.1.10 --port 5678 ...
   ```
3. Test basic connectivity:
   ```bash
   nc -z 192.168.1.10 5678
   ```
4. Check that you created the `access_key` with `hivemind-core add-client` and that you use the correct key/password pair.

### SSL / self-signed certificate

If the hive uses `wss://` with a self-signed certificate, the client may reject it. Either:
- Add the certificate to the system trust store on the satellite.
- Use a plain `ws://` connection on a private network.

When you pass the host manually, include the scheme:

```bash
hivemind-mic-sat --host wss://myhive.example.com --port 443 ...
```

---

## No audio input (microphone not working)

1. Check that a microphone plugin is installed and configured:
   ```bash
   arecord -l
   ```
2. Test the microphone directly:
   ```bash
   arecord -D hw:1,0 -f S16_LE -r 16000 -d 3 test.wav && aplay test.wav
   ```
3. Ensure `mycroft.conf` has the correct `microphone.module` and device string.
4. Check permissions. The user running `hivemind-mic-sat` must be in the `audio` group:
   ```bash
   sudo usermod -aG audio $USER
   ```

---

## Audio is streaming but the hive does not process it

**Symptom:** You see `Speech start, initiating audio transmission` in the log but never `UTTERANCE: ...`.

The server is missing [hivemind-audio-binary-protocol](https://github.com/JarbasHiveMind/hivemind-audio-binary-protocol). The default `hivemind-core` does not include STT/TTS/wakeword processing. Install `hivemind-audio-binary-protocol` on the server and restart `hivemind-core`.

---

## No TTS playback (no audio output)

1. Test speakers independently:
   ```bash
   speaker-test -t wav -c 2
   ```
2. Check that `ovos-audio` is installed. It ships with `requirements.txt`, so it should be present.
3. If ALSA reports `Device or resource busy`, another process holds the audio device. Check with:
   ```bash
   fuser /dev/snd/*
   ```
4. Check the log for `TTSHandler` messages:
   - `Received TTS: <filename>` means the satellite received audio and wrote it to `/tmp/`.
   - If this line is absent, the hive did not send TTS audio back. Check the server-side TTS configuration.
5. Verify the `speak:synth` round-trip: the satellite sends `speak:synth` to the hive, which should respond with a binary TTS payload. If the hive TTS plugin is not configured server-side, no audio comes back.

---

## TTS received but not played (stuttering or silent playback)

- The `PlaybackThread` writes received TTS to `/tmp/<hash>.wav`. Check that `/tmp` is writable and has free space.
- If you use a USB audio dongle, confirm ALSA recognizes it as a playback device (`aplay -l`).

---

## VAD triggers too eagerly or not at all

- Too eager (constant streaming): try a more selective VAD plugin (for example `ovos-vad-plugin-silero`) or tune the VAD aggressiveness in `mycroft.conf`.
- Not triggering (no `Speech start` log lines): check microphone levels with `alsamixer` and raise input gain if needed. Try `ovos-vad-plugin-webrtcvad`, which can be more sensitive.

---

## `mycroft.audio.play_sound` sound not found

The satellite resolves `snd/<name>` URIs against its bundled resource directory. Only the three bundled files (`acknowledge.mp3`, `error.mp3`, `start_listening.wav`) are available. Custom sound URIs must be absolute paths accessible on the satellite filesystem.

---

## Diagnosing with verbose logging

Set the log level to `DEBUG` in `mycroft.conf`:

```json
{
  "log_level": "DEBUG"
}
```

Or run with the environment variable:

```bash
OVOS_LOG_LEVEL=DEBUG hivemind-mic-sat
```

---

## PHAL not starting

`PHAL` is optional. If `ovos-PHAL` is not installed, the satellite logs:

```
PHAL is not available
```

and continues without it. This is not an error. Install `ovos-PHAL` only if you need hardware plugin support.

---
[← Testing](testing.md) · [Home](index.md)
