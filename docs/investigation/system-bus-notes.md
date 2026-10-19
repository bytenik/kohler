# System bus investigation history

Historical experiment log. Interpretations may be superseded later in this file.
Current findings are consolidated in `../protocols/`; capture identifiers resolve
through `captures/path-map.json` from the repository root.

Last updated: 2026-10-18

## Scope

The RJ45 system interface connects the controller to displays and other accessories, including music and steam equipment. Captured electrical and protocol evidence now includes a display connection and a DTV+ speaker amplifier connection. Music-module and steam connectivity are reported system capabilities; neither has been independently captured. Different baud rates and packet variants at the display and amplifier favor separate links, but shared wiring, switching, and port circuitry have not been independently traced.

The system bus is distinct from both the [RJ11 valve bus](../protocols/valve-bus.md) and the controller's dedicated Ethernet network port. Overall hardware, replacement objectives, and maintenance Ethernet notes are in [PROTOCOL.md](../../README.md).

Existing `display-*` capture filenames and decoder labels identify the peripheral and measurement point. They do not establish that the interface or packet format is exclusive to displays. The speaker amplifier has a related framing/checksum scheme with a different baud rate and packet layout, documented below. Music and steam packet types, addresses, and electrical compatibility have not been captured independently.

## Replacement objective

Replace the K-99695D-NA with an ESP32-based controller, preferably integrated with ESPHome, while operating the existing display and responding to its user interactions. The display investigation remains active until a controller emulator can initialize it, supply the state/content it needs, and process its events. Packet framing alone is not sufficient.

Immediate milestone: a display-only emulator tested with the valve disconnected. Required evidence includes startup/discovery, addressing, initialization/configuration, polling, display updates, user events, timeouts, and reconnect behavior. The physical display transmit/receive direction and identities of address fields remain to be established. The valve bus remains a separate protocol investigation, not a substitute for finishing display support.

## Target configuration and virtual chromatherapy

The replacement target includes two displays, one valve on the separate valve interface, steam, and virtual chromatherapy. The target music backend is the existing bathroom Sonos through Home Assistant. Speaker-amplifier behavior is documented from the connected spare amplifier as a reference, rather than a required physical replacement-system link. Two-display synchronization and steam traffic remain uncaptured.

### Chromatherapy evidence from the original controller web source

The saved web application contains separate paths for ordinary room lighting and chromatherapy:

- `network/controller-settings.js:2228`: chromatherapy settings appear when `rainpanel_installed` or `rainpanel2_installed` is true.
- The overall Lighting tab is enabled by either rain-panel flag or `bridge_installed`. The bridge alone is a separate room-lighting capability.
- `network/controller-values.js:74`: web setting IDs 79, 80, 81 and 82 represent rain-panel fade speed, brightness, white color and effect speed. These are **web API IDs, not established system-bus keys**.
- The saved values JSON reports `rain_fade`, `rain_brightness`, `rain_white` and `rain_speed`; both rain-panel presence flags are currently false.
- The settings script also references chromatherapy experience and color option labels. These references establish web application vocabulary, not display command encodings or proof that every option is present in this display firmware.

Kohler's [DTV+ user guide, page 37](https://resources.kohler.com/webassets/kpna/catalog/pdf/en/1241234_5.pdf) describes WaterTile Ambient Rain lighting defaults and requires a connected panel for the original controller to expose that settings page. The [K-98741-K1 product page](https://www.kohler.com/en/products/showers/shop-shower-trims-valves/watertile-ambient-rain-overhead-rain-shower-for-dtv-98741-k1) identifies integrated chromatherapy with solid colors and effects. This is the documented candidate for the virtual feature; an exact historical accessory model has not been specified.

### Replacement implementation and remaining evidence

The replacement controller can maintain a virtual chromatherapy device internally and map display events to its state, then optionally drive a generic light. This design does not require the original rain panel's wire protocol. The display-facing availability/configuration fields, event keys, color/effect values and state responses must first be established.

Capability comparison now identifies key `25 13` as an accessory capability/status candidate; see the historical amplifier comparison below. First capture a controlled amplifier disconnect/reconnect on the display link. Then bring up the spare display against a controller emulator with the real valve disconnected, reproduce the captured baseline configuration, and vary candidate capability/state responses in controlled steps. Observe whether lighting controls become available, then capture color, brightness, on/off and effect actions in grouped recordings. Retain the original baseline for comparison. Merely unhiding the browser's Lighting tab does not enable the feature on the physical display or establish controller support for an absent panel.

Steam remains a physical accessory investigation. Its electrical compatibility and operating baud rate must be measured independently rather than inferred from the display or amplifier. Two displays require independent link servicing and a shared controller state model unless further hardware evidence establishes a different topology.

## Evidence levels

- **Observed:** directly measured or validated against saved samples.
- **Hypothesis:** consistent with captures, but not independently established.
- **Unknown:** not investigated or insufficient evidence.

## Electrical observations at the display connection

Measurements were taken with the original controller and display connected and operating.

| Black meter lead | Red meter lead | DC voltage |
| --- | --- | ---: |
| 1 | 2 | −0.293 V |
| 1 | 3 | +0.015 V |
| 1 | 4 | +10.22 V |
| 1 | 5 | +10.22 V |
| 1 | 6 | −0.243 V |
| 1 | 7 | −1.775 V |
| 1 | 8 | −1.775 V |
| 7 | 4 | +11.99 V |
| 4 | 5 | 0.000 V |
| 7 | 8 | 0.000 V |
| 7 | 1 | +1.777 V |
| 7 | 2 | +1.483 V |
| 7 | 3 | +1.792 V |
| 7 | 6 | Approximately +1.512 V, fluctuating around 1.45–1.55 V |

**Hypothesis:** pins 4/5 supply approximately +12 V and pins 7/8 provide its return. Equal DC voltages do not by themselves prove that contacts are directly connected internally.

**Observed:** with AD3 Scope 1+ on pin 3 and Scope 1− on pin 6, active signaling has plateaus around −1.7 V and +2.0 V. Between bursts, the differential voltage can return to approximately +0.3 V.

**Hypothesis:** an RS-485/RS-422-type physical interface. The transceiver type, termination, topology, and electrical standard remain unknown. Both apparent address directions occur on this one pair, favoring a shared bidirectional bus over a dedicated one-way RS-422 link. The physical transmitter for each message has not been established.

The captured signaling is consistent with asynchronous serial, not normal 10/100 Ethernet signaling. The RJ45 connector and its lights are not evidence of Ethernet compatibility. Do not connect this powered component port to network equipment based on these observations.

Pins 1/2 remain unclassified. Earlier trigger attempts did not detect activity at the selected thresholds; they do not establish that the pair is unused.

## Serial framing observed at the display connection

**Observed:** 115200 baud, eight data bits, no parity, one stop bit is a consistent decoding model across multiple captures.

- Measurement polarity: `V(pin 3) − V(pin 6)`.
- Positive differential voltage decodes as logic 1; negative as logic 0.
- UART data bits are decoded least-significant bit first.
- Short pulses in the initial high-rate capture measured 8.68–8.82 µs; nominal 115200-baud bit duration is 8.6806 µs.
- Trials at 57600 and 230400 baud produced frequent framing failures. Inverted polarity fit worse.
- The complete 20-second open/close capture decoded 11,487 bytes with no UART framing errors.

This validates a useful framing model; it does not identify a standard application protocol such as Modbus.

## Packet framing and checksum observed at the display connection

Observed wire structure:

```text
88  [escaped body and checksum]  55
```

- `88`: observed start delimiter.
- `55`: observed end delimiter.
- `AA 88`: observed encoding of a literal `88` inside the packet.
- `AA AA`: observed encoding of a literal `AA` inside the packet.
- `AA 55`: observed encoding of a literal `55`, validated in startup identity messages containing the ASCII text `un-named UI`.

The penultimate **unescaped** byte is consistent with an additive checksum. Including the initial `88` and the checksum, but excluding the final delimiter `55`:

```text
sum(unescaped_packet_without_final_55) & 0xFF == 0
checksum = (-sum(unescaped_bytes_before_checksum)) & 0xFF
```

Examples without escaped bytes:

```text
88 03 00 30 45 55
88 00 03 31 00 44 55
88 03 00 34 01 02 02 31 0B 55
```

In the first example, `88 + 03 + 00 + 30 + 45 = 100` in hexadecimal.

Escape handling is necessary: two packets in the open/close capture failed the checksum when calculated over wire bytes, then passed after unescaping. All 990 complete packet groups in that capture pass after unescaping.

The initial analysis grouped bytes using an inter-start gap greater than 120 µs. That was an analysis heuristic, not a protocol requirement. The current parser uses delimiters and escape rules, records malformed/truncated input separately, and validates the unescaped checksum. It does not require a gap between packets.

## Observed fields and exchanges at the display connection

Offsets below are zero-based indices into the **unescaped** packet, including the initial `88`.

| Offset | Observation | Interpretation |
| --- | --- | --- |
| 0 | `88` | Start delimiter |
| 1–2 | Commonly `03 00` or `00 03`; discovery also uses `FF` | Candidate destination/source fields, with controller `00` and assigned peripheral `03`, based on reconnect capture 12; physical direction not independently traced |
| 3 | Observed `30`, `31`, `34` | Message-type hypothesis; meanings unconfirmed |
| 4 onward | Variable contents | Message-specific fields |
| Penultimate | Additive checksum | Observed |
| Final | `55` | End delimiter |

For all 666 checksum-valid `34` messages across recordings 01–03, **unescaped total packet length equals `packet[5] + 8`**. These steady-state messages have offset 4 equal to `01`, so offset 5 is a length-field candidate for that subtype only. Startup introduces subtype `00`, whose single observed example instead satisfies total length = `packet[6] + 8`. No universal type `34` length rule is established. This rule has not been established for `30` or `31` messages.

The six-byte message `88 03 00 30 45 55` repeats approximately every 50 ms (20 Hz). Messages beginning `88 00 03 31` commonly follow, and messages beginning `88 03 00 34` occur in the same exchanges. Poll/reply/data roles are hypotheses pending further timing and device-direction checks.

Fields containing `20 0E` and `20 1B` appeared in the later portions of both Settings-action recordings. Earlier traffic included fields containing `20 7F` and `20 7C`. These are candidate associations with display state; no field has been established as an “open Settings” or “close Settings” command. Screen changes may alter polling rather than send a dedicated navigation command.

## Display-connection capture inventory

All captures in this table observe breakout pins 3/6 with the original devices operating.

| Files | Conditions | Result and limitations |
| --- | --- | --- |
| `display-uart-test.csv` | Initial short capture, 14.286 MS/s | 11 complete UART frames; one complete six-byte packet and a partial subsequent exchange |
| `display-idle-01.csv` through `display-idle-03.csv` | Three idle captures, 2 MS/s | Two active captures containing three complete messages; third quiet |
| `display-settings-01.f64`, `.json`, `-decoded.json` | 20 seconds, 1 MS/s; no coordinated user action | **Idle baseline despite the filename and original action label.** 20,000,000 samples; no reported loss/corruption; 1,006 packet groups, all checksum-valid after unescaping |
| `display-settings-02.f64`, `.json`, `-decoded.json` | Settings opened during recording, 1 MS/s | 27.877898-second retained prefix before reported loss of 131,071 samples; 1,384 checksum-valid groups after unescaping; first two groups are incomplete/invalid; two UART framing errors |
| `display-settings-03.f64`, `.json`, `-decoded.json` | Open Settings, wait approximately five seconds, return to main screen | Full 20 seconds at 1 MS/s; no reported loss/corruption; 990 groups, all checksum-valid after unescaping; no UART framing errors. Action times were not electronically marked |

The `.f64` recordings contain native float64 voltage samples. Their JSON sidecars record sample rate and count. The `started_unix` value, where present, is a host timestamp near acquisition startup, not a hardware-synchronized event marker.

Legacy `-decoded.json` files retain `hex` wire bytes plus separately added `unescaped_hex` and `checksum_valid_after_unescaping` fields. The reproducible parser outputs are now `-packets.json`: `wire_hex` is transmitted bytes, `hex` is unescaped bytes, and `checksum_valid` applies to unescaped bytes. The legacy decoder remains for comparison; use `display_protocol.py` for current analysis.

## Measurement limitations

Use grouped captures for several ordered actions separated by pauses, retaining each action order and any reported screen transitions. Stop on the completion acknowledgment without an additional fixed recording tail. Cue and acknowledgment timestamps remain distinct from physical touch times.

- The AD3 differential inputs are not galvanically isolated and have limits relative to instrument/USB ground as well as differential limits.
- High-impedance measurements showed shared 60 Hz voltage relative to USB ground. Its magnitude changed with measurement loading. This does not establish a direct mains connection or available current.
- Two BNC probes with ground clips disconnected produced substantial shared pickup. Narrow-range input clipping created false pulses in the subtraction trace. Those traces are excluded from protocol evidence.
- The usable captures use the loose-wire differential input, 1× software attenuation, wide analog input range, and no AD3 GND connection to the bus. A plausible waveform alone does not validate common-mode compliance under every operating condition.
- No commands have been injected or replayed. All protocol evidence is from passive observation.

## Display port-change test (2026-10-18)

The display was moved to another equivalent controller port, with the RJ45 breakout remaining inline. Exact original/new port labels were not recorded. Capture `display-port-change-08` was acquired after the move, using the existing differential pin 3/6 setup. This records steady traffic, not the move or address negotiation itself.

One uninterrupted segment decoded into 598 complete checksum-valid packets, with zero UART framing errors or packet issues: 274 type `30`, 274 type `31`, and 50 type `34`. All 50 type `34` length checks pass. Median poll interval remains 50 ms.

Address-like fields remain unchanged: `03 00` in 324 packets and `00 03` in 274. No additional address pair appears. Analysis: `display-port-change-08-analysis.json`; decoded packets: `display-port-change-08-part-000-packets.json`.

**Conclusion:** moving between the two tested ports did not change the observed address fields. This argues against a distinct fixed address for each of those physical ports. It does not distinguish a shared electrical bus, isolated ports reusing the same addresses, device-role addresses, or an address retained/reassigned to the same value. A second simultaneous peripheral or cross-port electrical measurements are still needed to establish bus topology and address allocation.

### After power cycle

Following a reported power cycle on the new port, capture `display-port-restart-09` contains 477 complete checksum-valid packets and zero UART framing errors. Address pairs remain `03 00` (271 packets) and `00 03` (206 packets). Types: 206 polls (`30`), 206 replies (`31`), and 65 data messages (`34`), with all 65 length checks passing. Median poll interval remains 50 ms. Two bytes outside complete packets are recorded as boundary issues. Acquisition began after the reported power cycle, so this confirms post-restart addressing but does not capture the startup/address-assignment exchange. Analysis: `display-port-restart-09-analysis.json`.

## Display content: stored menus and supplied strings

Analysis: `analyze_display_content.py`, results in `display-content-analysis.json`. This inventories printable ASCII runs of at least five bytes in checksum/framing-valid packets; printable numeric fields are not automatically classified as text. It does not detect arbitrary encodings or reconstruct text split across packets.

**Observed:** startup capture `display-startup-07-part-001` contains literal null-terminated strings `Preset 1` through `Preset 6` in presumed controller-to-display type `34 01` messages. Each name appears three times. Candidate keys are `22 01` through `22 06`, respectively. Example at capture-relative 26.643198 s and 26.647172 s:

```text
88 00 03 31 02 04 22 01 00 1B 55
88 03 00 34 01 0C 02 22 01 50 72 65 73 65 74 20 31 00 4B 55
                           P  r  e  s  e  t     1 NUL
```

These are candidate preset-name fields. Editable-name behavior and display rendering remain to be confirmed by changing one name and observing its packet value. The query's format byte `04` may indicate a string, but that interpretation is unconfirmed.

**Observed:** the only recognizable textual content found by this scan is `un-named UI` in the startup identity exchange and the six preset names. Settings captures 01–05 and main-after-close 06 contain no recognizable menu-label text by this method. Maximum validated unescaped packet sizes are 38 bytes in those menu recordings and 56 bytes across startup parts. No graphics transfer or menu description has been identified.

**Working hypothesis:** the display implements menu layouts, fixed labels, and navigation locally, and requests controller state/configuration using keys relevant to the active screen. The controller supplies at least some names as strings. Existing evidence supports this model but does not rule out encoded labels, cached resources, or other traffic on unclassified pins 1/2. Captured startup includes a transfer interruption, so it is not a complete byte-for-byte boot record.

Spare-system experiments do not require a working valve: compare Settings/About navigation, change a display-local preference such as units if available, or rename one preset if the UI permits it. Capture one action at a time, record the visible before/after state, and repeat/reverse the action to distinguish a command from incidental polling. A display restart with its data pair isolated can further test which menus exist locally; preserve the power conductors and prepare the exact wiring procedure before this experiment.


## Parser validation and exchange analysis (2026-10-18)

Implementation: `display_protocol.py`; validation: `test_display_protocol.py`; comparison: `compare_display.py`.

```sh
python3 -m unittest test_display_protocol.py
python3 display_protocol.py display-settings-01 display-settings-02 display-settings-03
python3 compare_display.py
```

The parser only decodes the RJ45 display bus. It sends no traffic and contains no valve protocol assumptions. Synthetic validation covers adjacent packets without timing gaps, captured escaped checksum bytes, checksum corruption, UART error propagation, and recovery from partial input.

| Capture | Complete packets | Checksum/framing-valid packets | `30` | `31` | `34` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Idle 01 | 1,006 | 1,006 | 400 | 400 | 206 |
| Settings 02 retained prefix | 1,384 | 1,384 | 557 | 557 | 270 |
| Settings open/close 03 | 990 | 990 | 400 | 400 | 190 |

All 3,380 complete packets validate. Capture 02 also contains 24 decoded bytes outside a complete packet at its leading boundary; these are retained as issues, not interpreted as complete messages. Its two UART framing errors occur outside the accepted complete packets. The other two captures have no framing errors or packet-boundary issues.

### Exchange structure

Observed sequence:

```text
fields 03 00, type 30: short poll
fields 00 03, type 31: reply, sometimes carrying more content
fields 03 00, type 34: optional subsequent message
```

The field order above preserves packet bytes rather than assigning source/destination order. The median poll interval is 50.000 ms. Every observed complete `30` poll is followed by a `31` message. Median gap from the last `30` UART frame's nominal end to the first `31` frame is approximately 0.19–0.24 ms across captures. For adjacent `31`/`34` messages, the median analogous gap is approximately 2.47 ms. These are observed timings, not required timeout values.

For all 560 adjacent `31`/`34` pairs where `31` has offset 4 equal to `02`, **offsets 6–7 in `31` equal offsets 7–8 in `34`**. This supports a query/reply association using a two-byte key. It does not establish the key's byte order, namespace, or semantics.

Example:

```text
88 00 03 31 02 01 20 0D 01 09 0A 55
                  ----- candidate key: 20 0D
88 03 00 34 01 04 02 20 0D 14 F9 55
                     ----- matching key: 20 0D
```

### Navigation comparison and limits

In idle capture 01, candidate keys `20 7F` and `20 7C` recur roughly every four seconds; `20 0D` appears roughly once per second. No `20 0E` or `20 1B` query occurs in that recording.

In capture 02, `20 7F`/`20 7C` appear through approximately 11.6 s; `20 0E` first appears at 15.200 s and `20 1B` follows in the next second. These latter keys then alternate approximately once per second, so each recurs about every two seconds.

In capture 03, `20 7F`/`20 7C` appear through approximately 12.0 s; `20 0E` first appears at 16.226 s and `20 1B` at 17.176 s. They continue through the end of the capture. **The recorded traffic does not demonstrate a return to the initial polling profile after closing Settings.** Action timestamps, screen state, and possible delayed background changes remain unresolved. No dedicated navigation command is assigned.

Machine-readable results: `display-analysis-summary.json` and `display-comparison.json`. Candidate keys are reported as byte sequences, not assigned register numbers or endianness.

## Timed Settings opening capture 04 (2026-10-18)

Files: `display-settings-04.f64`, `.json`, `-packets.json`, and `-events.json`.

The full 60-second recording contains 30,000,000 samples at 500 kS/s, with no reported lost/corrupted samples. Decoding produced 34,344 UART bytes with zero framing errors and 2,982 complete checksum-valid packets: 1,200 type `30`, 1,200 type `31`, and 582 type `34`. All 582 type `34` length checks pass. The lower sample rate still produced consistent UART decoding and checksums in this capture.

Host event times relative to acquisition startup:

| Event | Capture-relative time |
| --- | ---: |
| Open Settings cue recorded | 26.695 s |
| Opened acknowledgment recorded | 45.224 s |
| Acquisition ended | 60.000 s |
| Close Settings cue recorded | 77.029 s — outside capture |
| Closed acknowledgment recorded | 95.804 s — outside capture |

Cue and acknowledgment timestamps are written after processing the corresponding chat messages. They bracket an approximate action interval, not a hardware event. The intended ten-second action spacing was not achieved. **This recording covers opening Settings but does not cover closing Settings or the subsequent main screen.**

Candidate query keys `20 7F` and `20 7C` recur about every four seconds through 26.482/26.532 s. After the opening cue, `20 0E` first appears at 28.632 s and `20 1B` at 29.632 s. These alternate about once per second through the end of acquisition, with each key recurring about every two seconds. This strengthens the association between opening Settings and changing the polling profile. It still does not identify a dedicated navigation command or establish the values' semantics.

A future closing experiment needs acquisition that remains active through the closing acknowledgment and a measured post-close interval, rather than relying on chat cue delivery to fit within a fixed short acquisition window.

## Event-controlled attempt 05 (2026-10-18)

The retained prefix contains 52.490598 seconds at 500 kS/s, ending before a reported chunk with 885 corrupted samples. That affected chunk was not saved. All 2,621 complete packets in the retained portion validate; 30,596 UART bytes have no framing errors.

Startup timing is approximated from recording-file creation time because the original recorder wrote acquisition metadata only on successful completion. Relative to that approximation, the opening cue was recorded at 26.468 s, opening acknowledgment at 45.909 s, closing cue at 73.978 s, and closing acknowledgment at 94.550 s. The capture therefore does not cover closing Settings, despite the intended acknowledgment-controlled stop.

`capture_resilient.py` adds separate contiguous files and an interruption manifest rather than joining samples across reported transfer errors. It discards affected chunks and continues into a new segment. This recovery path has been syntax-checked but has not yet been validated against an induced hardware transfer error. Segment host timestamps are approximate, not a substitute for synchronized event markers.

## Main screen after closing Settings: capture 06 (2026-10-18)

Files: `display-main-after-close-06.f64`, `.json`, and `-packets.json`.

A separate passive recording after the closing acknowledgment completed 20 seconds at 500 kS/s with no reported loss/corruption. All 1,005 complete packets validate, with 12,037 UART bytes and no framing errors. There are 400 type `30`, 400 type `31`, and 205 type `34` packets; all 205 type `34` length checks pass.

The polling profile matches the original main-screen baseline: `20 7F` and `20 7C` each appear five times in 20 seconds, `20 0D` appears 20 times, and `20 0E`/`20 1B` do not appear. Combined with the opening captures, this supports a display-state-dependent polling profile that eventually returns after closing Settings. The closing transition and exact reversion delay remain unmeasured.


## Next capture: display initialization

Capture name: `display-startup-07`. Keep Scope 1+ on breakout pin 3 and Scope 1− on pin 6, with all AD3 GND leads disconnected. Start recording before cycling the original controller's power so that both controller and controller-powered display startup are observed. Keep the original communication wiring connected. The shower must be off before cycling power. Record a controller-power-cycle event and a display-ready acknowledgment, then retain at least 30 seconds after the display becomes ready.

Use `capture_resilient.py display-startup-07` to retain separate contiguous segments across transfer errors. Parse each segment independently; no frames may span an interruption. Compare initial messages against steady-state message types and candidate keys before assigning initialization semantics.


## Startup handshake: capture 07 (2026-10-18)

The original controller was power-cycled with the RJ45 wiring and differential probes unchanged. Files use prefix `display-startup-07`; the manifest describes two contiguous segments and one discarded transfer interruption. Combined retained duration is approximately 168.91 seconds at 500 kS/s. The interruption occurred after the handshake and was not bridged during decoding. Segment 000 has 1,749 complete checksum-valid packets; segment 001 has 4,078. Segment 000 also contains 78 decoded bytes outside packets, including 48 framing errors around startup/power interruption; all accepted complete packets validate. Segment 001 has no framing errors or boundary issues.

On segment 000's local sample timeline, ordinary traffic ends near 14.376 s and resumes at 61.318 s. The first post-quiet exchange is:

| Time (s) | Address fields | Type | Observation |
| --- | --- | --- | --- |
| 61.318100 | `03 00` | `38` | Short initial request |
| 61.319124 | `00 03` | `39` | Reply with 12-byte-length candidate field and repeated `FF` values |
| 61.368086 | `03 00` | `33` | Short subsequent request |
| 61.369084 | `00 03` | `32` | Reply containing ASCII `un-named UI` |
| 61.418102 | `03 00` | `34`, subtype `00` | Initialization/configuration candidate, similar identity data with one changed byte |
| 61.421802 | `00 03` | `35` | Short acknowledgment candidate |
| 61.468102 | `03 00` | `30` | Regular polling begins |

Unescaped first messages:

```text
88 03 00 38 3D 55
88 00 03 39 00 0C 00 00 03 00 FF FF FF FF FF FF FF FF 35 55
88 03 00 33 42 55
88 00 03 32 00 1F 00 64 01 00 75 6E 2D 6E 61 6D 65 64 20 55 49 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC 55
88 03 00 34 00 00 1F 00 64 01 01 75 6E 2D 6E 61 6D 65 64 20 55 49 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC FD 55
88 00 03 35 40 55
```

The literal `55` inside the identity string is transmitted as `AA 55`, confirming that escape sequence. The startup subtype `34 00` uses a different field layout from steady-state subtype `34 01`; parsers must distinguish these before interpreting length.

**Hypothesis strengthened:** address `03` is the controller and `00` is the display, since `03` initiates the post-power-cycle request sequence. This remains an inference from one connected display, not an independently verified transmitter assignment. Types `38`/`39`, `33`/`32`, and `34`/`35` form likely request/reply pairs. The identity reply and changed field in the following initialization packet need comparison across repeat boots before assigning exact semantics.

The initial handshake starts about 47 seconds after the previous traffic ended. That interval includes the power-off period and boot time; it is not a measured protocol timeout. No replay has been attempted.

Next: verify repeatability of this handshake, compare byte changes between the `32` identity and `34 00` initialization payloads, and map the first subsequent state exchanges. Use this evidence to design a display-only controller emulator; do not replay initialization data until its variable fields and addressing are understood.

## Identity alignment and first state exchanges (2026-10-18)

Reproduce with `python3 analyze_startup.py`; machine-readable output: `display-startup-analysis.json`. All offsets below index unescaped packets.

### Identity-to-initialization comparison

The 32-byte slice `type32_packet[4:-1]` aligns with `type34_subtype00_packet[5:-2]`. Exactly one byte differs:

| Identity packet offset | Initialization packet offset | Identity value | Initialization value |
| --- | --- | --- | --- |
| 9 | 10 | `00` | `01` |

The copied slice includes the original identity checksum `EC`, which remains unchanged even though the aligned data byte changes. The initialization message has a separate outer checksum `FD`. Thus the inner copied `EC` must not automatically be recomputed as if it were the initialization packet's checksum. Whether it is treated as an opaque copied field, a nested checksum, or something else is unresolved.

The name `un-named UI` and its padding are copied unchanged. A role/enable/address-assignment interpretation for the `00`→`01` change is a hypothesis only; no bit meaning is assigned from a single boot.

### Initialization timing and state acquisition

Times relative to the first type `38` request:

- `38` request → `39` reply start: approximately 1.024 ms.
- `33` request at 49.986 ms → `32` identity reply at 50.984 ms.
- `34 00` initialization starts at 100.002 ms → `35` reply at 103.702 ms.
- First type `30` poll starts at 150.002 ms.
- Empty type `31` replies continue for approximately 3.25 seconds of polling.
- First nonempty type `31` reply starts at 3.401010 s, with candidate key `20 0D`; the matching type `34 01` follows at 3.405012 s.
- Early queries then include `21 65`, `21 0A`, `21 0B`, `24 55`, `20 63`, `24 03`, and `24 8B` before the familiar recurring state traffic.

These are one-boot observations, not mandatory delays or a complete startup specification. A controller emulator must be able to poll while receiving empty replies rather than assume state requests appear immediately after initialization.

### Nonempty type `31` patterns

In the retained initial segment, 106 adjacent nonempty `31`→`34` exchanges after the handshake divide into two observed classes based on `31` offset 4:

| Class byte | Exchanges | Candidate keys | Following response pattern |
| --- | ---: | --- | --- |
| `02` | 68 | `20 xx`, `21 xx`, `24 xx`, `25 xx` | Type `34 01` commonly echoes the two-byte key and supplies data |
| `01` | 38 | `30 xx`, `31 xx` | Type `34 01` has short payload `02 30` or `02 31` |

Examples:

```text
31 class 02, candidate key 21 65:
88 00 03 31 02 02 21 65 02 29 42 4D 55
88 03 00 34 01 05 02 21 65 00 3E 75 55

31 class 01, candidate key 30 74:
88 00 03 31 01 01 30 74 01 03 9A 55
88 03 00 34 01 02 02 30 0C 55

31 class 01, candidate key 31 1E:
88 00 03 31 01 02 31 1E 02 00 01 EF 55
88 03 00 34 01 02 02 31 0B 55
```

**Working hypothesis:** class `02` carries state-read requests, while class `01` carries writes/events that receive acknowledgments. Offset 5 may distinguish value format, and offset 8 is a value-length/count candidate. Endianness and units remain unresolved. Bytes trailing a read request must not automatically be treated as user data: some vary without a corresponding change in the returned value.

No class `01` key is assigned to a particular button or screen action yet. A minimal emulator can eventually implement the observed handshake and service known read requests, but user-event handling still requires controlled single-action captures. Before transmitting, confirm device direction and startup variability; all work so far remains passive.

## Next work

1. Correlate repeatable system-bus peripheral actions with packet changes and explicit event timing.
2. Validate source/destination fields, candidate query keys, and address allocation with additional peripherals.
3. Identify physical transmitters, investigate pins 1/2, and establish the relationship between equivalent ports.
4. Document physical connector orientation before designing replacement hardware.
5. Extend packet parsing as new message types and escapes appear; retain peripheral-specific evidence labels.

## Display and amplifier connected: capture 10 (2026-10-18)

Setup: the user connected a DTV+ speaker amplifier on another system port and retained the RJ45 breakout inline with the display. AD3 wiring was reported as Scope 1+ on 3, 1− on 6, all GND leads disconnected. Capture `system-display-amplifier-10` contains 20 seconds at 500 kS/s, with no USB loss/corruption reported. The recorder's legacy `bus:display` metadata denotes the display measurement connection; both peripherals were connected during this system-bus experiment.

The recorded differential polarity is reversed relative to earlier display captures: idle is approximately −0.26 V and negative voltage represents logical one. Plateau values in the first two seconds are approximately −1.8 V and +1.8 V. The cause of the polarity change was not established. Decoding the earlier positive-one model produced 1,701 UART errors and zero complete packets; explicit inversion yields 11,771 characters with zero UART framing errors, 963 complete packets, and no packet-boundary issues. All 963 packets pass checksum checks; all 205 type `34` messages pass their subtype length check. No physical wiring change was made to correct polarity.

| Address-like pair | Type | Count |
| --- | --- | ---: |
| `03 00` | `30` | 379 |
| `00 03` | `31` | 379 |
| `03 00` | `34` | 205 |

No additional address pair or message type appears at the display's pin 3/6 measurement point. Median poll interval remains 50 ms, but four intervals exceed 100 ms, with a maximum of approximately 377 ms. These scheduling gaps have no assigned cause.

A read-only `values.cgi` snapshot reports one interface connected and the amplifier installed/connected (`amp_installed:true`, `amp_con_string:"conn"`, `amp_version_string:"0.16"`). This establishes the controller's reported presence state alongside the user's physical connection report. Earlier configuration-page snapshots also reported the amplifier connected, so those historical presence strings alone are not an independently verified single-peripheral baseline.

**Conclusion:** this capture does not reveal amplifier exchanges on the display's observed data pair. It does not establish that all system ports are isolated, nor that address-like field `03` is the amplifier. Possible explanations include separate port links, use of pins 1/2 for another channel, or no amplifier exchange during this window. Address and topology hypotheses remain open.

Next measurement: move the passthrough breakout to the amplifier connection and capture pins 3/6 there, preserving peripheral and probe labels. Compare its traffic with the display connection; if absent, independently characterize the other candidate pair before drawing a topology conclusion. A synchronized two-channel comparison can subsequently distinguish simultaneous traffic from merely similar frames.

Reproduction: `decode_capture(Path('system-display-amplifier-10-part-000'), invert=True)` in `display_protocol.py`, or its CLI with `--invert`. Analysis is saved in `system-display-amplifier-10-analysis.json`; the controller presence snapshot is `network/system-display-amplifier-10-values.json`. The decoder supports explicit polarity without automatically guessing; its synthetic polarity test and five packet-parser tests pass.

## Amplifier connection: capture 11 (2026-10-18)

The RJ45 passthrough was moved inline with the amplifier cable, with the display and amplifier still connected to the controller. Scope 1 was reported on pins 3/6, all AD3 GND leads disconnected. Capture `system-amplifier-port-11` retains 20 seconds at 500 kS/s, with no USB loss/corruption reported. As in capture 10, the recorder's legacy `bus:display` field denotes use of the established system-interface pin setup, not the measured device identity.

**Observed:** amplifier traffic decodes at **57600 baud, 8N1**, with negative differential voltage representing one. The signal is approximately −0.12 V idle and ±2.2 V active. Decoding at the display's 115200 baud fails in both polarities. The 57600-baud inverted model yields 7,494 characters with zero UART framing errors, 114 complete packets with zero boundary issues, and valid additive checksums on all packets. All decoded characters are accounted for by complete wire packets.

### Repeating amplifier exchanges

| Address-like pair | Type | Count | Unescaped packet length |
| --- | --- | ---: | ---: |
| `03 00` | `33` | 29 | 8 |
| `00 03` | `32` | 29 | 38 |
| `03 00` | `30` | 28 | 8 |
| `00 03` | `31` | 28 | 212 |

Only four distinct packet byte sequences appear. Request-like messages alternate approximately every 350 ms, so each request type recurs approximately every 700 ms:

```text
88 03 00 33 00 1E 24 55
88 03 00 30 00 CC 79 55
```

The corresponding `32`/`31` replies contain `00 1E`/`00 CC` at offsets 4–5. Interpreting those two bytes as a big-endian count gives 30/204, respectively, equal to each reply's total unescaped length minus 8. Every one of the 57 replies satisfies this count rule. Since the 8-byte request-like messages contain the same counts but no such body, the request fields may specify the amount of response data requested; they are not literal request-body lengths. This is a separate layout from the display's steady-state type `34` packets.

The full 38-byte `32` reply is:

```text
88 00 03 32 00 1E 32 00 00 00 00 00 00 00 00 00 30 30 30 30 54 2A 53 00 00 00 00 00 00 00 00 00 00 00 00 00 62 55
```

Both reply types contain `32` at unescaped packet offset 6. That byte is decimal 50, matching `amp_volume_string:50` in the adjacent controller presence snapshot; this is a candidate volume field pending a controlled volume change. The `31` reply also contains `10` at offset 173, consistent with the reported amplifier version `0.16`, and ASCII `20131031` at offsets 174–181. The latter resembles a date, but no build-date meaning has been established. The `32` reply contains printable `0000T*S` at offsets 16–22; its meaning is unknown.

### Topology and address implications

Capture 10 at the display and capture 11 at the amplifier use the same reported physical pin pair but different baud rates and packet variants. Both contain only address-like pairs `03 00` and `00 03`. In each recording, all decoded bytes belong to valid packets at the connection's own baud rate; no interleaved traffic at the other connection's baud rate was identified. This strongly favors separate links or active port routing over one continuously shared passive data pair. The recordings are sequential rather than synchronized, so they do not prove controller wiring or rule out switching.

The reused field values argue against treating `00` and `03` as globally unique display/controller addresses. They may be role identifiers or addresses local to each link. A common framing layer can be used independently on multiple serial channels.

The physical interface remains consistent with RS-485-type differential signaling, but the transceiver standard is not confirmed. RS-485 electrical signaling is compatible with point-to-point as well as multipoint links; its presence alone does not establish shared topology.

Reproduction: `decode_capture(Path('system-amplifier-port-11-part-000'), invert=True, baud=57600)`. Decoded packets and metadata: `system-amplifier-port-11-part-000-packets.json`. Summary: `system-amplifier-port-11-analysis.json`. Baud/polarity exploration: `system-amplifier-port-11-baud-analysis.json`. The earlier 115200-baud attempt was rejected as an incorrect decode rather than interpreted as corrupt amplifier packets.

## Amplifier reconnect and discovery: capture 12 (2026-10-18)

The amplifier was disconnected while the breakout remained attached to the controller port. Acquisition began before the reconnect cue; the user then reconnected the amplifier. Scope wiring remained on the reported pins 3/6 with GND disconnected. Raw acquisition was 2 MS/s. Six USB transfer interruptions split the recording into seven parts, including three empty parts. The retained durations are 6.2018715, 0, 0.0205845, 0, 1.3583005, 0, and 31.5992725 seconds. Interruptions and discarded samples are retained in `system-amplifier-detection-12-manifest.json` and are not joined across gaps.

Baud/polarity exploration used every fourth raw sample (500 kS/s analysis) at 9600, 19200, 38400, 57600, and 115200 baud, in both polarities. Only 57600 baud, negative-voltage-one, produced valid packets. This is a finite set of 8N1 candidates, not proof against every possible rate or encoding. Parts 002 and 004 have no threshold-crossing activity. Part 000 contains 12 decoded characters, zero UART errors, and two checksum-valid packets. Part 006 contains 9,922 decoded characters, zero UART errors, 155 checksum-valid packets, and one character outside complete packets.

### Empty-port probe and reconnection

Part 000 contains only the following message, at 0.118818 and 3.188872 s:

```text
88 FF 00 05 74 55
```

The same message appears in uninterrupted part 006 at 1.682970 and 4.751438 s. There is no valid reply before the latter probe. At part-relative 4.794084 s, a new packet appears, followed by the following sequence at the same 57600-baud rate:

| Time relative to type `06` reply (ms) | Packet | Candidate role |
| --- | --- | --- |
| −42.646 | `88 FF 00 05 74 55` | Controller discovery probe |
| 0 | `88 00 FF 06 07 10 5C 55` | Unassigned-device identity reply |
| +7.340 | `88 FF 00 07 03 07 10 58 55` | Controller assigns address `03`, echoing identity bytes `07 10` |
| +17.910 | `88 00 03 35 40 55` | Acknowledgment using assigned address |
| +652.408 | `88 03 00 33 00 1E 24 55` | Normal short-block request |
| +663.694 | Type `32`, 38 bytes | Short-block reply |
| +1002.396 | `88 03 00 30 00 CC 79 55` | Normal long-block request |
| +1007.206 | Type `31`, 212 bytes | Long-block reply |
| +1352.758 | Type `34`, 38 bytes | Short-block initialization/update candidate |
| +1369.024 | `88 00 03 35 40 55` | Acknowledgment |

All these packets are contiguous within part 006 and checksum-valid. Thus USB interruptions do not cut the displayed discovery/assignment exchange. Exact physical reconnect time is not measured; the user acknowledgment follows later.

The type `34` packet copies the short-block data but changes unescaped offset 15 from `00` to `01`; following type `32` replies retain `01` at that offset. No semantic meaning is assigned to this flag. Amplifier type `34` uses the same two-byte count field as its other block messages; display-specific subtype/length checks must not be applied to it.

### Address interpretation revised by discovery

The empty-port probe establishes a likely controller-originated `FF 00` pattern. Its reply uses `00 FF`; the next message contains a new `03` in its payload, followed by acknowledgment fields `00 03` and normal `03 00`/`00 03` exchanges. Together these strongly support **destination then source**, controller address `00`, and peripheral address `FF` before assignment and `03` afterward. `FF` may be a discovery/broadcast address; only one peripheral on this link has been tested.

This supersedes the earlier tentative interpretation that the first field was the source and `03` identified the controller. Physical sender direction has not been electrically isolated, so assignments remain an evidence-based protocol model rather than an independently traced wiring fact. Identity byte `07` is a candidate amplifier class identifier and `10` matches amplifier version `0.16`, but those interpretations need another device/version comparison.

### What this establishes about baud detection

Discovery, address assignment, and operating exchanges all occur at 57600 baud in this amplifier reconnect. No transition to another baud rate or valid packet at the other tested rates was observed in retained data. The controller may be reusing a previously learned baud rate; this capture does not demonstrate how it chooses a rate on an unfamiliar port. Transfer interruptions further limit any assertion that a brief probe was absent from the entire attempt.

The next discriminating test is the display on this same controller port, with recording beginning while the port is empty and continuing through connection. This can show whether the controller continues 57600-baud probes, changes rate, or receives a device-originated announcement. It requires moving the display cable, not merely probing the amplifier again.

Evidence: `system-amplifier-detection-12-baud-analysis.json` retains each rate/polarity candidate by contiguous segment; `system-amplifier-detection-12-analysis.json` contains the discovery timing and summary. Event cues and user acknowledgments are in `system-amplifier-detection-12-events.json` and are not hardware transition timestamps.

## Display on the amplifier's former port: capture 13 (2026-10-18)

The amplifier was disconnected and the display connected through the breakout on that same controller port, with recording already running. The probe wiring remained on the reported pins 3/6, GND disconnected. `system-display-detection-13` contains 71.000544 seconds at 500 kS/s in one uninterrupted segment, with no reported USB loss/corruption. Event cues and the user's subsequent done acknowledgment are host annotations; the physical connection time is not measured.

**Observed:** discovery is at 57600 baud, followed by a type `18` command carrying the four-byte big-endian value **115200**, an acknowledgment at the old rate, and subsequent communication at 115200 baud. This supports a common discovery rate and a commanded change for the display, rather than requiring blind rate scanning to explain these two peripherals. It does not establish the startup rate for every possible accessory or all timeout/fallback behavior.

### Discovery and explicit baud change

All bytes below are unescaped and checksum-valid. Times are relative to capture startup.

| Time (s) | Baud | Packet | Interpretation |
| --- | ---: | --- | --- |
| 2.225768 | 57600 | `88 FF 00 05 74 55` | Discovery probe |
| 5.305840 | 57600 | Same probe | No reply observed |
| 8.405918 | 57600 | Same probe | No reply observed |
| 11.476146 | 57600 | Same probe | Probe preceding display reply |
| 11.477372 | 57600 | `88 00 FF 06 30 01 42 55` | Display identity reply, bytes `30 01` |
| 11.485910 | 57600 | `88 FF 00 07 03 30 01 3E 55` | Address-assignment candidate: `03`, identity echoed |
| 11.487628 | 57600 | `88 00 03 35 40 55` | Acknowledgment at assigned address |
| 11.820966 | 57600 | `88 03 00 18 00 01 C2 00 9A 55` | Baud-change command candidate, `0x0001C200` = 115200 |
| 11.822852 | 57600 | `88 00 03 35 40 55` | Baud-change acknowledgment at old rate |
| 12.330984 | 115200 | `88 03 00 38 3D 55` | First observed exchange at new rate |

The first new-rate request begins 510.018 ms after the baud-change command starts, or 508.132 ms after the old-rate acknowledgment starts. These are observed delays for one transition, not specified minimum/maximum timing requirements.

At 115200 baud, the display follows the previously observed sequence: type `38`/`39`, `33`/`32` identity, `34` initialization/`35` acknowledgment, then `30`/`31` polling. The type `32` identity payload differs in some numeric fields from startup 07; the name remains `un-named UI`. Do not assume startup identity/configuration bytes are immutable or replay the old identity blindly.

### Decode validation and mixed-rate evidence

The full recording was explored at 9600, 19200, 38400, 57600, and 115200 baud in both polarities. Only the two expected rates with negative-voltage-one yielded valid packets. A fixed-rate decode across the whole recording necessarily produces framing errors during the other rate's traffic; these are not evidence of acquisition corruption. The separately bounded discovery window (0–12 s at 57600) and operating window (12.2 s onward at 115200) are validated in `system-display-detection-13-analysis.json`.

The broad 0–12 s window contains nine complete valid packets but also 73 decoded characters outside packets and 58 UART errors concentrated around 9–10 s. Their cause is unresolved and they are excluded from protocol interpretation. The narrower 11.4–12 s window covering the final probe, identity, assignment, baud command, and acknowledgments has 45 characters, six complete packets, zero UART errors, and zero packet issues. The new-rate window has 27,735 characters, 2,805 complete packets, zero UART errors, and zero packet issues; every character belongs to a checksum-valid packet.

Reproduction: `python3 analyze_system_bauds.py system-display-detection-13`. The comparison script preserves candidates by contiguous segment and never decodes across a transfer gap. Full candidate analysis: `system-display-detection-13-baud-analysis.json`; transition summary and exact handshake packets: `system-display-detection-13-analysis.json`.

### Current startup model for the two captured peripheral types

1. The controller issues type `05` discovery probes to the `FF` address at 57600 baud.
2. The unassigned peripheral replies with type `06` and two identity bytes: amplifier `07 10`, display `30 01` in these recordings. Their exact class/version encoding remains unconfirmed.
3. Type `07` supplies assigned address `03` and echoes those identity bytes; the peripheral acknowledges with type `35` using `03`.
4. The amplifier continues at 57600. The display receives type `18` carrying `00 01 C2 00`, acknowledges at 57600, and then communicates at 115200.
5. Peripheral-specific initialization and polling follow. Shared discovery/framing does not imply identical message bodies or operating rates.

This explains how the same tested port supports the two device types without requiring a permanently dedicated port type. It strengthens the destination/source interpretation and a dynamically assigned peripheral address. Other devices, multiple peripherals on one electrical segment, recovery after a failed baud change, and return-to-discovery behavior after disconnection remain untested.

## Music controls opened on the display: capture 14 (2026-10-18)

Setup: breakout inline with the display, amplifier reconnected on a different controller port, reported Scope 1 pins 3/6 and GND disconnected. The user opened the music controls once without changing volume or playback. Visible state: Listen tab, Bluetooth label, volume, forward/back, play, options, and an Input tab.

Capture `system-display-music-14` retains 69.683694 seconds at 500 kS/s without USB loss/corruption. The established 115200-baud 8N1 negative-voltage-one model decodes 41,099 characters with zero UART framing errors, 3,428 complete checksum-valid packets, and zero packet issues. Counts: 1,335 type `30`, 1,335 type `31`, 758 type `34`; all 758 subtype length checks pass. Median poll interval is approximately 50 ms. Exact touch timing is not measured; user cues and the visible state acknowledgment are in `system-display-music-14-events.json`.

### Screen-dependent requests

The previous main-screen queries `20 7F`/`20 7C` stop near 20 s. New requests appear beginning at 20.556032 s:

| Candidate key | Request format byte | First request (s) | Reply bytes after the key | Candidate meaning |
| --- | --- | ---: | --- | --- |
| `24 69` | `01` | 20.556032 | `0A 00 00 00 00 00 00 64 64 64 32` | Music-state block; final `32` may be volume 50 |
| `22 13` | `04` | 21.826914 | `00` | Empty string candidate |
| `22 0D` | `04` | 22.793780 | `00` | Empty string candidate |
| `22 10` | `04` | 22.843692 | `00` | Empty string candidate |

`24 69` then recurs approximately once per second; the three `22 xx` keys are requested repeatedly. Their format byte `04` matches the format used for preset-name requests, and null-only replies are consistent with empty strings. No artist/title/source assignment is established for these keys.

Representative request/reply:

```text
88 00 03 31 02 01 24 69 0A 01 5F 11 0F C4 04 33 33 77 F0 95 55
88 03 00 34 01 0E 02 24 69 0A 00 00 00 00 00 00 64 64 64 32 3B 55
```

The adjacent read-only controller snapshot reports `amp_volume_string:50`, `volume:50`, and `musicStatus:"Off"`. It reports the amplifier installed, a separate music module not installed, and the amplifier connection as intermittent at that snapshot. The amplifier and music-module flags are distinct and must not be conflated. These are controller-reported values, not proof of packet-field meanings.

This navigation is consistent with display-local menus issuing different state/string reads. A dedicated menu-open command has not been assigned. The recurring class `01` key `31 17` increments approximately once per second before and after opening the menu; it is not assigned to a music button. Its meaning remains unresolved.

Next correlation: change volume by one small step on the display, record visible before/after values, compare class `01` messages and the `24 69` reply, and check the controller's readback. Capture amplifier-side propagation separately after identifying the display-side event.

Evidence: `system-display-music-14-part-000-packets.json`, `system-display-music-14-analysis.json`, and `network/system-display-music-14-values.json`.

## Display volume-slider adjustment: capture 15 (2026-10-18)

The user made one small upward slider adjustment on Listen/Bluetooth. The slider has no numerical indicator, so the user did not report a numeric target. Capture `system-display-volume-15` uses the same display-side probe setup and 115200-baud inverted decoding, retaining 25,043 UART characters with zero framing errors, 2,089 complete checksum-valid packets, and zero packet issues. All 481 type `34` length checks pass. No USB interruption was reported.

At capture-relative 11.779968 s, the display-originated class `01` message contains key `30 80`, one value byte, and value `3C` (decimal 60):

```text
Wire:      88 00 03 31 01 01 30 80 01 3C AA 55 55
Unescaped: 88 00 03 31 01 01 30 80 01 3C    55 55
```

The checksum is `55` and is escaped as `AA 55` on the wire; the final unescaped `55` is the packet terminator. At 11.784074 s, the controller returns the usual class-acknowledgment candidate:

```text
88 03 00 34 01 02 02 30 0C 55
```

The `24 69` state reply's final value changes from `32` (50) to `3C` (60): the old value appears in 12 replies through 12.134076 s; the new value appears in 30 replies beginning at 13.054098 s. Other bytes in the block remain unchanged:

```text
Before: 0A 00 00 00 00 00 00 64 64 64 32
After:  0A 00 00 00 00 00 00 64 64 64 3C
```

This strongly associates class `01` key `30 80` with an absolute requested volume and the final byte of the `24 69` block with the controller's corresponding display-facing state. Only one nonbaseline slider value has been tested; a second value should confirm the mapping before declaring it complete.

The same action cluster includes key `30 00` with value `14` at 11.664954 s and key `30 83` with value `00` at 11.733960 s. The latter receives the same `02 30` acknowledgment. Their meanings are unresolved; no mute/open-slider/event interpretation is assigned from this single action.

Both read-only web snapshots after the slider action still report `volume:50`, `amp_volume_string:50`, and `amp_con_string:"intermittent"`. Thus a display-facing request, acknowledgment, and state update do not yet establish amplifier-side propagation or application of the new level. These web fields must not be substituted for the observed bus value 60.

Evidence: `system-display-volume-15-analysis.json`, `system-display-volume-15-volume-correlation.json`, event annotations, raw/decoded capture files, and `network/system-display-volume-15-values{,-later}.json`. Next test: one small downward slider adjustment at the same measurement point; amplifier-link propagation remains a separate capture.

## Second display volume value: capture 16 (2026-10-18)

The user made a downward slider adjustment, again with no numeric indicator. Capture `system-display-volume-16` decodes 22,457 UART characters, zero UART errors, and 1,876 complete checksum-valid packets with no packet issues. All 432 type `34` length checks pass; no USB interruption was reported.

At 21.198652 s the display sends:

```text
88 00 03 31 01 01 30 80 01 23 6E 55
```

The value is `23` hex, decimal 35. The following controller acknowledgment at 21.202770 s is again `88 03 00 34 01 02 02 30 0C 55`. The `24 69` state retains final value `3C` (60) through 22.302788 s and returns `23` (35) beginning at 23.282804 s. This provides a second controlled value correlation for the same command and state field:

| Capture | Display key `30 80` value | Following `24 69` final value |
| --- | ---: | ---: |
| 15, upward adjustment | 60 (`3C`) | 60 (`3C`) |
| 16, downward adjustment | 35 (`23`) | 35 (`23`) |

**Current mapping:** display class `01`, format `01`, key `30 80`, count `01`, one-byte absolute volume request. The final byte of the observed `24 69` state block is the corresponding display-facing volume. Tested numeric values are 35, 50 (baseline), and 60; bounds, clipping, and exact slider scale remain untested.

Key `30 83` with value `00` appears twice around the second slider action, at 20.198620 and 21.149476 s; `30 00` with value `14` appears at 20.148638 s. Their meanings remain unresolved. Repetition supports treating them as part of the interaction cluster, not automatically equating either with the absolute volume value.

The adjacent web snapshot still reports both volume fields as 50 and the amplifier connection as intermittent. Actual amplifier application remains unconfirmed despite the consistent display-link request/state mapping. Data: `system-display-volume-16-analysis.json`, its decoded packet file, and `network/system-display-volume-16-values.json`.

## Play-button action: capture 17 (2026-10-18)

The user pressed Play once on Listen/Bluetooth. The icon changed briefly to Pause, then returned to Play. Exact touch and icon-transition timestamps are not measured. Capture `system-display-play-17` decodes 38,550 UART characters with zero UART errors and 3,231 complete checksum-valid packets, with zero packet issues. All 735 type `34` length checks pass; no USB interruption was reported.

The action produces this class `01` command cluster:

| Time (s) | Candidate key | Value | Wire packet |
| --- | --- | --- | --- |
| 27.695172 | `30 83` | `00` | `88 00 03 31 01 01 30 83 01 00 8E 55` |
| 27.745188 | `30 85` | `00` | `88 00 03 31 01 01 30 85 01 00 8C 55` |
| 27.795172 | `30 84` | `01` | `88 00 03 31 01 01 30 84 01 01 8C 55` |

Each receives `88 03 00 34 01 02 02 30 0C 55` in the following exchange. Key `30 84` with value 1 is a play-state/request candidate, but the roles of the three fields must be distinguished through additional controls. `30 83=00` was also observed during slider actions, so it is not specific to Play.

All 65 observed `24 69` replies retain `0A 00 00 00 00 00 00 64 64 64 23`; no polled change in that state block is observed. The web snapshot reports `musicStatus:"Off"`, volume fields 50, and amplifier connection intermittent. A temporary local/optimistic Pause icon followed by a stopped-state refresh is consistent with this evidence, but the display rendering logic and sub-poll-interval state changes have not been directly established. A controller acknowledgment alone does not prove amplifier playback.

Evidence: `system-display-play-17-analysis.json`, raw and decoded capture files, event annotations, and `network/system-display-play-17-values.json`. Next action: one Forward-button press to separate track navigation from the Play-associated command cluster.

## Forward/next-track action: capture 18 (2026-10-18)

The user pressed Forward once on Listen/Bluetooth and reported no visible change. Capture `system-display-forward-18` decodes 16,536 characters with zero UART errors and 1,383 complete checksum-valid packets, with zero packet issues. All 317 type `34` length checks pass; no USB interruption was reported.

At 13.506732 s, the only non-housekeeping class `01` command is:

```text
88 00 03 31 01 01 30 83 01 01 8D 55
```

The candidate key is `30 83`, value `01`. It receives the usual `88 03 00 34 01 02 02 30 0C 55` acknowledgment. All 27 observed `24 69` replies remain `0A 00 00 00 00 00 00 64 64 64 23`.

**Current association:** `30 83=01` requests Forward/next-track in the observed Bluetooth context. Values `00` previously accompanying Play/volume actions may clear or neutralize track navigation; that interpretation remains unconfirmed. Actual track advancement is not established without an active source or an amplifier-side capture. Back/previous-track is the next discriminating action.

Evidence: `system-display-forward-18-analysis.json`, its raw/decoded capture files, and `system-display-forward-18-events.json`.

## Back/previous-track action: capture 19 (2026-10-18)

The user pressed Back once. Capture `system-display-back-19` was stopped immediately on the completion acknowledgment, with no additional fixed recording tail. It decodes 22,676 UART characters with zero UART errors and 1,907 complete checksum-valid packets, with zero packet issues. All 433 type `34` length checks pass; no USB interruption was reported.

At 11.177942 s, the only non-housekeeping class `01` command is:

```text
88 00 03 31 01 01 30 83 01 FF 8F 55
```

The controller returns the usual `88 03 00 34 01 02 02 30 0C 55` acknowledgment. All 38 `24 69` state replies remain unchanged at `0A 00 00 00 00 00 00 64 64 64 23`.

Track-navigation mapping across the controlled Bluetooth-screen tests:

| Key `30 83` value | Observed action |
| --- | --- |
| `01` | Forward/next-track |
| `FF` | Back/previous-track |
| `00` | Accompanies Play/volume; neutral/reset candidate |

The values are consistent with signed relative navigation (+1, −1, 0). Wider signed arithmetic, repeated/held-button behavior, and actual source track changes remain untested. Evidence: `system-display-back-19-analysis.json`, event annotations, and raw/decoded capture files.

## Input tab opened: capture 20 (2026-10-18)

The user opened Input from Listen without selecting a source. Visible options are Bluetooth, Line In 1, and Line In 2. Capture `system-display-input-20` was stopped on the acknowledgment. It contains 66,221 decoded characters, 5,655 complete checksum-valid packets, and all 1,277 type `34` length checks pass. One character outside accepted packets has a UART framing error; no accepted packet has a framing/checksum error. No USB interruption was reported.

No non-housekeeping class `01` write/event key was observed for opening this tab. The `24 69` music-state query ends at 61.647938 s, while existing periodic state queries and the empty string requests `22 13`, `22 0D`, and `22 10` continue. No new read key appears relative to the preceding Listen captures. This is consistent with display-local tab navigation and locally stored source labels; it does not exclude encoded/cached strings or unobserved initialization resources.

The last observed `24 69` block remains `0A 00 00 00 00 00 00 64 64 64 23` (display-facing volume 35). Source enums and source-selection writes are not established by opening Input alone. Next action: select Line In 1 once, then compare emitted commands and any ensuing display state.

Evidence: `system-display-input-20-analysis.json`, its raw/decoded capture files, and event annotations with the visible options.

## Line In 1 selection: capture 21 (2026-10-18)

The user selected Line In 1 from Input. The display returned to Listen with only the volume slider available. Capture `system-display-line1-21` was stopped on acknowledgment and decodes 28,784 characters with zero UART errors, 2,492 complete checksum-valid packets, and zero packet issues. All 534 type `34` length checks pass; no USB interruption was reported.

The selection emits:

| Time (s) | Key | Value | Wire packet |
| --- | --- | --- | --- |
| 28.217610 | `30 83` | `00` | `88 00 03 31 01 01 30 83 01 00 8E 55` |
| 28.267772 | `30 82` | `02` | `88 00 03 31 01 01 30 82 01 02 8D 55` |

Both receive the usual `88 03 00 34 01 02 02 30 0C 55` acknowledgment. The display resumes `24 69` reads on returning to Listen. The first reply at 29.521786 s retains the previous state; replies beginning at 30.836800 s change only the source-associated byte:

```text
Bluetooth baseline: 0A 00 00 00 00 00 00 64 64 64 23
Line In 1:          0A 00 02 00 00 00 00 64 64 64 23
```

**Current mapping:** display class `01` key `30 82`, one-byte value `02`, selects Line In 1. The corresponding source-associated byte in the `24 69` response is at unescaped packet offset 11 (the second data byte after the observed `0A` count/prefix). The baseline Bluetooth context has value `00`; an explicit Bluetooth selection remains to be captured. The volume byte remains `23` (35).

The source enum and the removal of transport controls are consistent with local UI rendering from source state, but the exact render trigger has not been timed or independently injected. No amplifier-side source application is established. Evidence: `system-display-line1-21-analysis.json`, event annotations, and raw/decoded capture files. Next action: open Input and select Line In 2 once.

## Line In 2 selection: capture 22 (2026-10-18)

The user opened Input and selected Line In 2. Capture `system-display-line2-22` was stopped on acknowledgment. It decodes 12,394 characters with zero UART errors, 1,088 complete checksum-valid packets, zero packet issues, and all 204 type `34` length checks passing. No USB interruption was reported.

At 9.990664 s, key `30 83=00` appears, followed at 10.040658 s by:

```text
88 00 03 31 01 01 30 82 01 01 8E 55
```

Both receive the usual `02 30` acknowledgment. The `24 69` source-associated byte changes from `02` to `01`, first observed at 12.254790 s. Other bytes remain unchanged, including volume 35:

```text
Line In 1: 0A 00 02 00 00 00 00 64 64 64 23
Line In 2: 0A 00 01 00 00 00 00 64 64 64 23
```

The observed source enum is **Line In 1 = `02`, Line In 2 = `01`**; it must not be inferred from label numbering. Bluetooth's baseline value `00` still requires an explicit selection capture. Evidence: `system-display-line2-22-analysis.json`, event annotations, and raw/decoded capture files.

## Bluetooth selection: capture 23 (2026-10-18)

The user selected Bluetooth from Input and reported the playback controls returned on Listen. Capture `system-display-bluetooth-23` was stopped on acknowledgment. It decodes 21,230 characters with zero UART errors, 1,818 complete checksum-valid packets, zero packet issues, and all 378 type `34` length checks passing. No USB interruption was reported.

The action emits:

| Time (s) | Key | Value | Wire packet |
| --- | --- | --- | --- |
| 16.850904 | `30 8A` | `00` | `88 00 03 31 01 01 30 8A 01 00 87 55` |
| 16.900892 | `30 83` | `00` | `88 00 03 31 01 01 30 83 01 00 8E 55` |
| 16.950892 | `30 82` | `00` | `88 00 03 31 01 01 30 82 01 00 8F 55` |

All three receive the usual `02 30` acknowledgment. The `24 69` source-associated byte retains `01` through 18.005042 s, then changes to `00` beginning at 19.340062 s. Other bytes remain unchanged, including volume 35. Key `30 8A` is newly observed in this selection cluster; its purpose is unresolved.

### Current display-side music control map

All rows below use type `31`, class byte `01`, format byte `01`, a two-byte key, count `01`, and a single value byte. They describe commands from the display to the controller, not direct amplifier commands.

| Key | Value | Observed operation | Evidence |
| --- | --- | --- | --- |
| `30 80` | `23` / `3C` | Absolute volume 35 / 60 | Captures 15–16; corresponding `24 69` final-byte update |
| `30 82` | `00` | Bluetooth | Capture 23; corresponding source-state update |
| `30 82` | `01` | Line In 2 | Capture 22; corresponding source-state update |
| `30 82` | `02` | Line In 1 | Capture 21; corresponding source-state update |
| `30 83` | `01` | Forward/next-track request | Capture 18 |
| `30 83` | `FF` | Back/previous-track request | Capture 19 |
| `30 83` | `00` | Neutral/reset candidate accompanying other actions | Multiple captures; no independent action assigned |
| `30 84` | `01` | Play request | Captures 17 and 32; playing state observed with paired source |
| `30 84` | `02` | Pause request | Capture 32; paused state observed with paired source |
| `30 85` | `00` | Unresolved Play-cluster field | Capture 17 |
| `30 86` | Tested 50, 70, 80, 150 | Absolute Balance slider value | Capture 29; final state 50 |
| `30 87` | Tested 50, 130, 150 | Absolute Treble slider value | Capture 29; corresponding state updates |
| `30 88` | Tested 30, 130, 140 | Absolute Bass slider value | Captures 25 and 29; corresponding state updates |
| `30 8A` | `00` | Unresolved Bluetooth-selection field | Capture 23 |

The common controller acknowledgment is `88 03 00 34 01 02 02 30 0C 55`. It acknowledges the command family without echoing the full key or value; it does not prove downstream amplifier application. In the observed `24 69` state reply, unescaped packet offset 11 carries the source value and offset 19 carries the volume. These offsets apply to this block layout, not all type `34` messages.

The return of transport controls in Bluetooth and their absence for Line In sources correlate with the source enum and source-selection action. Layout, fixed labels, and button availability are consistent with local UI logic; the exact trigger timing remains unmeasured.

Evidence: `system-display-bluetooth-23-analysis.json`, event annotations, and raw/decoded capture files. Next action: open Options once without changing a setting, and record its visible controls and requests.

## Options menu opening and automatic closure: capture 24 (2026-10-18)

The user opened Options without adjusting a setting. Bass, treble, and balance controls appeared briefly, then closed automatically after a few seconds. Exact open/close times are unmeasured.

Capture `system-display-options-24` decodes 28,171 characters with zero UART errors, 2,430 complete checksum-valid packets, zero packet issues, and all 508 type `34` length checks passing. No USB interruption was reported. No class `01` action appears beyond the existing periodic `31 17` and `30 00` housekeeping candidates. The read keys and reply contents remain unchanged, including all 47 `24 69` replies:

```text
0A 00 00 00 00 00 00 64 64 64 23
```

No dedicated menu-open or menu-close command has been identified. The evidence favors a local overlay/timeout, but the exact closure trigger is not established. The three consecutive `64` bytes (decimal 100) are candidate centered tone/balance values; their meanings require individual adjustments rather than assignment by ordering alone.

Evidence: `system-display-options-24-analysis.json`, event annotations, and raw/decoded capture files. Next action: reopen Options and adjust Bass once, leaving Treble and Balance unchanged.

## Bass adjustment and subsequent UI power transition: capture 25 (2026-10-18)

The user adjusted Bass, then later reported that the display returned to its power-off screen; they powered it on and navigated back to music. The later UI actions explain why this recording contains more than the requested slider adjustment. Their exact times were not measured, and they must not be assigned to Bass.

Capture `system-display-bass-25` contains 32,368 decoded characters, 2,833 complete checksum-valid packets, and all 574 type `34` length checks pass. There are 21 UART errors in 21 characters outside accepted packets. No accepted packet has a framing/checksum error; no USB interruption was reported.

The initial slider cluster includes `30 83=00` followed by:

| Time (s) | Key | Value | Wire packet |
| --- | --- | ---: | --- |
| 14.300294 | `30 88` | 130 (`82`) | `88 00 03 31 01 01 30 AA 88 01 82 07 55` |
| 15.150304 | `30 88` | 140 (`8C`) | `88 00 03 31 01 01 30 AA 88 01 8C FD 55` |

The `88` key byte is escaped as `AA 88` on the wire. Both commands receive the usual `02 30` acknowledgment. `24 69` replies retain the baseline through 16.204438 s, then change at 17.254454 s:

```text
Before: 0A 00 00 00 00 00 00 64 64 64 23
After:  0A 00 00 00 00 00 00 64 64 8C 23
```

**Current association:** key `30 88` sets Bass, and unescaped packet offset 18 in this `24 69` layout is its display-facing state value. Baseline is 100, final adjusted value is 140; intermediate request 130 is not sampled as a returned state. Bounds, units, and whether 100 is the exact neutral value require further evidence.

From approximately 26–33 s, another action cluster includes repeated `30 42=01`, `30 7C=00`, several `30 01` values, volume-related keys `30 80`/`30 81` with `4C`, and many `30 86` onward keys with zero values. The reported power-screen transition and return to music provide context for this separate settings/event burst. It may represent display-side reinitialization or state restoration, but individual meanings are unresolved. Do not treat those later zero writes as isolated Bass actions or silently assume the initial slider state remained in force afterward.

Evidence: `system-display-bass-25-analysis.json`, raw/decoded files, and event annotations including the later user explanation. Subsequent captures group ordered adjustments with pauses instead of requiring a separate recording for each control.

## Grouped tone adjustments: capture 26, signal quality rejected (2026-10-18)

The actual user-reported action order was Treble up, Treble down, Balance up, Balance down, then Bass down. This supersedes the initial three-action cue. The capture was stopped immediately on the completion acknowledgment.

`system-display-tone-batch-26` retains 62.807072 seconds at 500 kS/s in one segment, with no reported USB loss/corruption. However, the analog signal is abnormal throughout sampled windows: approximately −13.5 V to +12.3 V at the first/99th percentiles, compared with approximately ±2 V active levels in prior usable recordings. At the established 115200-baud negative-voltage-one interpretation, 41,194 of 50,079 decoded characters have UART framing errors. The opposite polarity also fails broadly. Exploration at 57600, 38400, 19200, and 9600 produces no valid packet sequence.

Sparse checksum-valid frames amid widespread errors are insufficient to identify these actions reliably. Sampled two-second windows every five seconds show poor quality across the capture, so a complete clean action interval has not been established. Offline baseline subtraction and hysteresis exploration on a short prefix did not recover a consistently clean stream. No Treble, Balance, or additional Bass mapping is accepted from this attempt.

The cause of the changed analog signal is unresolved; probe contact or pickup must be checked before repeating the batch. The raw waveform is preserved unchanged. Evidence: `system-display-tone-batch-26-manifest.json`, `-events.json`, `-signal-quality.json`, `-baud-analysis.json`, and raw samples. The `-analysis.json`/`-packets.json` files from attempted fixed-rate decodes are diagnostic artifacts, not an accepted protocol decode.

Next step: verify the reported differential connections on system breakout pins 3/6 with GND disconnected, acquire a short passive quality check, then repeat the same ordered five-action batch only after reliable decoding returns.

### Passive check after reseating: capture 27

After probe reseating was acknowledged, `system-signal-check-27` recorded three seconds at 500 kS/s without requesting UI actions. The abnormal signal persists: approximately −13.45 V and +12.14 V at the first/99th percentiles, median +0.65 V. Neither polarity yields any complete valid packet at 115200 baud. Negative-voltage-one produces 2,483 UART errors among 3,201 decoded characters; positive-voltage-one produces 2,408 among 3,203. No transfer interruption was reported. The probe-reseating step did not restore usable acquisition, and the tone batch remains unrepeated.

Evidence: `system-signal-check-27-analysis.json` and its raw/metadata files. The next diagnostic compares direct multimeter voltage across breakout 3/6 with the AD3 waveform to distinguish a changed bus voltage from an acquisition/reference problem.

### Signal restored after further reseating: capture 28

The user reseated the probe connection again before `system-signal-check-28`. The three-second, 500 kS/s passive check returns to approximately −1.82/+1.78 V active plateaus and −0.26 V idle. The established negative-voltage-one 115200-baud model yields 1,785 UART characters, zero UART errors, 152 checksum-valid packets, and zero packet issues. This supports the reported probe-contact explanation for captures 26–27. No multimeter reading was needed after this successful check. Grouped tone-action recording can resume; the rejected action capture is not retroactively validated.

Evidence: `system-signal-check-28-analysis.json` and raw/metadata files.

## Grouped tone adjustments after probe recovery: capture 29 (2026-10-18)

The completed action order was Treble up, Treble down, Balance right, Balance left, then Bass down, with pauses between controls. Exact per-touch timing and numeric slider values were not provided. Capture `system-display-tone-batch-29` was stopped on acknowledgment and decodes 20,668 UART characters, zero UART errors, and 1,800 complete checksum-valid packets, with zero packet issues. All 390 type `34` length checks pass; no USB interruption was reported.

### Command mapping and values

| Control | Key | Observed time/value sequence (capture-relative seconds, decimal values) |
| --- | --- | --- |
| Treble | `30 87` | 11.496294 → 130; 12.796422 → 150; 14.546360 → 50; 16.096406 → 50; 21.546482 → 50 |
| Balance | `30 86` | 16.146372 → 80; 16.946400 → 150; 17.746418 → 70; 18.646452 → 50; 21.496482 → 50 |
| Bass | `30 88` | 19.996472 → 30; 20.846462 → 30; 21.596472 → 30 |

Each is a class `01`, format `01`, count `01`, one-byte absolute slider value. Each receives the common `02 30` acknowledgment. Neutral/reset candidate `30 83=00` accompanies the initial adjustments. At 21.496482–21.596472 s, all three final tone values are sent consecutively; this is a repeated settings triplet, not three independently reported new touches. A popup-close/commit interpretation is possible but not established without exact UI timing.

### State block mapping

The first `24 69` state in this recording is:

```text
0A 00 00 00 00 00 00 28 28 46 23
```

This reports Balance 40, Treble 40, Bass 70, and Volume 35 under the mapping established by this capture. Those initial settings differ from the old 100/100/100 baseline because intervening UI actions, including the rejected recording 26, were performed; a rejected acquisition does not imply its physical actions had no effect.

Treble state then reports 130, 150, and 50. Intermediate Balance/Bass requests are not all reflected in individually sampled replies. The final combined state begins at 23.550650 s:

```text
0A 00 00 00 00 00 00 32 32 1E 23
                     |  |  |  +-- Volume 35
                     |  |  +----- Bass 30
                     |  +-------- Treble 50
                     +----------- Balance 50
```

Offsets in the complete unescaped `34 01` reply for key `24 69`:

| Field | Packet offset | Display write key |
| --- | ---: | --- |
| Source | 11 | `30 82` |
| Balance | 16 | `30 86` |
| Treble | 17 | `30 87` |
| Bass | 18 | `30 88` |
| Volume | 19 | `30 80` |

These fields are observed one-byte numeric values. Physical dB/pan scale, exact neutral point, limits, and clipping behavior are not established. A previous baseline of 100 suggests a centered encoding, but no conversion formula is assigned. This capture validates display/controller exchange only; amplifier-side propagation remains unconfirmed.

Evidence: `system-display-tone-batch-29-analysis.json`, `-correlation.json`, event annotations, and raw/decoded files. The next useful grouped capture is at the amplifier connection while operating the already mapped display controls, to identify controller-to-amplifier translation and separate requested state from applied state.

## Periodic traffic and heartbeat candidates

Most packets occur independently of user input. `system-periodic-traffic-analysis.json` compares captures 14, 15, 17, 19, 24, 25, and 29.

| Traffic | Observed cadence | Interpretation |
| --- | --- | --- |
| Controller type `30` poll and display type `31` reply | Median interval approximately 50 ms (20 exchanges/s) | Ongoing polling; a reply may be empty, a state query, or a command/event |
| Display class `02` state reads and controller type `34` replies | Screen-dependent; many keys recur about once per second, others more slowly | Periodic state refresh |
| Display class `01`, key `31 17`, format `02`, count `02` | Approximately once per second, with scheduling gaps | Monotonic counter/heartbeat candidate |
| Display class `01`, key `30 00` | Often about every four seconds with value `00`; values and timing change around screens/actions | Periodic screen/activity/housekeeping candidate; semantics unresolved |

For `31 17`, the two-byte value interpreted big-endian increments by exactly one at every consecutive occurrence in the compared captures. Examples: capture 14 increases from 332 to 400 across 69 occurrences; capture 17 from 679 to 743 across 65; capture 29 from 1979 to 2009 across 31. The counter continues across the UI power-off-screen transition reported in capture 25. It resembles an elapsed-time or liveness counter, but neither its time origin nor a watchdog requirement has been established. It is not assigned to a music control merely because class `01` carries it.

Capture 29 illustrates the scale: 1,800 packets comprise 705 controller polls, 705 display replies, and 390 controller data/acknowledgment messages. Only 13 display messages carry Bass/Treble/Balance values; these include slider intermediate values and repeated final values from five reported gestures. Another ten messages in that interaction cluster carry neutral/reset candidate `30 83=00`. Periodic polls, state refreshes, counter messages, and acknowledgments account for the bulk of the traffic.

Controller replacement requires ongoing polling and state servicing while idle as well as handling user commands. Exact liveness timeouts, counter handling requirements, and whether every housekeeping value must be interpreted remain to be tested. Periodic traffic must retain its timing and identity in analysis rather than being counted as independent user actions.

## Music text and metadata candidates

`system-music-string-analysis.json` inventories adjacent matching class `02`, format `04` queries and type `34` replies across the accepted saved display captures, excluding the rejected tone capture 26 and the mixed-rate detection capture. The recurring music-related string keys are:

| Key | Matched replies | Observed reply data |
| --- | ---: | --- |
| `22 0D` | 394 | `00` in every reply |
| `22 10` | 394 | `00` in every reply |
| `22 13` | 188 | `00` in every reply |

The same request-format pattern also retrieves null-terminated `Preset 1` through `Preset 6` using keys `22 01`–`22 06`. This supports interpreting format `04` and the `22 xx` namespace as string-capable fields. Null-only music replies are consistent with empty text, and no nonempty title/artist/album text has been observed in these fields.

At this initial empty-string stage, specific field roles were unresolved. Subsequent pairing/playback captures 30–31 below identify device name, artist, and song title. Additional track/source changes and distinct known strings remain useful for confirming roles and establishing encoding, length limits, and truncation behavior.

## Paired phone name: capture 30 (2026-10-18)

The user paired their phone and reported its name visible on the display. A five-second passive capture, `system-display-phone-name-30`, decodes 3,057 UART characters with zero UART errors, 247 complete checksum-valid packets, zero packet issues, and all 57 type `34` length checks passing. No USB interruption was reported.

String key `22 13` now returns `David's Z Fold7` followed by a null terminator, observed twice. Keys `22 0D` and `22 10` still return null-only data. Example:

```text
Request: 88 00 03 31 02 04 22 13 00 09 55
Reply:   88 03 00 34 01 13 02 22 13 44 61 76 69 64 27 73 20 5A 20 46 6F 6C 64 37 00 1E 55
Text:    David's Z Fold7\0
```

Thus `22 13` is associated with the paired Bluetooth device name, rather than album metadata in this context. The music-state block remains `0A 00 00 00 00 00 00 32 32 1E 23`; merely showing a phone name does not change that block in this capture. Evidence: `system-display-phone-name-30-analysis.json` and raw/decoded files.

## Artist and song text during phone playback: capture 31 (2026-10-18)

The user began Spotify playback on the paired phone and reported artist and song text visible. Five-second passive capture `system-display-track-metadata-31` decodes 3,127 UART characters with zero UART errors, 256 complete checksum-valid packets, zero packet issues, and all 58 type `34` length checks passing. No USB interruption was reported.

| String key | Captured text | Display role |
| --- | --- | --- |
| `22 0D` | `Mia Baron` | Artist |
| `22 10` | `Losing Myself` | Song title |
| `22 13` | `David's Z Fold7` | Paired Bluetooth device name |

All values are null-terminated and use ASCII-compatible bytes for these examples. General UTF-8/Unicode support, maximum lengths, truncation, and other source types remain untested. These are controller-supplied content fields rendered by the display, rather than evidence of transferring menu layouts or graphics.

All five observed `24 69` replies now contain:

```text
Before playback: 0A 00 00 00 00 00 00 32 32 1E 23
During playback: 0A 01 00 03 00 00 00 32 32 1E 23
```

Unescaped packet offsets 10 and 12 change from `00`/`00` to `01`/`03`; source remains Bluetooth `00`, Balance/Treble/Bass remain 50/50/30, and Volume remains 35. Playback/power/status meanings for those two changing bytes require a pause/resume comparison; no individual bit or enum is assigned from this single state transition.

Evidence: `system-display-track-metadata-31-analysis.json`, its raw/decoded files, and adjacent controller web snapshot `network/system-display-track-metadata-31-values.json`. A grouped Pause → Play → Forward → Back capture with pauses can now distinguish active playback commands and state flags using the paired source.

## Active-source transport and metadata transitions: capture 32 (2026-10-18)

The actual initial display state was paused. The user performed Play → Forward → Back three times → Pause, superseding the original cue. `system-display-active-transport-32-events.json` records this corrected sequence. Exact touch times are not measured.

The recorder retained parts of 7.686398 and 61.879720 seconds. One USB corruption event discarded 27,294 available samples before part 001. The parts decode independently into 383 and 3,129 complete checksum-valid packets, respectively, with zero UART errors and zero packet issues in either part. All 812 type `34` length checks pass. All reported button actions appear within uninterrupted part 001; no command sequence is joined across the gap.

### Transport requests with a paired playing source

Times below are relative to part 001, not the start of the full capture.

| Time (s) | Key/value | Association |
| --- | --- | --- |
| 11.370940 | `30 83=00` | Neutral/reset candidate before Play |
| 11.420934 | `30 85=00` | Unresolved Play-associated field |
| 11.470936 | `30 84=01` | Play |
| 21.226114 | `30 84=01` | Playing-state request preceding Forward |
| 21.326108 | `30 83=01` | Forward |
| 26.287348 | `30 84=01` | Playing-state request preceding Back |
| 26.336142 | `30 83=FF` | First Back |
| 32.131284 | `30 84=01` | Playing-state request preceding Back |
| 32.181312 | `30 83=FF` | Second Back |
| 32.431294 | `30 84=01` | Playing-state request preceding Back |
| 32.481328 | `30 83=FF` | Third Back |
| 42.186498 | `30 83=00` | Neutral/reset candidate before Pause |
| 42.236472 | `30 84=02` | Pause |

All receive the same `88 03 00 34 01 02 02 30 0C 55` acknowledgment. **Play and Pause use explicit values 1 and 2, not an assumed boolean 1/0.** Forward and Back additionally assert Play before issuing the relative track action in this active-source capture. Exact ordering and associated fields should be preserved by an emulator until optionality has been tested.

### Playback state

In the `24 69` reply, unescaped packet offset 10 is the playback-state candidate:

| Value | Observed context |
| --- | --- |
| `02` | Initial paused state and final state after Pause |
| `01` | Playing after Play and during track navigation |
| `00` | Brief transition after Play and earlier inactive-source recordings; idle/stopped/transition meaning not fully distinguished |

The first post-Play state changes through `00` at 13.675110 s and reaches `01` at 14.675126 s. After the Pause request at 42.236472 s, sampled state reaches `02` at 48.595718 s. These are observed refresh delays and must not be treated as universal timeouts. Metadata can also clear briefly during a transition.

The source remains Bluetooth (`00` at offset 11). Another pair of bytes, packet offsets 12–13, changes from `03 00` to `02 14` during the next track and back later. Its interpretation is unresolved; it must not be conflated with the confirmed playback-state byte.

### Track metadata changes

| First observed part-001 time (s) | Artist key `22 0D` | Title key `22 10` |
| --- | --- | --- |
| 0.964896 / 1.014888 | Mia Baron | Losing Myself |
| 12.925094 / 12.975094 | Empty | Empty |
| 15.020142 / 15.090950 | Mia Baron | Losing Myself |
| 23.080280 / 23.130274 | girlFM | Radio |
| 35.240488 / 35.290484 | Mia Baron | Losing Myself |

Forward is followed by the second artist/title pair. The Back sequence is followed by return to the original pair. The captures do not distinguish which individual Back restarted the current track versus selected a prior track, especially with delayed metadata refresh and source-specific button behavior. The device-name key `22 13` remains `David's Z Fold7` throughout.

This confirms artist/title field roles across two populated tracks and ties transport requests to observable source changes through the original controller. It still does not identify the controller-to-amplifier wire commands; the measurement point remains the display link.

Evidence: `system-display-active-transport-32-analysis.json`, `-correlation.json`, both part packet files, raw recordings, manifest, and event annotations. Next useful capture: amplifier-side traffic while performing a grouped source/volume/tone/transport sequence from the display.

## Amplifier probe verification: capture 33 (2026-10-18)

The breakout was moved inline with the amplifier, with Scope 1 on reported pins 3/6 and GND disconnected. A three-second passive check at 500 kS/s observes approximately ±2.2 V active levels and −0.12 V idle. At 57600 baud, negative-voltage-one, all 1,064 decoded characters pass UART framing and form 16 checksum-valid packets with no boundary issues: four each of `30`, `31`, `33`, and `32`. No USB interruption was reported. This establishes usable amplifier-side acquisition before the grouped action test.

Evidence: `system-amplifier-check-33-analysis.json`, its decoded packet file, raw samples, and metadata.

## Amplifier-side grouped controls and metadata: capture 34 (2026-10-18)

The user performed this actual sequence: Play on the phone; Pause on the display; Play on the display; Volume up; Forward; Pause; Back; Line In 1; Mute; Unmute; Line In 2. This supersedes the initial cue. All actions after the initial phone Play were reported in the display-control context; exact touch times and numeric slider targets were not measured.

The 57600-baud negative-voltage-one capture has contiguous parts of 61.110784 and 86.191236 seconds. A USB corruption event between parts discarded 1,653 available samples. Parts decode independently into 341 and 445 complete checksum-valid packets (786 total), with zero UART framing errors. Part 001 has one truncated trailing packet at the stop boundary, excluded from accepted packets. All eleven settings writes and their eleven acknowledgments are intact within part 001.

### Settings are written as a full short block

The controller normally requests a 30-byte block using type `33` and receives type `32`. On control changes, it sends type `34` carrying a modified 30-byte block. The amplifier returns type `35`. Header, escaping, and additive checksum match the established system framing, but the body differs from the display's key/value messages.

```text
Controller read:  88 03 00 33 00 1E 24 55
Amplifier reply:  88 00 03 32 00 1E [30-byte block] checksum 55
Controller write:88 03 00 34 00 1E [30-byte block] checksum 55
Amplifier ack:   88 00 03 35 40 55
```

The field count `00 1E` is big-endian 30. Complete unescaped reply/write length is 38 bytes. Values below are offsets in the complete packet, not offsets in the 30-byte body:

| Packet offset | Control field | Observed encoding |
| --- | --- | --- |
| 6 | Volume | Unsigned absolute value; 35, 50, 55 observed |
| 7 | Unresolved | `00` in these settings blocks |
| 8 | Source | Bluetooth `00`, Line In 2 `01`, Line In 1 `02` |
| 9 | Track navigation | Neutral `00`, Forward `01`, Back `FF` (signed −1 candidate) |
| 10 | Playback request | Play `01`, Pause `02` |
| 11 | Mute | Unmuted `00`, muted `01` |
| 12 | Balance | Signed value, validated in capture 35; `CE` = −50 here |
| 13 | Treble | Signed value, validated in capture 35; `CE` = −50 here |
| 14 | Bass | Signed value, validated in capture 36; `BA` = −70 here |
| 15–35 | Other configuration | Preserved bytes; individual meanings unresolved |

The display-facing tone values immediately preceding this test were Balance 50, Treble 50, Bass 30. Together with the original 100/100/100 versus amplifier 0/0/0 baseline, this supports the candidate conversion **amplifier signed value = display value − 100**. Controlled amplifier-side tone changes are still needed to establish the formula independently and test bounds.

### Observed settings writes

Times are relative to part 001. Every row has a following type `35` acknowledgment.

| Time (s) | Volume | Source | Track | Playback request | Mute |
| --- | ---: | --- | --- | --- | --- |
| 4.043314 | 35 | Bluetooth | Neutral | Pause | Off |
| 7.873364 | 35 | Bluetooth | Neutral | Pause | Off |
| 21.253596 | 50 | Bluetooth | Neutral | Play | Off |
| 22.283616 | 55 | Bluetooth | Neutral | Play | Off |
| 25.058668 | 55 | Bluetooth | Forward | Play | Off |
| 29.228740 | 55 | Bluetooth | Neutral | Pause | Off |
| 38.654254 | 55 | Bluetooth | Back | Pause | Off |
| 47.379042 | 55 | Line In 1 | Neutral | Play | Off |
| 55.449202 | 55 | Line In 1 | Neutral | Play | On |
| 62.299330 | 55 | Line In 1 | Neutral | Play | Off |
| 68.219398 | 55 | Line In 2 | Neutral | Play | Off |

The first two writes both contain Pause despite the reported Pause/Play button sequence. Playback intent in the settings block can differ from subsequent actual playback state, and some short-block readbacks immediately retain or return to value `01` while the larger status reply later changes to paused. Do not assign one-to-one button success solely from the reported action order or acknowledgment. Track navigation, volume, source, and mute correlations are established by the corresponding byte changes across preserved full blocks.

After source and mute changes, subsequent type `32` replies match the written body in these examples. Volume readback reaches 55; the earlier 50 request is superseded by 55 before the next short reply. Thus the amplifier-side data now establishes application/readback beyond the display-only request/state observations. Timing and transient playback behavior still require separate treatment.

### Larger status block and metadata

The type `30` request with count `00 CC` returns type `31`, 212 bytes total, with a 204-byte body. The following field layout is supported by the changing values and populated strings:

| Complete packet offset/range | Candidate field |
| --- | --- |
| 6 | Reported volume (35, then 55) |
| 7 | Unresolved connection/enable flag (`01` here) |
| 8 | Reported playback state (`00`, `01`, `02`) |
| 9 / 10 / 11 | Balance / Treble / Bass signed values, controlled readback confirmed in captures 35–36 |
| 12 | Mute-associated field candidate |
| 13–76 | Song title region, 64 bytes |
| 77–140 | Artist region, 64 bytes |
| 141–172 | Paired device-name region, 32 bytes |
| 173 | Version candidate `10`, matching reported version 0.16 |
| 174 onward | ASCII `20131031` plus remaining configuration/padding; build-date interpretation unconfirmed |

Metadata is populated with `Losing Myself` / `Mia Baron` / `David's Z Fold7`, then `Radio` / `girlFM` / the same device name. Text is null-terminated within the observed fixed regions; maximum supported text lengths, non-ASCII encoding, and completely filled fields remain untested. These data provide the controller-side source for the display string keys `22 10`, `22 0D`, and `22 13`, respectively.

The status reply changes to playing/paused independently of the request byte, providing an actual-state feedback path. The controller replacement should preserve read/modify/write handling for unknown short-block fields and distinguish requested playback from reported status.

Evidence: `system-amplifier-controls-34-analysis.json`, `-correlation.json`, both part packet files, raw recordings, manifest, and the corrected event log. Next useful grouped capture: amplifier-side Bass/Treble/Balance changes to validate the signed conversion and complete per-field translation.

## Amplifier-side tone adjustments: capture 35 (2026-10-18)

The user selected Bluetooth, adjusted Treble up, Balance up, and Bass up. Balance is a vertical up/down slider on this display; the earlier right/left wording in cues must not be interpreted as an established physical left/right pan direction. Exact slider values and touch times were not measured.

The uninterrupted 68.018060-second capture at 500 kS/s decodes at 57600 baud, negative-voltage-one, into 23,708 UART characters with zero UART errors, 358 complete checksum-valid packets, and zero packet issues. Counts: 89 each of `30`/`31`, 84 each of `33`/`32`, six type `34` settings writes and six type `35` acknowledgments. No USB loss/corruption was reported.

| Write time (s) | Changed field relative to preceding short reply | Effect |
| --- | --- | --- |
| 17.164198 | Offset 8: `01`→`00` | Line In 2 → Bluetooth |
| 25.054324 | No body-byte difference | Repeated existing settings |
| 26.074404 | Offset 13: `CE`→`E2` | Treble signed −50 → −30 |
| 35.844534 | Offset 12: `CE`→`F6` | Balance signed −50 → −10 |
| 37.224524 | Same Balance update repeated before next short readback | No additional target value |
| 41.394618 | No body-byte difference | No changed Bass value captured |

Each write receives a type `35` acknowledgment. The larger type `31` status confirms Treble −30 at 27.110494 s and Balance −10 at 36.888186 s. Type `32` short replies also converge to these values, at 27.456064 and 38.599140 s respectively. Thus the field locations and amplifier readback for Treble/Balance are validated by controlled changes.

Bass stays at raw `BA` (signed −70) in all settings writes and status replies despite the reported upward gesture. It is unresolved whether the slider value stayed unchanged or an intended change was not emitted; no different Bass value or failure mode is inferred from this attempt. Volume remains 55, mute remains off, and source ends at Bluetooth. A follow-up grouped Bass up/down test with distinct movements is needed before claiming a controlled amplifier-side Bass change.

The candidate display-to-amplifier offset conversion remains `signed amplifier value = display value − 100`, supported by the prior matched baselines. This amplifier-only recording has no numeric display value, so it does not independently calibrate the entire conversion range or its limits.

Evidence: `system-amplifier-tones-35-analysis.json`, raw/decoded files, manifest, and corrected event annotations. Future instructions use Balance up/down.

## Amplifier Bass up/down confirmation: capture 36 (2026-10-18)

The user moved Bass clearly upward, paused, then moved it clearly downward. `system-amplifier-bass-batch-36` retains 220.736198 seconds at 500 kS/s in one segment, with no USB interruption. At 57600 baud, negative-voltage-one, it decodes 80,643 characters with zero UART framing errors and 1,218 complete checksum-valid packets. There are 91 characters outside complete packets, all at the leading boundary between 0.000160 and 0.015718 s; they are excluded from message interpretation. Counts: 302 each of `30`/`31`/`33`/`32`, five settings writes (`34`) and five acknowledgments (`35`).

Bass changes at complete-packet offset 14 in the short settings write:

| Write time (s) | Raw byte | Signed value | Interpretation |
| --- | --- | ---: | --- |
| 191.361030 | `C4` | −60 | Intermediate upward movement from baseline −70 |
| 192.396104 | `46` | +70 | Higher Bass setting |
| 193.416074 | `46` | +70 | Repeated target |
| 202.546210 | `C4` | −60 | Downward movement |
| 203.581238 | `C4` | −60 | Repeated target |

Every settings write receives `88 00 03 35 40 55`. The larger status reply reports +70 at complete-packet offset 11 beginning at 194.500368 s and −60 beginning at 204.605476 s. Short type `32` replies also report +70 at 194.860200 s and −60 at 204.964390 s. Both settings and status paths therefore confirm the Bass field and its signed-value interpretation across zero.

Balance remains −10, Treble −30, Volume 55, Source Bluetooth (`00`), and Mute off. No changed audio scale in dB or exact neutral/range limit is inferred. Under the existing display-offset model, amplifier +70/−60 would correspond to display values 170/40, but those display-link values were not recorded simultaneously and remain derived rather than directly observed.

Together, captures 35–36 validate all three amplifier tone field positions and changing readback values. The music path now has observed control/state exchanges for volume, sources, mute, transport, tone, and populated metadata. Remaining work includes startup/reset/recovery behavior, unknown block fields and timing limits, further text encodings/lengths, and controller-emulator validation; these captures do not constitute a complete system specification or establish valve control.

Evidence: `system-amplifier-bass-batch-36-analysis.json`, `-correlation.json`, event annotations, raw and decoded data, and manifest.

## Virtual amplifier backed by Sonos

The replacement controller exposes music capability to the displays and maps their existing music events to the bathroom Sonos through Home Assistant. No physical Kohler amplifier connection or additional UART/transceiver is needed for this target. Original amplifier captures remain reference evidence for interpreting display state.

Control path: display → ESP32 music state/event handler → Home Assistant → Sonos. Feedback path: Sonos → Home Assistant entity state/attributes → ESP32 display state responses. Both displays share the same music model.

Initial mappings are volume, mute, explicit play/pause, next/previous, playback state, artist and title. Use reported Sonos state to reconcile UI values rather than treating action dispatch as proof of playback. Track actions depend on the active Sonos media source. The display device-name string can identify the bathroom speaker; Bluetooth and line-input selection semantics require a separate mapping decision, since those labels describe the original amplifier's inputs. Tone control conversion remains uncalibrated; unsupported balance or source controls must not be silently treated as supported.

Home Assistant unavailability leaves local display protocol servicing active. Music state must reflect unavailable/stale backend status, and obsolete transport actions must not be replayed after reconnect. Water and steam control must remain independent of this network music bridge.

References: [Home Assistant Sonos integration](https://www.home-assistant.io/integrations/sonos/) and [media-player actions](https://www.home-assistant.io/integrations/media_player/).

## Additional virtual accessory controls: K-99701 bridge reference

A K-99701 room-light bridge has been purchased for spare-bench investigation and is expected in a few days. It is not yet available for captures. The replacement target includes display control of Home Assistant devices such as floor heating, without retaining the physical bridge. A Konnect module is separately available; its cloud/app/voice role is distinct from the room-light bridge.

Next evidence after arrival: capture bridge discovery and initialization on the spare system; compare display state/availability before and after connection; establish whether a paired switch/dimmer load module is required to expose controls; exercise available controls and map their requests/state. Bridge-only behavior and registered-load behavior must be distinguished.

No additional permanent UART is needed for a virtual accessory implemented inside the replacement controller. A floor-heating mapping must match the available control semantics, such as an enable switch rather than an unsupported temperature-setting interface. The existing floor thermostat remains responsible for temperature regulation and floor limits.

## Display capability/status candidate from historical amplifier comparison

Comparison performed on 2026-10-18 with `compare_display_capabilities.py`; machine-readable evidence is in `display-capability-comparison.json`. Only UART-framing-valid, checksum-valid, length-valid controller-to-display type `34`, subtype `01` responses are included. Other initialization packet layouts are outside this comparison.

`display-settings-01-packets.json` and `system-display-amplifier-10-part-000-packets.json` share 14 response keys. Twelve have identical payload sets. Two differ: `24 42` and `25 13`. The former contains multiple changes with no established accessory-presence interpretation. The latter provides a compact candidate:

| Session | Key `25 13` data bytes (after key, before checksum) | Count |
| --- | --- | ---: |
| Earlier settings capture 01 | `03 00 11 00 19 00 00` | 5 |
| Amplifier-connected capture 10 | `03 02 11 02 19 00 00` | 5 |

Zero-based payload offsets 1 and 3 each acquire bit `0x02`. This is an observed correlation, not proof of two independent music-presence flags. The same pair remains `02` throughout later valid display sessions with the amplifier connected, including changes between Bluetooth and both line inputs. Captures 08–09 have `03 00 01 00 19 00 00`; offset 2 therefore varies independently and cannot be assigned solely from the amplifier comparison.

The candidate appears in 28 saved packet files. During populated Bluetooth playback, payload offset 5 also takes `02`, giving `03 02 11 02 19 02 00`. Thus this block may mix capabilities with runtime state; not every bit should be interpreted as installed hardware.

Earlier capture metadata does not uniformly verify amplifier absence, and captures differ in other system state. Historical web snapshots also reported amplifier presence before the explicit amplifier-connection experiment. Treat the early-versus-late contrast as a candidate locator, not a controlled absent/present proof.

Next discriminating experiment: record the display link continuously while disconnecting and reconnecting only the amplifier, keeping other hardware fixed and noting Music visibility. Correlate `25 13` and other state changes with disappearance/reappearance. This passive experiment can be done before emulator hardware is ready. Emulator follow-up: vary the two correlated `0x02` bits independently to establish which controls music visibility and whether the other reports status. Once the K-99701 arrives, repeat the same comparison for lighting, using the candidate block as a starting point rather than assuming the bridge or chromatherapy uses the same bits.
