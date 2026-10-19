# Replacement display research

Replacement-display design and hardware research; separate from the original Kohler wire protocols.

Current prototype: framed air-bonded aTouch SM-RVT35HHBFWCA0 with the existing ESP32 DevKitC. The ProCircFix 3.3V-DC regulator pack (Amazon ASIN B0FP2TLXYW) was ordered on 2026-10-19. Display and other accessory order status is unconfirmed.

## Custom display feasibility: wet-touch candidate

Replacing the sealed Kohler displays is an alternative under evaluation, not yet a committed architecture change. A replacement must fit the existing mounting footprint and provide its own enclosure/seals; the factory-sealed original display is not assumed reusable.

Candidate: [Leadtek LTK035HVCCT34-V2](https://www.leadtekdisplay.com/35-inch-tft-lcd-module-p-2899.html), 3.5-inch 320×480 TN panel, specified overall dimensions 69.50 × 116.50 × 4.17 mm, glass/glass capacitive touch, ILI9488 over SPI and GT911 over I²C. The manufacturer explicitly claims wet-hand touch. Its quoted operating range is −10 to +60°C. The bare module fits within the K-99693 published outer envelope of approximately 84 × 130 mm; this is not confirmation of mounting, gasket, cable-fold or electronics clearance.

ESPHome provides [ILI9488 display support](https://esphome.io/components/display/mipi_spi/) and [GT911 touch support](https://esphome.io/components/touchscreen/gt911/). This establishes a driver path, not tested support for the exact panel assembly. Panel initialization, power/backlight circuitry, FPC pinout and touch configuration still need confirmation.

Procurement is by quotation; sample price, minimum quantity and availability are unknown. Before ordering, obtain the exact V2 mechanical/electrical drawings, sample terms and evidence of wet-touch performance including water-film false-touch behavior. Wet-hand support does not establish operation under continuous spray, soap, steam condensation or an enclosure IP rating. A complete replacement requires perimeter and cable-entry sealing and environmental validation.

### Direct-order wet-touch candidate: Noritake GTWQ043C3B00PWA

[Mouser listing](https://www.mouser.com/ProductDetail/Noritake/GTWQ043C3B00PWA?qs=doiCPypUmgEmeOB7ZvsnQQ%3D%3D) reports single-unit ordering at USD 394.18 and five immediately available units at the research check; stock and price remain subject to checkout confirmation. The listed module size is 108 × 80 × 9.5 mm. Rotated into portrait, its 80 × 108 mm footprint is within the published K-99693 outer envelope, but only 4 mm narrower overall; mounting, connector and gasket clearance remain unresolved.

The [manufacturer product page](https://www.noritake-elec.com/products/model?part=GTWQ043C3B00PWA) specifies 4.3 inches, 480×272, 5 V supply and CMOS UART/SPI/I²C/USB command interfaces. The [GT-CP series page](https://www.noritake-elec.com/products/lcd-touch-screen/gt-cp) explicitly describes operation with cover glass, gloves and water spillage. The manufacturer also provides a [water-spray demonstration](https://www.noritake-elec.com/support/videos/video?id=VsAUjVuM3xw). The series application note APN800 section 5.2.6 documents water-related limitations, tuning and layout guidance; wet operation is conditional, not an unconditional shower guarantee.

This is a command-controlled display, rather than a raw ILI9488/GT911 module. No built-in ESPHome GT-CP driver was identified in the published component catalog. Integration would require an external component implementing the documented command and touch-report interface. Rendering can use module drawing/text commands and stored assets; direct LVGL integration must not be assumed. This candidate meets public direct-order availability and documented wet-touch requirements, but exact mount fit and ESPHome operation remain unvalidated.

### Mechanical and portrait review of Noritake candidate

Full hardware and software specifications and Kohler bracket/display drawings are saved under `research/display-fit/`. The portrait setting is established, but reuse of the original bracket is not dimensionally confirmed.

- Noritake hardware specification DS-2122-0001-01, page 22: PCB 108.0 ±0.7 × 80.0 ±0.7 mm; thickness 9.5 ±0.5 mm before host connectors, cover overlay or carrier. In portrait the nominal footprint is 80 × 108 mm, with maximum width 80.7 mm. Mounting-hole center spacing is 102 × 74 mm (74 × 102 mm in portrait). Active LCD area in portrait is 53.86 × 95.04 mm.
- Kohler K-99693 specification drawing: front 84 × 130 mm, rear body width 75 mm, overall depth 27 mm. The 84 mm dimension is the front face, not the rear-body clearance. The candidate PCB is nominally 5 mm wider than the original rear body.
- Kohler K-99694 bracket drawing: outer dimensions 84 × 143 mm; depth approximately 19 mm at the top and 25 mm at the bottom; wall screw spacing 68 mm vertically. These are not dimensioned usable internal cavity measurements. The installation guide shows top hooks and a bottom latch. Internal width, latch intrusions and internal depth are not dimensioned. The 68 mm screw spacing is not a cavity-width measurement.
- Compared with the 84 mm outside width, the maximum-width candidate leaves only 3.3 mm total before accounting for bracket walls, carrier or seals. This cannot establish that it fits inside the bracket. Compared with the 130 mm face height, the maximum 108.7 mm board length leaves 21.3 mm overall.
- Noritake serial and power connections can use rear through-holes CN9 rather than the edge USB connector. A low-profile soldered harness may reduce connector protrusion; its actual depth and routing require a carrier layout. The 9.5 mm panel thickness alone does not establish installed depth. A separate protective nonconductive overlay is required by hardware specification section 9.

Portrait: software specification section 3.2, page 9 and section 4.2, page 96 establish Memory SW 6 settings 01h for 90° and 03h for 270°. The display area becomes 272 × 480 pixels (table on page 7). Firmware history, page 98, dates this function to F200b or later; firmware on the delivered unit remains a procurement/bench check. Touch-coordinate correspondence must be checked during bring-up.

Conclusion: documented portrait rendering; plausible custom front assembly within the wall footprint; no confirmed direct insertion into the existing Kohler bracket. The next fit check is the removed bracket's minimum clear width, available front-to-back clearance, top-hook and bottom-latch geometry. A dimensionally accurate dummy board can validate fit before purchasing the display. A custom carrier may need to place the PCB forward of the bracket rather than inside its original rear-body envelope.

## Riverdi RVT35HHBNWC00-B: mechanical and portrait review

The USD 106.25 optically bonded uxTouch model is a stronger cost/size candidate than the Noritake. Its mechanical drawing supports a custom replacement face within the original wall footprint; direct compatibility with the original bracket latches remains unverified.

### Mechanical evidence

Source: `research/display-fit/riverdi-rvt35hhbnwc00-b.pdf`, Rev.1.7, page 6 (module drawing), page 5 (assembly) and pages 15–16 (touch specifications).

- Cover glass: 93.96 × 76.44 mm, 1.1 mm thick, four R3.50 mm corners. In portrait the full glass outline is 76.44 mm wide × 93.96 mm tall. These dimensions include the overhanging cover glass; they are not merely PCB dimensions. Drawing default tolerance is ±0.3 mm unless individually specified.
- Maximum complete module depth: 12.00 mm before external cable routing, enclosure and seals.
- TFT outline: 77.00 × 63.89 mm; in portrait 63.89 mm wide × 77.00 mm tall. Cover-glass viewing window: 70.68 × 53.16 mm; active LCD area: 70.08 × 52.56 mm.
- Rear host interface: RiBUS 20-pin, 0.5 mm pitch, underside-contact flip-lock FFC connector P1. Ribbon bend/exit clearance must be included in the carrier layout. Speaker connection is unnecessary for the proposed Sonos backend.
- uxTouch is designed for adhesive attachment by its extended glass. The drawing identifies 3M9485 double-sided adhesive, thickness 0.175 mm. No Kohler-compatible hooks or latch are present. Adhesive mounting alone does not establish a watertight enclosure.

Kohler comparison from the saved K-99693 and K-99694 drawings:

| Item | Width × height | Implication |
| --- | --- | --- |
| Original display face | 84 × 130 mm | A custom face can retain this outline |
| Original rear-body width | 75 mm | Not the same as usable bracket cavity width |
| Original bracket outside | 84 × 143 mm | Existing wall footprint can be retained with a suitable adapter |
| Riverdi glass, portrait | 76.44 × 93.96 mm | Within original face, nominal 3.78 mm per side and 18.02 mm top/bottom if centered |
| Riverdi TFT, portrait | 63.89 × 77.00 mm | TFT is narrower than original rear body; rear PCB, connector and latch clearances still require verification |

The compact module cannot directly substitute for the original 130 mm-tall hooked/latching display. Use a custom carrier/front assembly to bridge the original mount, support the glass, route the FFC and provide sealing. Existing bracket internal dimensions are not provided by the published drawing. Measure the bracket/latch geometry or fit a dummy before deciding whether to retain its original latches or attach a replacement carrier using the existing wall fixings.

### Portrait rendering

Source: `research/display-fit/bt81x-programming-guide-displayone.pdf`, Bridgetek BRT_AN_033 Version 2.2, section 5.61/page 159 and register definition/page 30.

The BT817Q supports portrait rendering in hardware. `CMD_SETROTATE(2)` selects portrait and `CMD_SETROTATE(3)` selects inverted portrait. Logical layout becomes 240 × 320 for this 320 × 240 panel. The command adjusts the touch transform matrix as well as the displayed orientation; writing `REG_ROTATE` directly does not adjust touch transforms. Riverdi's module datasheet section MODULE INITIALIZATION states that native touch/display orientation and resolution already match and supplies initialization values and a reference to its public `riverdi-eve` library. Apply normal panel initialization first, then the chosen display rotation, and verify touch coordinates on the bench.

Conclusion: portrait is documented, and the complete glass outline is inside the original display face. A custom carrier is required; exact fit into the existing bracket cavity, cable clearance, environmental sealing and ESPHome integration remain unvalidated.

## aTouch availability and active-area centering review

The requested 3.5-inch optically bonded aTouch SKU has not been identified in the public Riverdi catalog, checkout listings or download index. The public aTouch SKU RVT35HHBNWCA0 is air-bonded and listed at USD 87.26. Optical bonding is confirmed for uxTouch RVT35HHBNWC00-B at USD 106.25. An optically bonded aTouch option must not be assumed available as a standard orderable part.

Sources: [aTouch checkout listing](https://riverdi.com/product/eve4-intelligent-display-rvt35hhbnwca0-3-5-inch-projected-capacitive-touch-panel-air-bonding-atouch), [aTouch mechanical datasheet](https://download.riverdi.com/RVT35HHBNWCA0/DS_RVT35HHBNWCA0_Rev.1.4.pdf), and [uxTouch mechanical datasheet](https://download.riverdi.com/RVT35HHBNWC00-B/DS_RVT35HHBNWC00-B_Rev.1.7.pdf). Local copies and rendered drawings are in `research/display-fit/`.

### aTouch: centered-screen fit for the available air-bonded model

The Rev.1.4 mechanical drawing, page 5, specifies a 76.90 × 63.90 mm module and 76.70 × 63.70 mm cover glass. Its active LCD area is 70.08 × 52.56 mm, starting 3.41 mm from the left and 3.40 mm from the top of the landscape TFT outline. Therefore its active center is (38.45, 29.68) mm, compared with the module center (38.45, 31.95) mm. The active LCD is offset by 2.27 mm toward one short edge of the module.

In portrait, with the active LCD centered on an 84 × 130 mm Kohler-sized face, the nominal module edges can be placed at x = 12.32 and 76.22 mm, y = 26.55 and 103.45 mm. The lateral outer margins are therefore 12.32 and 7.78 mm, or swapped for the opposite portrait orientation. The top and bottom margins are 26.55 mm. The visible active LCD edges are x = 15.72 and 68.28 mm, y = 29.96 and 100.04 mm. Nominal module depth is at most 12.25 mm before the external ribbon, carrier and sealing.

This establishes that active-area centering fits within the original face rectangle for the air-bonded model; it does not establish installed bracket, connector or gasket clearance. Public product-summary dimensions for aTouch appear copied from uxTouch; use the exact aTouch mechanical drawing rather than those summary dimensions.

### uxTouch: active LCD is centered in cover glass

The Rev.1.7 drawing of RVT35HHBNWC00-B, page 6, specifies cover glass 93.96 × 76.44 mm and active LCD area 70.08 × 52.56 mm with a 11.94 mm border on every side. Its active-area center is exactly the glass center: 46.98 × 38.22 mm. Centering its glass in an 84 × 130 mm portrait face also centers the active LCD. The TFT/body offset and rear electronics do not establish an active-area offset.

The aTouch model's smaller outline permits a smaller carrier opening. The optically bonded uxTouch model remains a viable standard option if optical bonding is required; its screen-centering geometry is not a reason to reject it. Neither candidate is a confirmed direct replacement for the original bracket latch geometry.

## Selected first prototype and order list

The selected prototype is one framed air-bonded aTouch SM-RVT35HHBFWCA0 connected to the existing ESP32 DevKitC. Begin with a dry-bench display/touch prototype before enclosure fabrication.

| Quantity | Part | Purpose |
| --- | --- | --- |
| 1 | SM-RVT35HHBFWCA0 | Selected framed display, public Riverdi price USD 89.34; order status unconfirmed |
| 1 | Riverdi BREAK OUT BOARD 20, Mouser 166-BREAKOUTBOARD20 | Assembled passive 20-pin 0.5 mm ribbon to 2.54 mm header breakout; Mouser listing USD 4.11, 23 available at lookup |
| 1 optional spare | Riverdi FFC0520150 | Matched 20-pin 0.5 mm, 150 mm ribbon, USD 1.20; breakout kit documentation includes one ribbon |
| 1 pack (5 modules) | ProCircFix 3.3V-DC buck regulator, Amazon ASIN B0FP2TLXYW | Ordered 2026-10-19; use one module for the display logic supply. Replaces the previously proposed Adafruit 2745 |
| 1 if not already available | Regulated 5 V/2 A supply with accessible output adapter | Backlight and buck input; not connected to DevKitC USB 5 V during computer-powered development |
| As needed | Breadboard, 2.54 mm jumper leads, header strips | Connect breakout, regulator and DevKitC |

Power: display RiBUS pin 1 receives regulated 3.3 V; pins 17/18 receive 5 V for the built-in backlight driver; pin 2 and pins 19/20 share ground with the ESP32. The dedicated regulator output supplies only the display, not the DevKitC 3.3 V rail. Leave the ESP32 on its normal USB connection. Display logic is specified at 104 mA typical with audio off and 398 mA maximum in the documented audio-on measurement; backlight draws 135 mA at 5 V/full brightness. The ordered regulator is advertised as fixed 3.3 V output (±0.1 V), 4.5–24 V input, up to 1.8 A, and less than 30 mV ripple. These are seller specifications, not measured performance. Use 5 V input for this prototype. Verify output voltage with the multimeter and startup/ripple with the AD3 before connecting the display; repeat the check under display load during bring-up. The backlight remains on the separate 5 V rail.

SPI mode 0 uses pins 3 SCLK, 4 MISO, 5 MOSI and 6 CS, with pin 7 INT and pin 8 active-low RST/PD. All logic is 3.3 V; no level shifter is needed. Touch reports pass through the BT817Q, so no separate touch-interface board is required. Confirm ribbon pin numbering and 3.3 V/5 V rails with the meter before attaching the display. Initially use short jumper runs and a conservative SPI clock.

Prototype milestone: initialize BT817Q and Riverdi-specific touch configuration, render text/buttons in portrait, report taps, and control brightness. An ESPHome external component is required unless an existing compatible implementation is selected and validated. UART expansion and differential transceivers are not needed for this display-only stage.

Links: [display](https://riverdi.com/product/eve4-intelligent-display-rvt35hhbfwca0-3-5-inch-projected-capacitive-touch-panel-air-bonding-atouch-frame), [breakout](https://www.mouser.com/en/ProductDetail/Riverdi/BREAK-OUT-BOARD-20?qs=7D1LtPJG0i0nKgSxeAMfVQ%3D%3D), [breakout kit documentation](https://riverdi.com/wp-content/uploads/2016/01/Break_Out_Board_20_Rev.1.1.pdf), [spare ribbon](https://riverdi.com/product/ffc0520150), [ordered 3.3 V regulator](https://www.amazon.com/dp/B0FP2TLXYW). Prices and stock remain subject to checkout confirmation.

## Framed aTouch recommendation

Prefer SM-RVT35HHBFWCA0 for the custom enclosure over the previously listed frameless SM-RVT35HHBNWCA0. The [manufacturer checkout listing](https://riverdi.com/product/eve4-intelligent-display-rvt35hhbfwca0-3-5-inch-projected-capacitive-touch-panel-air-bonding-atouch-frame) is USD 89.34, a USD 2.08 increase. Electrical interface, display/touch controllers and air bonding remain the same; the prototype breakout, ribbon and power parts remain applicable.

The exact Rev.1.4 mechanical drawing, saved as `research/display-fit/riverdi-atouch-frame.pdf` page 6, shows a metal frame with four 3.5 mm mounting holes. Nominal hole spacing is 86 × 54 mm in landscape (54 × 86 mm in portrait). Complete module envelope including ears is 93.50 × 64.70 × 12.78 mm, or 64.70 × 93.50 mm in portrait. Drawing dimensions supersede inconsistent product-summary dimensions.

The active center is 2.27 mm off the frame-envelope center along its short dimension. With the active LCD centered in an 84 × 130 mm face, nominal lateral envelope margins are 11.92/7.38 mm (or swapped with rotation); top/bottom margins are 18.25 mm. The framed version therefore remains within the face outline on paper, including mounting ears. Exact bracket depth/latch/cable clearance remains unverified.

Mount the ears to internal printed bosses with suitable screws/washers, preferably threaded inserts, keeping fasteners behind the sealed front. Mechanical stops or spacers must control seal compression rather than tightening against the glass. Frame provides retention, not waterproofing; a separate perimeter seal is still required. No screw length is selected until the carrier stack-up is designed.
