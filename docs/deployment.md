# Deployment

---

## systemd service

Create `/etc/systemd/system/hivemind-mic-sat.service`:

```ini
[Unit]
Description=HiveMind Microphone Satellite
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
User=pi
ExecStart=/home/pi/.local/bin/hivemind-mic-sat
Restart=on-failure
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Adjust `User` and the `ExecStart` path to match your system. Find the installed binary:

```bash
which hivemind-mic-sat
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hivemind-mic-sat
sudo systemctl start hivemind-mic-sat
```

View logs:

```bash
journalctl -u hivemind-mic-sat -f
```

---

## Passing credentials to the service

**Option 1: identity file (recommended):** run `hivemind-client set-identity ...` as the service user before you start the service. The satellite reads the file automatically.

**Option 2: environment variables in the unit:**

```ini
[Service]
Environment=HM_KEY=abc123
Environment=HM_PASSWORD=secret
Environment=HM_HOST=192.168.1.10
ExecStart=/home/pi/.local/bin/hivemind-mic-sat --key ${HM_KEY} --password ${HM_PASSWORD} --host ${HM_HOST}
```

Or use `EnvironmentFile=/etc/hivemind-mic-sat.env` to keep secrets out of the unit file.

---

## Raspberry Pi Zero notes

The Raspberry Pi Zero, and the Zero 2 W, are the target hardware for this satellite.

### Recommended OS

Raspberry Pi OS Lite (64-bit for Zero 2 W; 32-bit for Zero W). Install Python 3.10 or later through the official packages or the `deadsnakes` PPA.

### Audio hardware

The Pi Zero has no built-in audio output. Common options:

| Option | Notes |
|---|---|
| USB audio dongle | Cheapest; plug-and-play |
| I2S DAC HAT (for example pHAT DAC, IQaudio) | Better quality; requires a device tree overlay |
| USB microphone + speaker combo | Single device, simplest wiring |
| ReSpeaker 2-mic HAT | Microphone array, built-in speaker output |

Identify ALSA devices after you connect hardware:

```bash
arecord -l   # input devices
aplay -l     # output devices
```

Set the correct device index in `mycroft.conf` (see [configuration.md](configuration.md)).

### ALSA default device

If the USB audio device is not the default, either configure it in `mycroft.conf` or create `/etc/asound.conf`:

```
defaults.pcm.card 1
defaults.ctl.card 1
```

Replace `1` with the card number from `arecord -l`.

### Performance tips

- Use `ovos-vad-plugin-webrtcvad` instead of Silero on a Zero W to use less CPU.
- Disable unnecessary services on the Pi to free RAM.
- Avoid running a desktop environment on the satellite.
- The satellite uses roughly 40-80 MB RAM under typical load (mic + VAD + WebSocket client).

### Network

Wi-Fi works on the Pi Zero W and Zero 2 W. For latency-sensitive deployments, a USB-to-Ethernet adapter is more reliable.

---

## Autostart without systemd (user session)

Add to `~/.bashrc` or `~/.profile` for single-user systems:

```bash
hivemind-mic-sat &
```

Or use a cron `@reboot` entry:

```bash
crontab -e
# add:
@reboot /home/pi/.local/bin/hivemind-mic-sat >> /home/pi/mic-sat.log 2>&1
```

---

## Docker

A minimal Dockerfile:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y alsa-utils libportaudio2 && rm -rf /var/lib/apt/lists/*

RUN pip install hivemind-mic-satellite ovos-microphone-plugin-alsa ovos-vad-plugin-silero

COPY mycroft.conf /root/.config/mycroft/mycroft.conf

CMD ["hivemind-mic-sat", "--host", "host.docker.internal"]
```

Note: audio access inside Docker requires ALSA device passthrough (`--device /dev/snd`).

---
[← Architecture](architecture.md) · [Home](index.md) · [Testing →](testing.md)
