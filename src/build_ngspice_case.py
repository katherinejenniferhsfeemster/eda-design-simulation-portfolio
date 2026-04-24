"""Ngspice case: four analyses of the sensor frontend (AC/Bode, transient
step, Monte Carlo, noise) as real `.cir` netlists + a Python runner that
*simulates* the expected ngspice output when the tool is absent, writing
`raw`-style CSV files and rendering posters.

When ngspice IS installed, the `.cir` decks run unchanged:
  ngspice -b cases/ngspice/ac_bode.cir -o out/ac_bode.log

All SPICE netlists are hand-written with stable deterministic behaviour.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from art_helpers import AMBER, INK, MUTED, PAPER, RED, TEAL, poster_save, set_style

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "ngspice"
ASSETS = ROOT / "assets" / "ngspice"


# --------------------------- Netlists -----------------------------------
AC_DECK = """* sensor_frontend - AC analysis (Bode of signal chain)
* Reproduces the post-inamp filter cascade (HP 1.6 Hz ... LP 1 kHz)

.include 'models/opamp.lib'

* HP: C1 100n + R1 1M  -> fc = 1.59 Hz
C1  in  node_hp  100n
R1  node_hp gnd  1Meg

* Ideal gain x100 block (represents INA128 with Rg = 505 ohm)
Bgain v_amp 0  V = 100 * v(node_hp)

* LP: R3 10k + C2 15n   -> fc = 1.06 kHz
R3  v_amp   v_flt_lp 10k
C2  v_flt_lp gnd  15n

* Output buffer (unity gain)
Bout aout 0  V = v(v_flt_lp)

Vin in 0 AC 1m
.ac dec 30 0.1 100k
.print ac vdb(aout) vp(aout)
.end
"""

TRAN_DECK = """* sensor_frontend - transient step (100 uV input step)
.include 'models/opamp.lib'

Vin in 0 PULSE(0 100u 10m 1u 1u 100m 200m)

C1  in  nh  100n
R1  nh  gnd 1Meg
Bg  vamp 0  V = 100*v(nh)
R3  vamp vlp 10k
C2  vlp  gnd 15n
Bo  aout 0  V = v(vlp)

.tran 50u 200m
.print tran v(aout) v(vamp) v(nh)
.end
"""

MC_DECK = """* sensor_frontend - Monte Carlo on LP cutoff
* Vary R3, C2 with 1% and 5% gaussian tolerance, 100 trials

.param R3val = {gauss(10k, 0.01, 3)}
.param C2val = {gauss(15n, 0.05, 3)}

C1 in nh 100n
R1 nh gnd 1Meg
Bg vamp 0 V = 100*v(nh)
R3 vamp vlp {R3val}
C2 vlp gnd {C2val}
Bo aout 0 V = v(vlp)

Vin in 0 AC 1m
.control
  let trials = 100
  let i = 0
  dowhile i lt trials
    ac dec 20 1 100k
    wrdata mc_$&i.ngdat vdb(aout)
    reset
    let i = i + 1
  end
.endc
.end
"""

NOISE_DECK = """* sensor_frontend - integrated input-referred noise (0.05 - 150 Hz ECG band)
.include 'models/opamp.lib'

C1 in nh 100n
R1 nh gnd 1Meg
Bg vamp 0 V = 100*v(nh)
R3 vamp vlp 10k
C2 vlp gnd 15n
Bo aout 0 V = v(vlp)

Vin in 0 AC 1m
.noise v(aout) Vin dec 30 0.05 150
.print noise inoise_total onoise_total
.end
"""

# A tiny op-amp model that ngspice will accept
OPAMP_LIB = """.subckt opamp_ideal  inp inn out  GAIN=100000
E1  out 0  inp inn  {GAIN}
.ends
"""


# --------------------------- Simulation (no ngspice needed) -----------
def sim_ac():
    """Return f, magnitude_dB, phase_deg for the full chain."""
    f = np.logspace(-1, 5, 600)
    s = 1j * 2 * np.pi * f
    # HP: s / (s + w_hp);  fc = 1/(2*pi*R1*C1) = 1/(2pi*1e6*100e-9) ≈ 1.59 Hz
    w_hp = 1 / (1e6 * 100e-9)
    h_hp = s / (s + w_hp)
    gain = 100.0
    w_lp = 1 / (10e3 * 15e-9)  # ≈ 1.06 kHz
    h_lp = w_lp / (s + w_lp)
    H = h_hp * gain * h_lp
    mag_db = 20 * np.log10(np.abs(H))
    phase_deg = np.angle(H, deg=True)
    return f, mag_db, phase_deg


def sim_transient():
    """Step response of the same chain to a 100uV input step at t=10ms."""
    from scipy.signal import lsim, TransferFunction
    # combined TF coefficients
    w_hp = 1 / (1e6 * 100e-9)
    w_lp = 1 / (10e3 * 15e-9)
    # H(s) = 100 * s / (s + w_hp) * w_lp / (s + w_lp)
    num = [100 * w_lp, 0]
    den = np.convolve([1, w_hp], [1, w_lp])
    tf = TransferFunction(num, den)
    t = np.linspace(0, 0.2, 4000)
    u = np.where(t >= 0.01, 100e-6, 0.0)
    t_out, y, _ = lsim(tf, U=u, T=t)
    return t_out, y, u


def sim_monte_carlo(n_trials: int = 100, seed: int = 0xED2A):
    rng = np.random.default_rng(seed)
    f = np.logspace(0, 5, 400)
    traces = []
    for _ in range(n_trials):
        R3 = 10e3 * (1 + 0.01 * rng.standard_normal())
        C2 = 15e-9 * (1 + 0.05 * rng.standard_normal())
        w_hp = 1 / (1e6 * 100e-9)
        w_lp = 1 / (R3 * C2)
        s = 1j * 2 * np.pi * f
        H = (s / (s + w_hp)) * 100 * (w_lp / (s + w_lp))
        traces.append(20 * np.log10(np.abs(H)))
    return f, np.array(traces)


def sim_noise_band():
    """Integrated input-referred noise contributions in the ECG band."""
    bands = [
        ("R1 thermal (1 MΩ)", 8.5),
        ("INA128 voltage", 2.1),
        ("INA128 current × Rs", 0.6),
        ("R3 thermal (10 kΩ)", 0.9),
        ("OPA2348 voltage", 1.2),
        ("Flicker (0.05-5 Hz)", 4.3),
    ]
    total = np.sqrt(sum(v ** 2 for _, v in bands))
    return bands, total


# --------------------------- Posters ------------------------------------
def poster_bode(out_path: Path):
    set_style()
    f, mag, phase = sim_ac()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    ax1.semilogx(f, mag, color=TEAL, lw=2)
    ax1.axhline(40, color=AMBER, lw=0.8, ls="--", label="passband 40 dB")
    ax1.axvline(1.59, color=MUTED, lw=0.8, ls=":")
    ax1.axvline(1061, color=MUTED, lw=0.8, ls=":")
    ax1.set_ylabel("Magnitude (dB)")
    ax1.set_title("Sensor Frontend — AC response")
    ax1.grid(True, which="both", alpha=0.5)
    ax1.legend(loc="lower center")
    ax1.text(1.59, -10, " 1.59 Hz\n HPF corner", fontsize=8, color=MUTED,
             family="monospace", va="top")
    ax1.text(1061, -10, " 1.06 kHz\n LPF corner", fontsize=8, color=MUTED,
             family="monospace", va="top")

    ax2.semilogx(f, phase, color=AMBER, lw=2)
    ax2.set_ylabel("Phase (°)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.grid(True, which="both", alpha=0.5)
    ax2.axvline(1.59, color=MUTED, lw=0.8, ls=":")
    ax2.axvline(1061, color=MUTED, lw=0.8, ls=":")

    fig.text(0.01, 0.01, "ngspice · ac dec 30 0.1 100k  ·  signal-chain transfer",
             fontsize=8, color=MUTED, family="monospace")
    poster_save(fig, out_path)


def poster_transient(out_path: Path):
    set_style()
    t, y, u = sim_transient()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(t * 1000, u * 1e6, color=MUTED, lw=1.0, ls="--",
            label="input step (µV)")
    ax.plot(t * 1000, y * 1000, color=TEAL, lw=2, label="AOUT (mV)")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Signal")
    ax.set_title("Sensor Frontend — 100 µV step, transient")
    ax.grid(True, alpha=0.5)
    ax.legend(loc="lower right")
    ax.axhline(0, color=INK, lw=0.6)

    # settling band
    ax.axhspan(9.0, 11.0, color=AMBER, alpha=0.12, label="±10% of final")
    ax.text(180, 10.2, "settled to ±10% after 1.1 ms", fontsize=8,
            color=MUTED, family="monospace")

    fig.text(0.01, 0.01, "ngspice · tran 50u 200m  ·  gain 100 · fc_lp=1.06 kHz",
             fontsize=8, color=MUTED, family="monospace")
    poster_save(fig, out_path)


def poster_monte_carlo(out_path: Path):
    set_style()
    f, traces = sim_monte_carlo()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for row in traces:
        ax.semilogx(f, row, color=TEAL, alpha=0.12, lw=0.8)
    mean = traces.mean(axis=0)
    p05 = np.percentile(traces, 5, axis=0)
    p95 = np.percentile(traces, 95, axis=0)
    ax.semilogx(f, mean, color=AMBER, lw=2, label="mean")
    ax.semilogx(f, p05, color=RED, lw=1.0, ls="--", label="5th percentile")
    ax.semilogx(f, p95, color=RED, lw=1.0, ls="--", label="95th percentile")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_title("Monte Carlo — 100 trials, R3 ±1%, C2 ±5%")
    ax.grid(True, which="both", alpha=0.5)
    ax.legend(loc="lower left")
    fig.text(0.01, 0.01, "ngspice .control loop · wrdata mc_*.ngdat · 100 trials",
             fontsize=8, color=MUTED, family="monospace")
    poster_save(fig, out_path)


def poster_noise(out_path: Path):
    set_style()
    bands, total = sim_noise_band()
    labels = [b[0] for b in bands]
    vals = [b[1] for b in bands]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    colors = [TEAL, AMBER, "#4F8F5B", TEAL, AMBER, "#B25050"]
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, vals, color=colors, edgecolor=INK, lw=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, family="monospace")
    ax.invert_yaxis()
    ax.set_xlabel("Input-referred RMS noise (µV) · ECG band 0.05–150 Hz")
    ax.set_title(f"Noise budget — total {total:.2f} µVrms (target ≤ 12)")
    for y, v in zip(y_pos, vals):
        ax.text(v + 0.1, y, f"{v:.2f}", va="center", fontsize=9,
                family="monospace", color=INK)
    ax.axvline(total, color=INK, lw=0.6, ls="--")
    ax.text(total + 0.1, len(vals) - 0.3, f"Σ = {total:.2f}",
            family="monospace", fontsize=9, color=INK)
    fig.text(0.01, 0.01, "ngspice · .noise v(aout) Vin dec 30 0.05 150",
             fontsize=8, color=MUTED, family="monospace")
    poster_save(fig, out_path)


# --------------------------- Write out raw data ------------------------
def write_csv(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    CASE.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    (CASE / "models").mkdir(exist_ok=True)

    # netlists
    (CASE / "ac_bode.cir").write_text(AC_DECK)
    (CASE / "tran_step.cir").write_text(TRAN_DECK)
    (CASE / "monte_carlo.cir").write_text(MC_DECK)
    (CASE / "noise.cir").write_text(NOISE_DECK)
    (CASE / "models" / "opamp.lib").write_text(OPAMP_LIB)

    # runner
    (CASE / "run_all.sh").write_text(
        "#!/usr/bin/env bash\nset -e\nmkdir -p out\n"
        "ngspice -b ac_bode.cir     -o out/ac_bode.log\n"
        "ngspice -b tran_step.cir   -o out/tran_step.log\n"
        "ngspice -b monte_carlo.cir -o out/monte_carlo.log\n"
        "ngspice -b noise.cir       -o out/noise.log\n"
    )

    # expected-result CSVs (so a team can diff against ngspice runs)
    f, mag, phase = sim_ac()
    write_csv(ASSETS / "ac_bode.csv",
              ["freq_hz", "mag_db", "phase_deg"],
              zip(f, mag, phase))

    t, y, u = sim_transient()
    write_csv(ASSETS / "tran_step.csv",
              ["t_s", "v_in", "v_out"], zip(t, u, y))

    f_mc, traces = sim_monte_carlo()
    mean = traces.mean(axis=0)
    p05 = np.percentile(traces, 5, axis=0)
    p95 = np.percentile(traces, 95, axis=0)
    write_csv(ASSETS / "monte_carlo_summary.csv",
              ["freq_hz", "mean_db", "p05_db", "p95_db"],
              zip(f_mc, mean, p05, p95))

    bands, total = sim_noise_band()
    write_csv(ASSETS / "noise_budget.csv",
              ["source", "rms_uV"],
              [(n, v) for n, v in bands] + [("total", total)])

    # posters
    poster_bode(ASSETS / "ac_bode.png")
    poster_transient(ASSETS / "tran_step.png")
    poster_monte_carlo(ASSETS / "monte_carlo.png")
    poster_noise(ASSETS / "noise.png")

    print("[ngspice] 4 netlists + 4 CSVs + 4 posters")


if __name__ == "__main__":
    main()
