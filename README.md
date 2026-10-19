# Kohler DTV+ controller replacement

**Disclaimer:** I am not associated with Kohler in any way. This is an independent
project and is not sponsored, endorsed, or supported by Kohler.

Reverse engineering the K-99695D-NA controller interfaces for an ESP32/ESPHome
replacement. Bench hardware includes an original display, amplifier and a
K-682-K valve with a stuck-stepper fault. Valve operation is not yet implemented.

## Protocol specifications

- [RJ45 system protocol](docs/protocols/system-bus.md): electrical observations,
  UART, framing, discovery, display messages and amplifier messages.
- [RJ11 valve protocol](docs/protocols/valve-bus.md): framing, startup, status and
  correlated identification/calibration fields.

Specifications describe the current findings and explicitly identify unknowns.
They are separate from experiment logs and future integrations.

## Investigation and design

- [System bus investigation history](docs/investigation/system-bus-notes.md)
- [Valve investigation history](docs/investigation/valve-bus-notes.md)
- [Network maintenance investigation](docs/investigation/network-maintenance.md)
- [Replacement controller design and roadmap](docs/design/controller.md)
- [Alternative display research](docs/design/replacement-displays.md)

The historical logs retain superseded hypotheses and unsuccessful experiments.
Use the protocol specifications for current field interpretations.

## Repository layout

| Location | Contents |
| --- | --- |
| `docs/protocols/` | Current wire protocol specifications |
| `docs/investigation/` | Experimental history, reasoning, rejected interpretations |
| `docs/design/` | Replacement hardware, integrations and research decisions |
| `captures/system/<session>/` | RJ45 recordings, sidecars, decoded packets and session analyses |
| `captures/valve/<session>/` | RJ11 recordings and analyses |
| `captures/network/` | Controller web readbacks and Ethernet evidence |
| `captures/reports/` | Comparisons spanning multiple sessions |
| `research/controller-web/` | Saved original controller HTML and JavaScript |
| `research/display-fit/` | Manufacturer documents, extracted text and drawings |
| `tools/` | Capture, decoding and comparison tools |
| `tools/network/` | Historical macOS DHCP setup; manual operation only |
| `tests/` | Decoder tests |

## Evidence retention

Decoded packets, metadata, event annotations, analyses, CSV captures and research
files are versioned. Original waveform and packet-capture bytes are also
versioned as lossless `.f64.xz` and `.pcap.xz` archives beside their sidecars.
The 54 archives total 812 MB versus 10.13 GB uncompressed (about 92% smaller).
The largest individual archive is 66.1 MB. Uncompressed local copies remain
ignored by Git.

[captures/raw-inventory.json](captures/raw-inventory.json) records the original
paths, sizes and SHA-256 hashes. The companion
[captures/archive-inventory.json](captures/archive-inventory.json) records archive
paths, sizes and hashes. Every archive was fully decompressed and checked against
the original SHA-256 before committing. No samples were quantized, downsampled,
or discarded for storage.

Historical evidence identifiers and JSON payloads are preserved.
[captures/path-map.json](captures/path-map.json) maps former locations to current
paths. Bare capture filenames in old notes are evidence identifiers rather than
root-relative paths. Existing manifests retain their original segment identifiers;
the tools resolve them through this mapping.

## Running tools

Python 3 standard library; capture additionally requires the Digilent WaveForms
SDK. The recorder currently loads the macOS SDK from `/Applications/WaveForms.app`.
Analysis does not require attached hardware. Python's standard-library LZMA
support reads XZ archives automatically when an uncompressed waveform is absent.
For seekable decoding, one recording is unpacked to a temporary directory and
removed afterward, including on errors; allow disk space for its original size.
An existing local uncompressed copy is preferred. Commands run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 tools/compare_display.py
python3 tools/compare_display_capabilities.py
python3 tools/compare_valve_startup.py valve-startup-03 valve-startup-04
python3 tools/display_protocol.py display-settings-01
python3 tools/analyze_valve_uart.py valve-startup-04-part-000 --parity odd
```

To recreate or verify the archives against the original inventory:

```sh
python3 tools/archive_raw.py
```

Archive creation uses `xz` with four threads when installed, otherwise Python's
standard-library LZMA compressor. Packet-capture archives can be unpacked with
`xz -dk <capture>.pcap.xz` for use in Wireshark.

Analysis accepts historical capture identifiers or explicit paths. Per-session
outputs are written beside the input; cross-session reports go to
`captures/reports/`. Analysis tools can regenerate derived JSON; raw recordings
are not modified. Run the following only after probes and physical actions have
been coordinated:

```sh
python3 tools/capture_resilient.py experiment-name --bus display --duration 300
```

New captures go to `captures/system/experiment-name/` (`captures/valve/` for
`--bus valve`). The legacy `display` bus option means RJ45 terminals 3/6; it is
also used when probing the amplifier. The recorder does not identify which
peripheral is physically connected. Stop by writing the session's
`<name>-stop.json` with `{"stop_at_unix": <unix timestamp>}`.

The earlier `capture_action.py`, `capture_idle.py`, `capture_main.py` and
`capture_settings_gated.py` are fixed-session historical tools. Use
`capture_resilient.py` for new recordings.
