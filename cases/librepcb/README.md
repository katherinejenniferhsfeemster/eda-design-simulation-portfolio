# LibrePCB · Same AFE, portable netlist

**Tool**: LibrePCB 1.x · **Language**: LibrePCB S-expression

The same ECG analog front-end from the KiCad case, re-emitted in LibrePCB's
native `.lpp` project tree. The point of this case is **netlist portability**
— prove the generator can target two independent FOSS EDA flows from the same
circuit description, which matters when the AI pipeline needs to fan out to
multiple downstream tools.

## Open in LibrePCB

```bash
librepcb sensor_frontend.lpp/
```

The project folder [`sensor_frontend.lpp/`](sensor_frontend.lpp/) follows
LibrePCB's mandated layout:

| Path                        | Content                                                   |
|-----------------------------|-----------------------------------------------------------|
| `project/project.lp`        | Top-level project metadata + board/schematic references.  |
| `circuit/circuit.lp`        | Net-list-level circuit with component instances + nets.   |
| `boards/default/board.lp`   | Board layout with footprints, copper, silkscreen.         |
| `library/` (sym / cmp / dev / pkg) | Flattened LibrePCB library with every symbol, component, device and package used by this project. |

## Poster renders

- [`assets/librepcb/schematic.png`](../../assets/librepcb/schematic.png) —
  LibrePCB-flavour schematic of the same AFE.
- [`assets/librepcb/pcb.png`](../../assets/librepcb/pcb.png) — LibrePCB-flavour
  PCB layout with the same 50 mm × 32 mm outline.

## Why LibrePCB

LibrePCB's built-in library manager and strict s-expression schema make it a
stricter target than KiCad — if a generator round-trips through LibrePCB it
will almost certainly round-trip through anything else. It is also the default
EDA choice on Wayland-only Linux distributions, which matters for containerised
CI rendering.
