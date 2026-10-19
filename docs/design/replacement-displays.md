# Replacement display research

Alternative hardware research; separate from the original Kohler wire protocols.

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
