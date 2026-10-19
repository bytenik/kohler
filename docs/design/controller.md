# Replacement controller design and roadmap

Last updated: 2026-10-18

## Replacement objective

Replace the K-99695D-NA with an ESP32-based controller, preferably integrated with ESPHome, while operating the existing display and responding to its user interactions. The display investigation remains active until a controller emulator can initialize it, supply the state/content it needs, and process its events. Packet framing alone is not sufficient.

Immediate milestone: a display-only emulator tested with the valve disconnected. Required evidence includes startup/discovery, addressing, initialization/configuration, polling, display updates, user events, timeouts, and reconnect behavior. The physical display transmit/receive direction and identities of address fields remain to be established. The valve bus remains a separate protocol investigation, not a substitute for finishing display support.

## Scope and hardware

The replacement target is the K-99695D-NA system controller. The retained configuration is one K-682-K valve, two displays, steam, and a virtual chromatherapy light controlled from the existing displays. Music is a virtual amplifier backed by the bathroom Sonos through Home Assistant; the physical Kohler amplifier is retained only as a protocol reference. A K-99701 room-light bridge has been purchased for spare-bench investigation and is expected in a few days; it is not yet available for captures. The additional target is display control of Home Assistant devices such as floor heating, without retaining the physical bridge. A Konnect module is also available but is a distinct accessory. Display and steam adapter/generator model numbers remain unrecorded; bridge discovery, load-module registration requirements and exposed display controls require verification.

The virtual chromatherapy target is display-facing compatibility: expose the lighting feature, accept its commands, and maintain its state. A simulated light can exercise this path before connecting an RGB/RGBW light. Reproducing the discontinued rain panel's physical peripheral protocol is only required if emulating that accessory to an original Kohler controller becomes necessary for discovery; it is not inherently required for a replacement controller.

**The display bus and valve bus are separate investigations. Findings from one must not be applied to the other without measurement.**

| Interface | Connector | Investigation status |
| --- | --- | --- |
| Controller ↔ displays and accessories | RJ45 system interface | Differential serial traffic captured on breakout pins 3 and 6; UART framing and packet checksums validated |
| Controller ↔ K-682-K valve | RJ11, four conductors | Candidate supply/return on breakout 6/3; differential serial on 4/5, 9600 baud with odd parity |
| Controller home-network connection | Separate Ethernet port | Outside the bus captures documented here |

Pin numbers below are the breakout's terminal labels. Their mapping to the physical controller socket contact orientation has not been independently documented. A replacement PCB pinout must establish that mapping first.

## Protocol documents

- [System bus protocol](../protocols/system-bus.md): the RJ45 interface used by displays and other accessories, including music and steam equipment. Current captures observe display and speaker-amplifier connections; their baud rates and packet variants differ. Other accessory traffic remains uncharacterized.
- [Valve bus protocol](../protocols/valve-bus.md): the four-conductor RJ11 valve interface, candidate pinout, 9600-baud odd-parity traffic, packet hypotheses, and the stuck-stepper-motor fault condition.

Each protocol document retains its own observations, hypotheses, limitations, and next work. Capture filenames and decoder labels remain unchanged to preserve evidence provenance.

## Replacement readiness and remaining milestones

The observations support beginning a spare-bench display controller prototype with virtual music. They do not yet support operating a healthy valve. Exhaustively assigning every unused field is not a prerequisite for a prototype, but unknown values must remain explicit and preserved where required.

| Area | Established evidence | Required next evidence |
| --- | --- | --- |
| Display/system discovery | 57600-baud discovery, address assignment candidate, explicit 115200-baud display change, initialization, polling | Emulator successfully starts and services the display; reconnect and timeout behavior |
| Display state/events | Music state, source, volume, tone, transport, metadata strings; other captured state/query keys | State dictionary for retained shower features, outlet/temperature actions, availability/configuration, power and fault handling |
| Virtual amplifier / Sonos | Display music events/state and metadata captured; physical amplifier settings/status captured as reference | Home Assistant action/state bridge, volume scaling, playback and metadata feedback, reconnect behavior, source/tone mapping |
| Valve | Candidate pinout, 9600-baud odd-parity framing, repeatable initialization, fault/status and calibration-read correlations | Healthy-state interpretation, output/temperature/flow commands, configuration writes, acknowledgments, faults and communication-loss behavior |
| Two displays | One display captured; per-port address reuse observed between display and amplifier | Independent initialization of both displays, shared state synchronization, simultaneous inputs, restart/reconnect behavior |
| Steam | Controller web source exposes installed/running flags, temperature, duration and cleaning settings | Adapter/generator identity, discovery capture, commands/status, faults, timeout and shutdown behavior |
| Virtual accessory controls | K-99701 room-light bridge purchased, pending arrival; floor-heating control through Home Assistant requested | Capture bridge discovery and load registration behavior; identify exposed display controls and their events/state; map to Home Assistant |
| Virtual chromatherapy | Web source distinguishes rain-panel chromatherapy from room-light bridge; brightness/white/fade/effect settings identified | Display feature-availability fields, lighting event/state keys, effect/color encoding and synchronization across displays |
| Electrical interface | Passive differential captures and candidate power/reference pins | Confirm transceiver standard, connector orientation, driver direction/turnaround, power/reference design, termination/protection, and transmit behavior |

### Bench development sequence

1. Target one valve, two displays, steam, virtual Sonos-backed music, and virtual chromatherapy. Use the historical `25 13` capability/status candidate and a controlled amplifier disconnect/reconnect capture to narrow display feature flags, then map configuration responses to expose retained controls, including chromatherapy without a physical rain panel. Capture a second display and steam independently when spare hardware is available.
2. Select suitable controller/transceiver hardware for the ESP32 DevKitC, adding independent UART channels as needed. Provision independent serial links for the observed peripheral operating rates unless port-circuit evidence supports a different implementation.
3. Implement packet encoding/decoding and captured-message regression fixtures, then emulate the original controller for the spare display with virtual Sonos-backed music and the valve disconnected. Validate startup, periodic polling, state/text updates, user events, and reconnection.
4. Emulate a valve on the spare original controller's valve port, with the real valve disconnected. Explore candidate nonfault status/identity responses and observe whether the original controller enables shower controls and emits new commands. This can reveal controller intent without exercising a real valve; it cannot establish physical valve behavior by itself.
5. Validate valve commands and failure handling on a healthy valve in a suitable bench setup before using a replacement controller for water control. Establish output closure, temperature/outlet behavior, watchdogs, and response to controller restart or lost communications. The broken valve's stuck-motor state cannot supply this evidence.
6. Integrate the validated state machine with ESPHome and test the retained system configuration. Keep protocol handling and autonomous shutdown behavior functional independently of Home Assistant connectivity.

Open questions: display and steam hardware model numbers; spare-bench availability of the second display and steam adapter; transceiver and UART-expansion selection; access to a healthy spare valve or another source of independently verified healthy-valve behavior. All current hardware experiments remain on the spare system.


## Controller and serial expansion

The selected controller is an ESP32 DevKitC. The intended physical links are two
displays, one valve and steam; steam compatibility remains to be measured. Music
uses a virtual amplifier backed by Sonos through Home Assistant. Chromatherapy
and room-device controls are also virtual features and need no physical UART.

UART expansion remains a hardware choice. Two dual-channel expansion boards can
provide four additional ports while retaining USB serial diagnostics. The
Waveshare Serial Expansion HAT uses an SC16IS752 over I²C, not SPI; software,
buffering and RS-485 direction timing need validation. The board does not replace
the differential transceivers. No emulator firmware has been implemented yet.
