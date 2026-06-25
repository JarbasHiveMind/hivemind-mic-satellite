# Dependencies

All dependency policy lives in `pyproject.toml`; there is no `requirements.txt`,
`setup.py`, or `MANIFEST.in`. Packaged sound assets ship via
`[tool.setuptools.package-data]`.

## Runtime dependencies

| Package | Constraint | Role |
|---|---|---|
| `click` | — | CLI entrypoint (`hivemind-mic-sat`) |
| `pybase64` | — | Decode base64 TTS audio responses |
| `ovos-bus-client` | `>=2.0.0a3,<3.0.0` | OVOS message bus / `Message` / `Session` |
| `ovos-plugin-manager` | `>=2.4.1a1,<3.0.0` | Microphone + VAD plugin factories |
| `ovos-audio` | `>=1.2.3a1,<2.0.0` | `PlaybackThread` + optional `AudioService` |
| `hivemind-bus-client` | `>=0.9.2a1,<1.0.0` | Encrypted HiveMind bus to the hive |

### Why the pre-release floors (and the bus-client 2.x story)

`ovos-bus-client` 2.x support exists **only in the OVOS pre-releases**: the
latest *stable* `ovos-audio` (1.2.0) and `ovos-plugin-manager` (2.2.0) still cap
`ovos-bus-client<2.0.0`, while their alphas (`ovos-audio>=1.2.3a1`,
`ovos-plugin-manager>=2.4.1a1`) widen the cap to `<3.0.0`. To land on the modern
2.x bus-client stack the floors are pinned at those alphas. A pre-release
**min-version pin is enough** for `uv`/`pip` to select the 2.x-compatible
versions — `--pre` / `pre_install_pip` is never used.

The satellite needs `ovos-audio` (playback) and `ovos-plugin-manager` (mic/VAD)
at runtime, so this is the binding constraint: only because those OVOS alphas now
allow `ovos-bus-client<3.0.0` can the satellite ride the HiveMind 2.x bus stack
(`hivemind-bus-client>=0.9.2a1`, `hivemind-core>=4.6.2a1`).

## Test / e2e dependencies (`[e2e]` extra)

The `e2e` extra adds the in-process hub + harness used by `tests/e2e/`:

| Package | Constraint | Role |
|---|---|---|
| `pytest`, `pytest-timeout` | — | Test runner |
| `hivescope` | `>=0.5.2a1` | In-process hub + loopback WebSocket + assertions |
| `hivemind-core` | `>=4.6.2a1` | Real hub master booted in-process |
| `hivemind-ovos-agent-plugin` | `>=0.3.1a1` | Hub agent protocol / policy chain |
| `hivemind-plugin-manager` | `>=0.8.0a1` | Hub protocol plugin manager |

`hivemind-core`'s own transitive pre-release floors (`json-database`,
`hivemind-sqlite-database`, `hivemind-json-db-plugin`, `hivemind-websocket-protocol`,
`ovos-utils`, `ovos-workshop`) are restated in the `e2e` extra so the resolver
picks those alphas without `--pre`.

A `test` alias (`hivemind-mic-satellite[e2e]`) is kept for shared-CI
compatibility.

## Resolving locally

```bash
uv pip install -e .[e2e]
```
