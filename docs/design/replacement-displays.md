# Replacement displays

## Selected design

Build custom portrait touch displays in replacement enclosures that retain the Kohler mounting footprint. Each prototype uses a Riverdi **SM-RVT35HHBFWCA0**, the **framed, air-bonded aTouch** model, connected locally to an ESP32 DevKitC. The frame adds mounting ears for mechanical retention inside the case. A printed bezel surrounds the smaller display; a continuous glass front is not required. The sealed original Kohler display is replaced as a complete assembly.

The first milestone is one dry-bench display with working portrait rendering and touch. The eventual installation has two displays, one valve and steam. Music, chromatherapy and floor-heating controls can use Home Assistant, including the existing bathroom Sonos, without emulating the corresponding Kohler display accessories. Valve and steam communication remain separate protocol work.

The connection between replacement display nodes and the central controller is an open design decision. The short SPI wiring below is local to each display; it does not establish SPI operation over the existing in-wall cable.

## Hardware and purchase status

| Quantity | Part | Status and purpose |
| --- | --- | --- |
| 1 | ESP32 DevKitC | Already available; prototype host |
| 1 | [Riverdi SM-RVT35HHBFWCA0](https://riverdi.com/product/eve4-intelligent-display-rvt35hhbfwca0-3-5-inch-projected-capacitive-touch-panel-air-bonding-atouch-frame) | Selected framed aTouch display; listed USD 89.34 |
| 1 | [Riverdi BREAK OUT BOARD 20](https://www.mouser.com/en/ProductDetail/Riverdi/BREAK-OUT-BOARD-20?qs=7D1LtPJG0i0nKgSxeAMfVQ%3D%3D), Mouser 166-BREAKOUTBOARD20 | Passive 20-pin, 0.5 mm FFC to 2.54 mm header adapter; listed USD 4.11 |
| 1 optional spare | [Riverdi FFC0520150](https://riverdi.com/product/ffc0520150) | 20-pin, 0.5 mm, 150 mm ribbon; listed USD 1.20. The breakout kit documentation includes one ribbon |
| 1 pack of 5 | [ProCircFix 3.3V-DC buck regulator, ASIN B0FP2TLXYW](https://www.amazon.com/dp/B0FP2TLXYW) | **Ordered 2026-10-19**; one module supplies display logic. Replaces the Adafruit 2745 proposal |
| 1 if needed | Regulated 5 V/2 A supply and matching terminal adapter | Display backlight supply and buck-regulator input |
| As needed | Breadboard, jumper leads and header strips | Short bench connections |

Prices are research snapshots, not current checkout quotes. Only the regulator purchase is recorded as confirmed; display and accessory purchases are not recorded. The selected framed display costs USD 2.08 more than the previously discussed USD 87.26 frameless aTouch.

The [breakout kit manual](https://riverdi.com/wp-content/uploads/2016/01/Break_Out_Board_20_Rev.1.1.pdf) documents the included ribbon. The adapter is passive: verify its header mapping and ribbon contact orientation against the display pinout before applying power.

No UART expansion, differential transceiver, separate touch-interface board or logic-level shifter is required for this display-only prototype.

## Power and wiring

The module contains a BT817Q EVE4 graphics controller and an ILI2132A touch controller. The ESP32 talks to the BT817Q over SPI; touch reports use that same host interface.

Use the external 5 V supply for the backlight and the buck-regulator input. Feed the regulator's 3.3 V output only to the display logic supply. Power the DevKitC from its normal USB connection and join the grounds. Do not join independent 5 V sources or connect the external regulator output to the DevKitC's 3.3 V rail.

RiBUS pin numbers below are from the exact framed-module datasheet, not the Kohler connector or the breakout's unverified header numbering.

| RiBUS pin | Signal | Prototype connection |
| --- | --- | --- |
| 1 | VDD | Dedicated regulated 3.3 V |
| 2 | GND | Common ground |
| 3 | SCLK | ESP32 SPI clock |
| 4 | MISO / IO1 | ESP32 SPI MISO |
| 5 | MOSI / IO0 | ESP32 SPI MOSI |
| 6 | CS | ESP32 chip select |
| 7 | INT | ESP32 input; active low |
| 8 | RST / PD | ESP32 output; active low |
| 9 | GPIO0 | Unused initially |
| 10 | DISP_AUDIO | Unused; Sonos supplies audio |
| 11–12 | GPIO1 / IO2, GPIO2 / IO3 | Unused in single-channel SPI |
| 13–16 | NC | Leave unconnected |
| 17–18 | BLVDD | 5 V backlight supply |
| 19–20 | BLGND | Common ground |

All host logic is 3.3 V. Use SPI mode 0, short jumper runs and a conservative initial clock. ESP32 GPIO assignments remain to be selected. INT and RST/PD have internal 47 kΩ pull-ups according to the module specification.

Display logic consumption is specified as 104 mA typical with audio off; the documented audio-on measurement reaches 398 mA. The backlight uses 135 mA at 5 V/full brightness. These measurements do not establish startup transient limits.

The ordered regulator is advertised as fixed 3.3 V ±0.1 V output, 4.5–24 V input, up to 1.8 A and less than 30 mV ripple. These are seller claims. Use 5 V input for the prototype. Check output voltage with the multimeter and startup/ripple with the AD3 before attaching the display, then repeat under display load. The backlight remains on the 5 V rail.

## Portrait rendering and firmware

The BT817Q supports portrait rendering. After normal Riverdi module initialization, `CMD_SETROTATE(2)` selects portrait and `CMD_SETROTATE(3)` selects inverted portrait. The logical resolution becomes **240 × 320**. The command updates both display orientation and the touch transform; writing `REG_ROTATE` directly does not update the touch transform.

The driver must implement Riverdi's panel initialization and the module-specific touch configuration. Riverdi references its public [riverdi-eve library](https://github.com/riverdi/riverdi-eve). ESPHome integration requires an external component unless an existing compatible implementation is selected and validated. No replacement-display firmware has been implemented.

Bench sequence:

1. Verify regulator output, ribbon orientation, adapter mapping and both display supply rails.
2. Connect the module to the DevKitC and establish BT817Q communication.
3. Initialize the panel and touch controller; draw text and buttons in portrait.
4. Log touch coordinates and verify all corners, button hits and both portrait orientations.
5. Exercise brightness control and repeat power checks under load.
6. Validate wet-touch behavior and the enclosure separately before duplicating the assembly.

Portrait command reference: [BT81x programming guide](../../research/display-fit/bt81x-programming-guide-displayone.pdf), BRT_AN_033 v2.2, section 5.61, page 159.

## Mechanical fit and carrier

Use the **framed aTouch drawing**, [RVT35HHBFWCA0 Rev.1.4](../../research/display-fit/riverdi-atouch-frame.pdf), page 6. Product-summary dimensions are inconsistent with the exact drawing and must not drive the carrier design.

| Dimension | Selected framed aTouch |
| --- | --- |
| Complete envelope including mounting ears, landscape | 93.50 × 64.70 mm |
| Complete envelope, portrait | **64.70 wide × 93.50 tall mm** |
| Maximum module depth, before external cable and enclosure | 12.78 mm |
| Mounting holes | Four, 3.50 mm diameter |
| Hole center spacing, portrait | 54 × 86 mm |
| Cover glass, landscape | 76.70 × 63.70 mm; 1.1 mm thick |
| Active LCD, portrait | 52.56 × 70.08 mm |

The active LCD center is offset 2.27 mm from the frame-envelope center across its short dimension. Center the **active LCD**, rather than the frame, on the replacement face.

On a nominal 84 × 130 mm Kohler-sized face, this leaves 11.92 mm and 7.38 mm between the frame envelope and the side edges, swapped for the opposite portrait orientation. Top and bottom margins are 18.25 mm. The centered active LCD occupies x = 15.72–68.28 mm and y = 29.96–100.04 mm, measured from the face's upper-left corner. Thus the selected module, including its ears, fits within the face outline on paper.

This is an outline comparison, not confirmation of bracket fit. The [K-99693 drawing](../../research/display-fit/kohler-display.pdf) gives a front face of 84 × 130 mm, rear-body width of 75 mm and overall depth of 27 mm. The [K-99694 bracket drawing](../../research/display-fit/kohler-mount.pdf) gives an outside envelope of 84 × 143 mm and depth of approximately 19 mm at the top and 25 mm at the bottom. Its 68 mm wall-screw spacing is **vertical**, not a cavity-width measurement. Internal clearance and latch intrusions are not dimensioned.

Carrier measurements still required:

- Minimum inside width at the top, middle and bottom, plus usable inside height.
- Available depth from the intended face plane to bracket obstructions and screw heads.
- Top-hook positions, width, thickness and projection.
- Bottom-latch geometry, engagement and release access.
- Cable-entry position, opening size and ribbon/connector clearance.
- Flat sealing land around the opening.

Attach the metal ears to internal carrier bosses, preferably with threaded inserts and suitable screws/washers. Keep fasteners behind the sealed front. Use spacers or mechanical stops to control compression without loading the glass. Screw lengths depend on the final carrier stack-up. Retaining the existing hooks and latch requires the measurements above; the Riverdi frame itself does not mate with them.

## Sealing and wet operation

The aTouch model is intended for integration behind a bezel. Its frame provides retention, not waterproofing. Seal the display-glass perimeter to the bezel, seal the enclosure and cable entries, and provide a seal between the replacement assembly and the wall/bracket interface.

A compatible neutral-cure electronics silicone adhesive can form the glass-to-bezel seal; a custom molded gasket is not inherently required. A removable joint can use a cut silicone-sheet gasket with controlled compression. Printed TPU can prototype gasket geometry, but material hardness, layer leakage and compression behavior require testing. Neither a printed case nor a perimeter bead alone establishes a watertight assembly.

Optical bonding is not required for the selected module's documented wet-touch capability. The air-bonded model is the selected lower-cost prototype. Its internal air gap introduces a potential condensation/fogging concern in steam service. Validate touch behavior with water films and droplets, false touches, condensation and enclosure leakage before installation or purchasing the second display. Riverdi's wet-touch claims do not establish a shower enclosure rating.

## Earlier alternatives

These are research references, not the current order list.

| Model | Reason not selected |
| --- | --- |
| Leadtek LTK035HVCCT34-V2 | Wet-hand claim and plausible size, but quotation-only procurement |
| Noritake GTWQ043C3B00PWA | Documented wet operation and portrait support, but approximately USD 394 at lookup and tight mechanical clearance |
| Riverdi RVT35HHBNWC00-B uxTouch | Optically bonded, approximately USD 106; larger overhanging glass and adhesive mounting instead of frame ears |
| Riverdi RVT35HHBNWCA0 aTouch, frameless | Approximately USD 87; the selected framed version adds mounting ears for approximately USD 2 |

The uxTouch active LCD is centered in its cover glass; the rear-body offset is not an active-area offset. The selected aTouch's offset is accounted for above. No standard publicly orderable optically bonded 3.5-inch aTouch SKU was identified. Source drawings for the earlier candidates remain under `research/display-fit/`; their dimensions must not be substituted for the selected framed model.
