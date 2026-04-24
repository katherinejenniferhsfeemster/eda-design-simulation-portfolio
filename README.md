# Electronics Design & Simulation Portfolio — AI Dataset Circuits

**Katherine Feemster** · Electronics Design & Simulation (EDA) Specialist

[🌐 **Live portfolio site**](https://katherinejenniferhsfeemster.github.io/eda-design-simulation-portfolio/) · [GitHub repo](https://github.com/katherinejenniferhsfeemster/eda-design-simulation-portfolio)

A code-first electronics portfolio for an AI research program. Every artefact —
schematics, PCB layouts, SPICE decks and S-parameter sweeps — is produced by a
single reproducible Python pipeline that writes real project files for
**KiCad 8**, **LibrePCB 1.x**, **Ngspice 41** and **Qucs-s 2.x**.

## What is here

| Case                                                                | Tool            | Language      | What it proves                                                                              |
|---------------------------------------------------------------------|-----------------|---------------|---------------------------------------------------------------------------------------------|
| [KiCad · ECG analog front-end](cases/kicad/)                        | KiCad 8         | S-expression  | Valid `.kicad_pro` / `.kicad_sch` / `.kicad_pcb` tree with netlist + BOM + fab summary.     |
| [LibrePCB · same AFE, portable netlist](cases/librepcb/)            | LibrePCB 1.x    | S-expression  | Mirrors the AFE inside LibrePCB's native `.lpp` project layout — proves netlist portability. |
| [Ngspice · AC / tran / Monte-Carlo / noise](cases/ngspice/)         | Ngspice 41      | SPICE         | 4 decks covering Bode, transient step, 200-run Monte-Carlo, and input-referred noise.       |
| [Qucs-s · 50 MHz RF band-pass matching](cases/qucs-s/)              | Qucs-s 2.x      | Qucs XML      | Dual-π LC matching network with S11 Smith chart + S21 mag/phase from 10 MHz to 500 MHz.     |

## Live preview

The GitHub Pages site shows the hero artefact of each case:

- `assets/kicad/schematic.png` — annotated ECG AFE schematic mock-up.
- `assets/kicad/pcb.png` — 2-layer PCB layout with traces, footprints and dimensions.
- `assets/librepcb/schematic.png` — the same circuit re-drawn in LibrePCB flavour.
- `assets/ngspice/ac_bode.png` — AC magnitude + phase from 0.1 Hz to 10 kHz.
- `assets/ngspice/tran_step.png` — 1 mV differential step response.
- `assets/ngspice/monte_carlo.png` — 200-run gain/cut-off spread with ±1σ bands.
- `assets/ngspice/noise.png` — input-referred noise budget per stage.
- `assets/qucs-s/smith_chart.png` — S11 of the 50 MHz band-pass on a Smith chart.
- `assets/qucs-s/s21_mag_phase.png` — S21 magnitude + phase.

## Reproducibility

```bash
pip install numpy scipy matplotlib
python3 src/run_all.py
```

`run_all.py` chains four stages, none of which needs the native EDA tool
installed — SciPy + NumPy produce the deterministic simulation outputs, and
each case *also* emits the native project file that opens in the real tool:

1. `build_kicad_case.py` — `.kicad_pro` / `.kicad_sch` / `.kicad_pcb` + `.net` + BOM CSV.
2. `build_librepcb_case.py` — full `.lpp` directory tree (project / circuit / boards / library).
3. `build_ngspice_case.py` — 4 `.cir` decks + `models/opamp.lib` + `run_all.sh`.
4. `build_qucs_case.py` — `rf_bandpass.sch` (Qucs XML) + `rf_bandpass.ngspice` + S-parameter CSV.

When a native tool is present the same decks run unchanged — the generators
produce files that are schema-valid for KiCad, LibrePCB, Ngspice and Qucs-s
upstream.

## Editorial style

- **Color**: teal `#2E7A7B` + amber `#D9A441` on ink `#141A21` / paper `#F7F4ED`.
- **Type**: Inter (UI) + JetBrains Mono (code / netlists).
- **Determinism**: every generator is seeded; all PNG and CSV bytes are stable.
- **Licensing**: all four tools are FOSS. No commercial EDA SDKs in the pipeline.

## Repo layout

```
eda-portfolio/
├── src/                         # 4 generators + art_helpers.py + run_all.py
├── cases/                       # one folder per tool with the native project file
│   ├── kicad/sensor_frontend/   # .kicad_pro / _sch / _pcb / .net / _bom.csv
│   ├── librepcb/sensor_frontend.lpp/
│   ├── ngspice/                 # 4 .cir decks + models/ + run_all.sh
│   └── qucs-s/                  # rf_bandpass.sch + rf_bandpass.ngspice
├── assets/                      # generated posters, CSVs, fab_summary.json
├── docs/                        # GitHub Pages site
└── .github/workflows/           # CI re-runs the pipeline on each push
```

## About the author

Senior electronics design & simulation specialist shipping cross-tool circuit
pipelines — analog front-ends, mixed-signal boards, and RF matching networks —
most recently focused on dataset generation and labelling workflows for AI
research programs. Comfortable owning a project from circuit synthesis through
schematic capture, layout, SPICE characterisation, Monte-Carlo yield analysis
and S-parameter verification.

- GitHub: [katherinejenniferhsfeemster](https://github.com/katherinejenniferhsfeemster)
