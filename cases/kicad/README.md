# KiCad · ECG analog front-end

**Tool**: KiCad 8 · **Language**: KiCad S-expression

A clinical-grade differential ECG analog front-end designed for a biosignal
dataset pipeline:

- **INA128** instrumentation amplifier with gain set by a single `Rg` resistor.
- 1.6 Hz high-pass on each input (DC-block for electrode offset).
- 1.06 kHz low-pass anti-alias filter ahead of the ADC buffer.
- **OPA2348** rail-to-rail op-amp as unity-gain output buffer.
- ESD clamps and protection resistors on every patient-connected node.

## Open in KiCad

```bash
kicad sensor_frontend/sensor_frontend.kicad_pro
```

The project tree under [`sensor_frontend/`](sensor_frontend/) contains:

| File                              | Purpose                                               |
|-----------------------------------|-------------------------------------------------------|
| `sensor_frontend.kicad_pro`       | Project file with ERC / DRC rule sets.                |
| `sensor_frontend.kicad_sch`       | Hierarchical schematic with power nets and ref-des.   |
| `sensor_frontend.kicad_pcb`       | 2-layer PCB, 50 mm × 32 mm, ground-pour both layers.  |
| `sensor_frontend.net`             | KiCad flat netlist (round-trip with external SPICE).  |
| `sensor_frontend_bom.csv`         | BOM with manufacturer part numbers and reference-des. |

## Fab summary

The generator also writes [`assets/kicad/fab_summary.json`](../../assets/kicad/fab_summary.json)
with layer stack-up, controlled-impedance traces, via counts and drill
statistics — the sort of hand-off data a fab house (JLCPCB, PCBWay, OSHPark)
needs alongside the Gerbers.

## Poster renders

- [`assets/kicad/schematic.png`](../../assets/kicad/schematic.png) — annotated
  schematic mock-up with InAmp, HPF, LPF and buffer stages labelled.
- [`assets/kicad/pcb.png`](../../assets/kicad/pcb.png) — 2-layer PCB layout
  with traces, footprints, vias, mechanical dimensions and net labels.

## Why KiCad

KiCad's `.kicad_*` S-expression format is text and version-controllable, which
makes it the natural home for programmatically-generated schematics — exactly
what an AI-assisted circuit pipeline needs.
