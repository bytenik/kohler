# K-682-K RJ11 valve protocol

Status: partial specification from passive captures, 2026-10-18. Hardware:
K-99695D-NA controller and a K-682-K valve reporting error 061, stuck stepper
motor. Healthy valve operation and control commands are not specified.
This protocol is separate from the [RJ45 system protocol](system-bus.md).

## 1. Physical interface and UART

Numbers refer to labels on the shared 1–8 passthrough breakout. The valve cable
has four conductors at expected centered positions 3–6. Socket contact
orientation is not independently documented.

| Terminal | Function | Measurement relative to terminal 3 |
| --- | --- | --- |
| 3 | Candidate supply return | Reference |
| 4 | Differential data | +2.31 V DC |
| 5 | Differential data | +2.70 V DC |
| 6 | Candidate supply | +12.3 V DC |

Power/return assignments are not traced. The electrical standard is unconfirmed;
RS-485-like signaling is a candidate. Differential idle is about −0.39 V and
active levels about −2.2 / +2.4 V for `V(4)−V(5)`.

Validated UART model: **9600 baud, 8 data bits, odd parity, at least one stop bit**.
Negative differential voltage represents logical one with recorded polarity.
Exact stop-bit count remains unknown.

## 2. Packet format

| Offset | Field |
| --- | --- |
| 0–1 | Header `AA 55` |
| 2 | Role/address field: `00`, `01`, or startup `1F`; exact semantics unknown |
| 3 | Command/type |
| 4 | Payload length L |
| 5…4+L | Payload |
| 5+L | Checksum |

```text
total_bytes = 6 + L
sum(all packet bytes, including header and checksum) & FF == 00
checksum = (−sum(all preceding packet bytes)) & FF
```

No escape mechanism has been identified. Known packets fit this structure;
unobserved payloads containing header bytes have not been tested. No Modbus RTU
CRC match was found. The evidence supports a proprietary packet format.

`00` request / `01` response is a temporal protocol model, not an electrically
isolated transmitter measurement. Responses use command/type `01` even when
the request command differs; interpretation requires exchange context.

## 3. Startup sequence

Two captured starts have identical 19-packet initialization sequences before
regular polling. Times are relative to the first initialization packet, not
physical power-on.

| Time | Packet or exchange |
| --- | --- |
| 0 s | `AA 55 1F 3A 01 03 A4` |
| ~1.575, 3.150, 4.725, 6.300 s | `AA 55 1F 3A 01 01 A6`; no intervening replies observed |
| ~7.875 s onward | Seven request/reply exchanges below |
| ~11.960 s | Recurring status polling begins |

The `1F 3A` role, `03`→`01` payload change, and any address-assignment meaning
remain unknown. Request packets in the following table have role `00`, the
listed command, zero payload length and the additive checksum. Replies have
role `01`, command `01`, and the listed payload.

| Order | Request command | Reply payload | Meaning |
| --- | --- | --- | --- |
| 1 | `54` | `00 06 00 0C` | Candidate outlet count/version: six outlets, version 0.12 |
| 2 | `40` | `00 02 51 17` | Unknown |
| 3 | `54` | `00 06 00 0C` | Same response as first read |
| 4 | `16` | `03 09 00 04` | Unknown |
| 5 | `0B` | `01 02 00 64 00 C8 01 2C 01 2C` | Unknown |
| 6 | `0C` | `02 01 00 3F 00 02 76 00 00 01 5C` | Unknown |
| 7 | `15` | `B2` | Candidate calibration read: 178 in controller UI |

Observed request-start to reply-start intervals are approximately 12–23 ms.
These are measurements, not established timeout requirements. Multi-byte numeric
endianness and field boundaries remain unknown except for the one-byte
calibration correlation.

## 4. Recurring status

| Role | Complete packet |
| --- | --- |
| Request/poll | `AA 55 00 01 00 00` |
| Fault-state response | `AA 55 01 01 02 80 3D 40` |

Poll interval: approximately 525 ms. Response data `80 3D` correlates with
controller diagnostics `DTV Error: 061 Motor Stuck Fast Error` and fatal flag 1.
`3D` equals decimal 61; its interpretation as error ID is a strong candidate.
Meaning of `80` and a healthy-state response are unknown.

## 5. Configuration and write commands

The connected valve appears as Valve 2, six outlets, software 0.12, calibration
178. Request `15` returns `B2`, matching 178, in both startup captures.

The web interface was used to attempt calibration 178 → 179 → 178. Every saved
controller readback remained 178. Valve captures contained only the recurring
poll/status exchange: **no accepted write, write command or write acknowledgment
has been identified**. The fault may inhibit writes; that cause is unconfirmed.

No commands have been actively injected on this bus. Temperature, outlet,
flow, shutdown, fault reset and other operating commands remain unknown.

## 6. Evidence

| Reference | Finding / limitation |
| --- | --- |
| valve-idle-01 | UART and recurring fault-state packets; transfer interruption preserved |
| valve-startup-02 | Probe detachment; excluded as continuous startup reference |
| valve-startup-03 / 04 | Identical startup bytes/order; 9600 odd-parity packet validation |
| valve-calibration-05 / 06 | Attempted edit did not establish a write |
| captures/network/valve-ui-correlation.json | Controller UI/version/calibration/fault correlation |
| captures/reports/valve-startup-comparison.json | Repeatability comparison |

Sessions are under [captures/valve](../../captures/valve/).
[Investigation history](../investigation/valve-bus-notes.md) retains complete
measurements, timing, experiment annotations and unresolved interpretations.
