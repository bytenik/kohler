# Valve bus investigation history

Historical experiment log. Interpretations may be superseded later in this file.
Current findings are consolidated in `../protocols/`; capture identifiers resolve
through `captures/path-map.json` from the repository root.

Last updated: 2026-10-18

## Scope

This document covers the RJ11 connection between the K-99695D-NA controller and K-682-K valve. It is separate from the [RJ45 system bus](../protocols/system-bus.md), which connects displays and other accessories. Overall hardware and replacement objectives are in [PROTOCOL.md](../../README.md).

## Evidence levels

- **Observed:** directly measured or validated against saved samples.
- **Hypothesis:** consistent with captures, but not independently established.
- **Unknown:** not investigated or insufficient evidence.

## Hardware and current fault

Hardware: K-682-K valve connected to the K-99695D-NA controller through RJ11.

The connected spare valve powers up and communicates. The display reports a **stuck stepper motor** error during the `valve-idle-01` recording. The later configuration-page inspection identifies this as DTV error 061; see the correlation section below. Measurements and recordings below belong exclusively to this valve interface.

### Valve electrical measurements

The shared 1–8 breakout is used with a centered four-conductor valve plug; expected occupied terminal labels are 3–6. Physical plug contact orientation remains to be documented independently.

| Black lead | Red lead | DC voltage |
| --- | --- | ---: |
| 3 | 4 | +2.31 V |
| 3 | 5 | +2.70 V |
| 3 | 6 | +12.3 V |
| 4 | 5 | +0.39 to +0.42 V, fluctuating |

**Candidate pinout:** 3 power return, 6 approximately +12 V supply, 4/5 differential data. Meter readings support this assignment, but power/return have not been independently traced. RS-485 is a physical-interface hypothesis; no driver component or electrical compliance has been identified.

### First passive valve recording

Capture `valve-idle-01` uses AD3 Scope 1+ on breakout 4 and Scope 1− on 5, all AD3 GND leads disconnected. Acquisition: 2 MS/s, 50 V input range, attenuation 1, 12-second target. A USB transfer corruption event discarded 13,718 available samples and split the recording into contiguous parts of 4.620479 and 7.372662 seconds. No decoder bridges that interruption.

The first second of each retained part shows differential idle around −0.39 V, active plateaus around −2.2 V and +2.4 V, and short excursions to approximately −2.58 V. Common edge spacings near 104 microseconds support 9600 baud.

**Validated decoding model:** 9600 baud, eight data bits, odd parity, at least one stop bit, negative differential voltage representing logical one with the recorded probe polarity. Part 000 contains 120 decoded characters with one parity/framing error outside accepted packets; part 001 contains 200 with zero errors. At the same baud, 8N1 and even-parity interpretations produced many errors. Exact stop-bit count remains unconfirmed.

`analyze_valve_uart.py` is independent of display framing. Odd-parity analysis files contain 45 accepted packets, all passing character framing and the candidate additive checksum:

| Repeating bytes | Count | Interpretation |
| --- | ---: | --- |
| `AA 55 00 01 00 00` | 23 | Candidate request/poll |
| `AA 55 01 01 02 80 3D 40` | 22 | Candidate response/status |

The first pattern repeats approximately every 525 ms. Physical transmitter identity has not been established, so request/response roles remain hypotheses.

### Candidate valve packet structure

For both observed patterns, the following model fits every accepted packet:

| Offset | Candidate meaning |
| --- | --- |
| 0–1 | Header `AA 55` |
| 2 | Direction, role, or address-like field (`00`/`01` at idle; startup also uses `1F`); unresolved |
| 3 | Command/type (`01` at idle; startup introduces other values) |
| 4 | Payload length (`00` or `02`) |
| 5 onward | Payload followed by one checksum byte |

Candidate total length is `6 + byte[4]`. The sum of every byte including header and final byte is zero modulo 256. Since the header sums to `FF`, the final byte is also `(1 - sum(bytes[2:-1])) & FF`. The first idle recording contains only two distinct messages; startup capture 03 below extends validation to 16 distinct messages with multiple payload lengths and commands.

The response's candidate payload is `80 3D`, observed while the display reports a stuck stepper motor. This correlation does not establish that either byte encodes the fault; temperature, flags, status, and numeric interpretation remain unresolved. No Modbus RTU CRC match was found on the complete candidate packets; the recognized header/length/additive-checksum structure favors a proprietary protocol over ordinary Modbus RTU. No valve command has been transmitted or replayed.

Next evidence: compare controlled configuration or status changes with packet payload changes. Startup repeatability is documented below. Record any numeric error code if one becomes visible. All valve recordings must retain the `valve-` prefix and explicit connector/pin metadata.

No display-bus pinout, baud rate, delimiter, escape rule, or checksum is assumed to apply to the valve bus. Valve captures must have separate filenames and explicitly identify connector, terminal numbering, probe polarity, and operating action.

## Startup attempt 02: probe interruption

Capture `valve-startup-02` was stopped after temporary probe-connector detachment was reported. Retained raw data and `valve-startup-02-events.json` preserve the attempt, but it is excluded as a continuous startup reference. No USB transfer interruption was reported; physical probe continuity is a separate limitation.

## Startup capture 03 (2026-10-18)

Files: `valve-startup-03-manifest.json`, `-events.json`, `-part-000.f64`, `-part-000.json`, `-part-000-uart-odd-analysis.json`, and `valve-startup-03-analysis.json`.

Recording began before the spare-system power cycle and retained 103.684070 seconds at 500 kS/s, with no reported USB loss/corruption. The probe connections remained Scope 1+ on pin 4 and 1− on pin 5, all GND leads disconnected. The power-cycle cue and subsequent user acknowledgment are host-time annotations, not measurements of power transitions. The acknowledgment does not independently timestamp the display error's appearance.

The first decoded character begins at capture-relative 47.567302 s. All 1,347 decoded characters pass the 9600-baud, 8-bit, odd-parity decoding model with negative voltage representing one. They are accounted for by 189 complete packets, spanning 16 distinct byte patterns. Every packet satisfies the `AA 55` header, `6 + byte[4]` length rule, and zero-modulo-256 additive checksum. This supports the packet structure beyond the two idle patterns. At 500 kS/s, there are approximately 52 samples per bit.

### Startup sequence

Times below are relative to the first captured packet, not the physical power-on instant.

1. At 0 s: `AA 55 1F 3A 01 03 A4`.
2. At approximately 1.575, 3.150, 4.725, and 6.300 s: `AA 55 1F 3A 01 01 A6`. No intervening reply packet is observed.
3. At 7.875 s: the first `00 54` request-like packet receives a `01 01` reply-like packet, followed by additional short exchanges in the table below.
4. At 11.960 s: recurring `AA 55 00 01 00 00` polls begin, each followed by `AA 55 01 01 02 80 3D 40`. There are 85 of each in this capture.

The repeated `1F 3A` messages may belong to discovery, initialization, or addressing. Neither a broadcast meaning for `1F` nor physical transmitter identity has been established. The `03`→`01` payload change has no assigned meaning yet.

### Startup request/reply candidates

The request-like packets have field 2 equal to `00`, no payload, and a varying field 3. The following reply-like packets have field 2 equal to `01`, field 3 equal to `01`, and the following payloads:

| Request field 3 | Time after first packet (s) | Reply payload | Request-start to reply-start (ms) |
| --- | ---: | --- | ---: |
| `54` | 7.875324 | `00 06 00 0C` | 15.450 |
| `40` | 7.902354 | `00 02 51 17` | 12.984 |
| `54` | 8.285236 | `00 06 00 0C` | 23.350 |
| `16` | 8.810236 | `03 09 00 04` | 14.468 |
| `0B` | 9.450174 | `01 02 00 64 00 C8 01 2C 01 2C` | 13.562 |
| `0C` | 9.860256 | `02 01 00 3F 00 02 76 00 00 01 5C` | 21.300 |
| `15` | 10.385268 | `B2` | 12.354 |

These are temporal associations, not independently confirmed physical directions or command semantics. Field 3 in the reply does not echo the request's varying field 3; a decoder must retain exchange context. Identification/version/configuration interpretations remain open. Numeric byte order and units are unresolved.

The final startup reply's `B2` payload belongs to a different request (`15`) from the later `80 3D` replies (`01`). It must not be treated as a changing value of the same status field. The recurring `80 3D` remains correlated with the reported stuck-stepper-motor condition, without assigning individual bits or bytes to that fault.

No active bus injection has occurred.

## Repeat startup capture 04 (2026-10-18)

Capture `valve-startup-04` uses the same pin 4/5 differential wiring, 500 kS/s acquisition, and 9600-baud odd-parity decoding. The user explicitly reported initialization complete and the stuck stepper motor error visible; the acknowledgment is retained in `valve-startup-04-events.json`.

The uninterrupted 144.438406-second recording contains 2,621 decoded characters, zero character parity/framing errors, and 371 complete packets. Every character is accounted for by a complete packet, and all packets pass the length/checksum checks. The first 58 packets are normal polling before the power cycle; the first `1F 3A` startup message occurs at capture-relative 55.357234 s. No USB loss/corruption was reported.

Comparison with startup 03:

| Observation | Startup 03 | Startup 04 |
| --- | --- | --- |
| Initialization packets before regular polling | 19 | 19 |
| Initialization packet bytes and order | Identical across captures | Identical across captures |
| Seven startup request/reply pairs | Same commands and payloads | Same commands and payloads |
| First regular poll after first `1F 3A` (s) | 11.960276 | 11.960284 |
| Regular status reply payload | `80 3D` | `80 3D` |

Thus the initial `1F 3A` payload change (`03` followed by four occurrences of `01`), request order (`54`, `40`, `54`, `16`, `0B`, `0C`, `15`), and all reply payloads are repeatable for this controller/valve in this fault condition. No changing session identifier is apparent in those bytes across these two starts. Repeatability alone does not identify version fields, configuration fields, address assignment, or fault bits, and it does not establish behavior for other valves or a healthy state.

Reproduction: `python3 analyze_valve_uart.py valve-startup-04-part-000 --parity odd`, followed by `python3 compare_valve_startup.py valve-startup-03 valve-startup-04`. Comparison output: `valve-startup-comparison.json`. The comparison separates pre-cycle polling from initialization, using the first observed `1F 3A` message as the alignment point.

Next useful evidence is a controlled change in a setting exposed by the spare system, comparison with device/version information from the controller UI, or another independently known valve state. A third unchanged startup would add little information about payload semantics.

## Configuration-page correlation (2026-10-18)

Read-only inspection of `http://192.168.2.2/service.html`, Settings → About, and the page's `values.cgi` data establishes the following current UI state. No settings were changed.

- Valve 2 is installed and connected; Valve 1 is not installed and is disconnected.
- Valve 2 has six outlets, calibration code 178, and software version `0.12`.
- The diagnostics log contains `DTV Error: 061 Motor Stuck Fast Error` for the repeated startups.
- `valve2_ErrorFatal` is 1 and `valve2_ErrorResettable` is 0.
- About also displays Valve 1 version `0.12` despite that valve being disconnected. A displayed version alone is not proof of current device presence; cached/default values are possible.

Evidence is preserved in `network/controller-values-observed.json`, `network/valve-ui-correlation.json`, the saved `controller-settings.html`/`controller-service.html`, and their page scripts under `captures/network/` and `research/controller-web/`.

| Request field 3 | Captured reply payload | UI match | Interpretation strength |
| --- | --- | --- | --- |
| `15` | `B2` | Calibration code 178 = `0xB2` | Strong candidate for reading the calibration code; only one value tested |
| `01` | `80 3D` | DTV error 061 = `0x3D` | Strong candidate for status flags plus error ID; meaning of `80` unconfirmed |
| `54` | `00 06 00 0C` | Six outlets and version `0.12` | Candidate capability/version response; exact field boundaries and number encoding unconfirmed |

The fatal flag reported by the UI is consistent with a possible flag in `80`, but there is no healthy-state comparison to establish bit 7 as the fatal bit. Likewise, matching error 61 does not map other error codes.

The diagnostics source renders the calibration field directly from `data.v2_cal_code`. Its change handler accepts decimal values 160–200 and writes web variable ID 62 (`const_six_port_calibration_valve2`); Valve 1 uses ID 61. These are web API variable IDs, not valve-bus command or address values. The UI's write path is documented from source only and was not invoked.

The next controlled correlation could compare a known device value or a reversible configuration change with the bus while capturing. Changing valve calibration affects physical operation; retain the known value 178 and establish write/restore behavior explicitly before such a test. Remaining startup replies to `40`, `16`, `0B`, and `0C` have no established semantic mapping.

## Temporary calibration-entry experiment (2026-10-18)

The spare Valve 2 calibration field was temporarily edited from 178 to 179, then restored to 178, with the stuck-stepper-motor condition still present. Two valve captures were acquired using the established pin 4/5 differential setup at 500 kS/s. No direct bus injection was used.

| Capture | Duration (s) | UART characters | Character errors | Complete packets | USB interruptions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `valve-calibration-05` | 78.925376 | 2,086 | 0 | 298 | 0 |
| `valve-calibration-06` | 49.540208 | 1,316 | 0 | 188 | 0 |

All decoded characters are accounted for by complete packets, and every packet passes length and checksum checks. Capture 05 contains 149 occurrences of each normal poll/reply; capture 06 contains 94 of each. Neither contains a different packet pattern.

The first UI edit displayed 179, but `values.cgi` still returned `v2_cal_code:178`. Capture 06 repeated the edit using individual keypresses and added an Ethernet capture to verify submission. `network/valve-calibration-06-http.pcap` and its `-analysis.json` establish both requests and their complete response bodies:

```text
GET /save_variable.cgi?index=62&value=179&_=1792353453663
Response: done

GET /save_variable.cgi?index=62&value=178&_=1792353453708
Response: done
```

The controller's `v2_cal_code` readback remained 178 after the 179 request and again after restoration. The final browser field also displays 178. The Ethernet capture reports zero kernel drops.

**Result:** the web server acknowledged both requests, but no calibration write appeared on the observed valve link. `done` is not evidence that the value reached or was accepted by the valve. No valve write command or acknowledgment can be assigned from this experiment. The current fatal fault may inhibit writes; a controller-side validation or handling issue is also possible. The reason is unresolved.

Machine-readable summary: `valve-calibration-analysis.json`. Event annotations: `valve-calibration-05-events.json` and `valve-calibration-06-events.json`. Controller readbacks are saved under `network/valve-calibration-0{5,6}-{at-179,restored}.json`. The `at-179` filenames describe the attempted entry, not a successful state change; all four readbacks contain 178.

Further write-command identification requires an accepted configuration change. A possible next experiment is submitting the edit during initialization before the fatal fault is reported, while capturing both Ethernet and the valve link; fault inhibition remains a hypothesis until such a comparison is observed.
