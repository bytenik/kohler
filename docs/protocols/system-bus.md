# DTV+ RJ45 system protocol

Status: partial specification from passive captures, 2026-10-18. Applies to the
K-99695D-NA with the captured display and speaker amplifier. No active controller
implementation has been validated. Steam, room-light bridge and Konnect traffic
are not specified here.

## 1. Physical interface

Numbers are terminal labels on the passthrough breakout, not an independently
verified socket-contact drawing.

| Terminals | Function | Evidence |
| --- | --- | --- |
| 3 / 6 | Bidirectional differential serial data | Valid display and amplifier packets captured |
| 4 / 5 | Candidate +12 V supply | Equal measured voltage; about 12 V relative to terminal 7 |
| 7 / 8 | Candidate supply return | Equal measured voltage |
| 1 / 2 | Unknown | No function established |

The electrical standard is not confirmed. RS-485/RS-422-like levels were observed;
no transceiver identification, termination or common-mode compliance test exists.
This is separate from the controller's Ethernet network port.

| Phase/device | Baud | UART |
| --- | ---: | --- |
| Discovery, display and amplifier | 57600 | 8N1 |
| Display operation | 115200 | 8N1 |
| Amplifier operation | 57600 | 8N1 |

Later recordings decode with negative `V(3)−V(6)` representing logical one.
Earlier display recordings decode with the opposite polarity. Probe orientation
must therefore be explicit per capture; no A/B wiring designation is established.
Different operating rates and repeated address `03` on different ports favor
independent links or active routing. Internal controller topology is unknown.

## 2. Packet envelope

All offsets below refer to **unescaped bytes**, starting at zero. Hexadecimal byte
values are written without a prefix. Wire encoding:

```text
88  escaped(destination source type body checksum)  55
```

| Offset | Field |
| --- | --- |
| 0 | Start `88` |
| 1 | Destination, inferred from discovery/assignment |
| 2 | Source, inferred from discovery/assignment |
| 3 | Message type |
| 4… | Type-specific body |
| N−2 | Checksum |
| N−1 | End `55` |

Within body/header fields/checksum, literal `88`, `55`, and `AA` are encoded as
`AA 88`, `AA 55`, and `AA AA`. Delimiters themselves are not escaped.

```text
checksum = (−sum(all preceding unescaped bytes, including initial 88)) & FF
sum(packet[0:N−1]) & FF == 00
```

No universal packet length field exists. Length depends on message type and,
for display type `34`, subtype. Parsers must not infer amplifier lengths from
display layouts. Discard frames with UART errors or invalid checksums; retain
acquisition interruptions as separate segments.

Address model: controller `00`, unassigned peripheral `FF`, assigned peripheral
`03` in all observed assignments. Physical transmitter direction was not isolated;
address meanings are inferred from the following exchange.

## 3. Discovery and rate negotiation

At 57600 baud, observed unescaped packets are:

| Purpose | Packet |
| --- | --- |
| Controller discovery | `88 FF 00 05 74 55` |
| Display identity reply | `88 00 FF 06 30 01 42 55` |
| Amplifier identity reply | `88 00 FF 06 07 10 5C 55` |
| Assign display address 03 | `88 FF 00 07 03 30 01 3E 55` |
| Assign amplifier address 03 | `88 FF 00 07 03 07 10 58 55` |
| Peripheral acknowledgment | `88 00 03 35 40 55` |
| Set display rate | `88 03 00 18 00 01 C2 00 9A 55` |

The identity-byte meanings are not fully established. The amplifier's `10`
correlates with software version 0.16. The rate payload `00 01 C2 00` is big-endian
115200. The display acknowledges at 57600, then operating traffic appears at
115200 about 0.51 s later. The amplifier stays at 57600.

Empty-port discovery interval: approximately 3.07 s. Disconnect detection,
retry limits, rate-change deadline and recovery behavior remain unknown.

Evidence: captures 12 and 13, including their `-baud-analysis.json` files.

## 4. Display startup and normal exchanges

After rate negotiation, the observed startup order is:

| Controller → display | Display → controller | Function |
| --- | --- | --- |
| Type `38`, empty body | Type `39` | Startup query/reply; body meanings unknown |
| Type `33`, empty body | Type `32` | Identity, including `un-named UI` |
| Type `34`, subtype `00` | Type `35` | Initialization / acknowledgment |
| Type `30` | Type `31` | Recurring poll / event or query reply |

Startup `34 00` total length equals `packet[6] + 8` in the captured example.
Its identity-related fields are not fully decoded; constructing a correct
initialization response from a new identity is not yet specified. Capture 07
contains example bytes and alignment analysis in the investigation history.

Normal poll: `88 03 00 30 45 55`, approximately every 50 ms.
Empty reply: `88 00 03 31 00 44 55`.

### Type 31 display request/event layout

| Offset | Field |
| --- | --- |
| 4 | Class: `02` read/query, `01` write/event; `00` empty reply |
| 5 | Format: `01` in one-byte controls, `02` numeric/block, `04` text examples |
| 6–7 | Two-byte key, preserved as a byte pair |
| 8 | Count in captured write/event messages |
| 9…N−3 | Write/event value; query trailing fields are not fully specified |

### Type 34, subtype 01 controller response

| Offset | Field |
| --- | --- |
| 4 | Subtype `01` |
| 5 | Length field: total unescaped length = this byte + 8 |
| 6 | Class/format marker, commonly `02`; full semantics unknown |
| 7–8 | Key |
| 9…N−3 | Data |

Read responses echo the query key. A common acknowledgment to music events is
`88 03 00 34 01 02 02 30 0C 55`; it does not echo each individual event key.
This is an observed acknowledgment form, not proof that an action succeeded.

## 5. Display keys

### Music events

These use class `01`, format `01`, count `01` unless otherwise noted.

| Key | Meaning | Observed values |
| --- | --- | --- |
| `30 80` | Absolute volume | 35, 60; complete range unknown |
| `30 82` | Source | `00` Bluetooth, `01` Line In 2, `02` Line In 1 |
| `30 83` | Track navigation | `01` next, `FF` previous, `00` neutral/reset |
| `30 84` | Playback request | `01` play, `02` pause |
| `30 85` | Unresolved play-associated event | `00` |
| `30 86` | Balance slider value | Absolute display value; limits/physical pan mapping unknown |
| `30 87` | Treble slider value | Absolute display value; limits/dB mapping unknown |
| `30 88` | Bass slider value | Absolute display value; escaped key byte on wire |
| `30 8A` | Unresolved Bluetooth-associated event | `00` |

Display-side mute encoding has not been isolated. Amplifier-side mute is known
(section 6). Do not substitute one interface's field encoding for the other.

### Music state: key 24 69

For subtype `34 01`, data starts at complete packet offset 9. Example:
`0A 01 00 03 00 00 00 32 32 1E 23`.

| Data offset | Packet offset | Meaning |
| --- | --- | --- |
| 0 | 9 | `0A`; unresolved prefix |
| 1 | 10 | Playback: `00` inactive/transition, `01` playing, `02` paused |
| 2 | 11 | Source, same observed enumeration as `30 82` |
| 3–6 | 12–15 | Unresolved status/flags |
| 7 | 16 | Balance display value |
| 8 | 17 | Treble display value |
| 9 | 18 | Bass display value |
| 10 | 19 | Volume |

### Text responses

| Key | Meaning |
| --- | --- |
| `22 01`…`22 06` | Preset 1…6 names |
| `22 0D` | Artist |
| `22 10` | Song title |
| `22 13` | Paired device name |

Captured text is NUL-terminated ASCII-compatible data. Unicode, maximum lengths
and truncation are unknown. Fixed menu labels and layouts were not observed as
text transfers. Input selection correlates with transport controls appearing or
disappearing; the display-local visibility rule has not been actively verified.

### Housekeeping and capability candidates

| Key | Finding | Unknown |
| --- | --- | --- |
| `31 17` | Class `01`, format `02`, count `02`; big-endian counter increments about once per second | Clock/heartbeat semantics |
| `30 00` | Periodic/context-related event, including values `00`, `09`, `14` | Meaning |
| `25 13` | Data `03 00 11 00 19 00 00` in early sessions, `03 02 11 02 19 00 00` with amplifier connected | Capability/status bit meanings; causal availability test pending |

`25 13` data offset 5 can also become `02` during playback. This is not established
as a presence-only block. No lighting, chromatherapy or steam availability bit
has been identified. Other unassigned `20 xx`, `24 xx`, `25 xx` state keys remain
in the packet evidence; none is assigned a feature solely by its numeric value.

## 6. Amplifier protocol variant

Same envelope, escaping and checksum; 57600 8N1. Different message layouts:

| Request | Reply | Size |
| --- | --- | --- |
| `88 03 00 33 00 1E 24 55` | Type `32` | 30-byte body, 38 total |
| `88 03 00 30 00 CC 79 55` | Type `31` | 204-byte body, 212 total |
| Type `34`, 30-byte settings body | `88 00 03 35 40 55` | Write acknowledgment |

Offsets 4–5 encode the body count, big-endian. The two read types alternate
approximately every 350 ms; each repeats about every 700 ms.

### Short settings/readback body: types 34 / 32

| Complete packet offset | Field |
| --- | --- |
| 6 | Volume, unsigned |
| 7 | Unknown |
| 8 | Source: `00` Bluetooth, `01` Line In 2, `02` Line In 1 |
| 9 | Track: `00` neutral, `01` next, `FF` previous |
| 10 | Requested playback: `01` play, `02` pause |
| 11 | Mute: `00` off, `01` on |
| 12 / 13 / 14 | Balance / treble / bass, signed 8-bit |
| 15–35 | Other configuration; preserve unknown bytes |

Captured tone values support `amplifier_signed = display_value − 100` as a
candidate conversion. Full ranges, units and saturation behavior are unknown.

### Long status body: type 31

| Complete packet offset | Field |
| --- | --- |
| 6 | Reported volume |
| 7 | Unknown flag |
| 8 | Playback state: `00`, `01`, `02` |
| 9 / 10 / 11 | Balance / treble / bass, signed 8-bit |
| 12 | Mute-associated candidate |
| 13–76 | Title region, 64 bytes |
| 77–140 | Artist region, 64 bytes |
| 141–172 | Device-name region, 32 bytes |
| 173 | Version candidate `10`, matching 0.16 |
| 174… | Includes ASCII `20131031`; remaining fields unknown |

Observed strings are NUL-terminated within these regions. Requested playback
and reported playback can differ. Acknowledgments do not establish playback.

## 7. Evidence and implementation limits

| Finding | Reference captures |
| --- | --- |
| Framing, checksum, query/response keys | display-settings-01 through 03 |
| Display operating startup | display-startup-07 |
| Discovery, assignment, rate switch | system-amplifier-detection-12; system-display-detection-13 |
| Source, volume, tone, transport | system-display-* captures 14–29 and 32 |
| Text metadata | system-display-phone-name-30; system-display-track-metadata-31 |
| Amplifier fields and readback | system-amplifier-controls-34; tones-35; bass-batch-36 |
| Availability candidate | captures/reports/display-capability-comparison.json |

Evidence is organized by session under [captures/system](../../captures/system/).
[Investigation history](../investigation/system-bus-notes.md) retains measurements,
rejected hypotheses, capture-quality caveats, and chronology. Historical sections
may contain interpretations superseded by later observations; the current
specification above takes precedence.

Still unspecified: complete startup field construction, retry/timeout policy,
electrical transmit implementation, shower controls, feature availability,
steam/lighting/Konnect application protocols, multi-display synchronization,
and limits of all partially observed enumerations.
