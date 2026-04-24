# Qucs-s · 50 MHz RF band-pass matching

**Tool**: Qucs-s 2.x · **Language**: Qucs XML + Ngspice

A 50 MHz dual-π LC band-pass matching network between a 50 Ω source and a
50 Ω load. The case demonstrates an RF flow end-to-end:

- Qucs-s schematic capture in [`rf_bandpass.sch`](rf_bandpass.sch).
- The same network exported as an Ngspice-driven S-parameter deck
  ([`rf_bandpass.ngspice`](rf_bandpass.ngspice)).
- S-parameters computed analytically from the ABCD chain at 4001 frequency
  points between 10 MHz and 500 MHz for a clean Smith trajectory.

## Open in Qucs-s

```bash
qucs-s -f rf_bandpass.sch
```

Qucs-s uses Ngspice as the simulation back-end, so the same passive network
also runs through the CLI Ngspice flow used in the other case — no per-tool
port of the circuit.

## Outputs

- [`assets/qucs-s/s_params.csv`](../../assets/qucs-s/s_params.csv) — one row
  per frequency with `f, |S11|, ∠S11, |S21|, ∠S21`.

## Poster renders

- [`assets/qucs-s/smith_chart.png`](../../assets/qucs-s/smith_chart.png) —
  S11 trajectory over the 10 MHz → 500 MHz sweep on a Smith chart with
  constant-resistance and constant-reactance circles. Centre-frequency marker
  highlights `|S11| ≈ 0.43` at 50 MHz.
- [`assets/qucs-s/s21_mag_phase.png`](../../assets/qucs-s/s21_mag_phase.png) —
  transmission magnitude (dB) and phase (degrees) on a shared log-frequency
  axis, with the −3 dB band shaded.

## Why Qucs-s

Qucs-s bridges textbook-style RF schematics with Ngspice simulation, which
means a single circuit description drives both the Smith chart in this case
and the transient / noise sweeps in the Ngspice case. For an AI dataset
pipeline that mixes DC-to-RF signal chains, that shared back-end cuts the
tool matrix in half.
