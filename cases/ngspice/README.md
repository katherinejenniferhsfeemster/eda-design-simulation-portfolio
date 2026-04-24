# Ngspice · AC / transient / Monte-Carlo / noise

**Tool**: Ngspice 41 · **Language**: SPICE

Four SPICE decks that characterise the ECG analog front-end end-to-end:

| Deck                 | Analysis            | What it answers                                                 |
|----------------------|---------------------|-----------------------------------------------------------------|
| `ac_bode.cir`        | `.ac dec 40 0.1 10k`| Does the HPF / LPF corner land where the spec says?             |
| `tran_step.cir`      | `.tran 10us 20ms`   | How fast does the buffer settle to a 1 mV differential step?    |
| `monte_carlo.cir`    | 200-run `.ac` MC    | What is the ±3σ spread of mid-band gain and −3 dB corners?      |
| `noise.cir`          | `.noise`            | What is the input-referred noise density between 1 Hz and 1 kHz?|

## Run

```bash
cd cases/ngspice
bash run_all.sh           # runs all four decks through ngspice -b
```

Each deck pulls its op-amp model from [`models/opamp.lib`](models/opamp.lib),
a generic single-pole op-amp macro-model (GBW, slew-rate, noise density) that
stands in for the INA128 and OPA2348. Swap the `.lib` line to retarget the
decks at vendor SPICE models from TI or Analog Devices.

## Outputs

- [`assets/ngspice/ac_bode.csv`](../../assets/ngspice/ac_bode.csv) — mag/phase.
- [`assets/ngspice/tran_step.csv`](../../assets/ngspice/tran_step.csv) — time-domain.
- [`assets/ngspice/monte_carlo_summary.csv`](../../assets/ngspice/monte_carlo_summary.csv)
  — per-run gain, `f_L`, `f_H`, worst-case bounds.
- [`assets/ngspice/noise_budget.csv`](../../assets/ngspice/noise_budget.csv)
  — integrated noise per stage.

## Poster renders

- [`assets/ngspice/ac_bode.png`](../../assets/ngspice/ac_bode.png) — magnitude +
  phase with corner markers.
- [`assets/ngspice/tran_step.png`](../../assets/ngspice/tran_step.png) — step
  with 0.1 %-settling envelope.
- [`assets/ngspice/monte_carlo.png`](../../assets/ngspice/monte_carlo.png) —
  200 MC runs overlaid on the nominal response with ±1 σ band.
- [`assets/ngspice/noise.png`](../../assets/ngspice/noise.png) — input-referred
  noise density with per-stage contribution bars.

## Why Ngspice

Ngspice is the only fully-scriptable open SPICE simulator with a stable CLI
(`ngspice -b deck.cir`), which is essential for dataset-scale Monte-Carlo
sweeps — the AI program runs hundreds of parameter variants per component
choice, and commercial simulators are too licence-heavy for that workload.
