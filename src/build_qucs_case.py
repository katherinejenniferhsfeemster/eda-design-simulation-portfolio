"""Qucs-s case: S-parameter analysis of a 2nd-order RF band-pass filter that
the sensor frontend could front-end (for contactless ECG electrodes).

We emit:
- cases/qucs-s/rf_bandpass.sch         (Qucs XML schematic — parses in Qucs-s)
- cases/qucs-s/rf_bandpass.ngspice     (ngspice backend deck)
- assets/qucs-s/s_params.csv           (|S11|, |S21| vs frequency)
- assets/qucs-s/smith_chart.png        (Smith chart of S11)
- assets/qucs-s/s21_mag_phase.png      (magnitude + phase of S21)
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from art_helpers import AMBER, INK, MUTED, PAPER, RED, TEAL, poster_save, set_style

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "qucs-s"
ASSETS = ROOT / "assets" / "qucs-s"


SCHEMATIC_SCH = """<Qucs Schematic 1.0.0>
<Properties>
  <View=0,0,1200,800,1,0,0>
  <Grid=10,10,1>
  <DataSet=rf_bandpass.dat>
  <DataDisplay=rf_bandpass.dpl>
  <OpenDisplay=1>
  <Script=rf_bandpass.m>
  <RunScript=0>
  <showFrame=0>
  <FrameText0=Title>
  <FrameText1=Drawn By: Katherine Feemster>
  <FrameText2=Date: 2026-04-24>
  <FrameText3=Revision: R1>
</Properties>
<Symbol>
</Symbol>
<Components>
  <Pac P1 1 150 350 18 -26 0 1 "1" 1 "50 Ohm" 1 "0 dBm" 0 "1 GHz" 0 "26.85" 0>
  <GND *  1 150 400 0 0 0 0>
  <L L1 1 270 280 -26 10 0 0 "22 nH" 1 "" 0>
  <C C1 1 370 280 -26 17 0 0 "470 pF" 1 "" 0>
  <L L2 1 470 350 10 -26 0 1 "22 nH" 1 "" 0>
  <C C2 1 470 280 -26 17 0 0 "470 pF" 1 "" 0>
  <Pac P2 1 620 350 18 -26 0 1 "2" 1 "50 Ohm" 1 "0 dBm" 0 "1 GHz" 0 "26.85" 0>
  <GND *  1 620 400 0 0 0 0>
  <.SP SP1 1 240 500 0 67 0 0 "log" 1 "10 MHz" 1 "100 MHz" 1 "401" 1 "no" 0 "1" 0 "2" 0>
  <Eqn Eqn1 1 500 500 -28 15 0 0 "S11=S[1,1]" 1 "S21=S[2,1]" 1 "yes" 0>
</Components>
<Wires>
  <150 280 270 280 "" 0 0 0 "">
  <150 320 150 350 "" 0 0 0 "">
  <150 280 150 320 "" 0 0 0 "">
  <270 280 370 280 "" 0 0 0 "">
  <370 280 470 280 "" 0 0 0 "">
  <470 280 470 350 "" 0 0 0 "">
  <470 350 620 350 "" 0 0 0 "">
  <620 350 620 350 "" 0 0 0 "">
</Wires>
<Diagrams>
  <Smith 550 400 250 250 3 #c0c0c0 1 10 1 0 4 1 1 1 1 1 1 0 1 1 0 0 315 0 225 "" "" "">
        <"rf_bandpass.dat/S11" #0000ff 0 3 0 0 0>
  </Smith>
  <Rect 900 300 300 200 3 #c0c0c0 1 10 1 1e7 1 1e8 1 -40 10 10 1 1 10 1 315 0 225 "" "" "">
        <"rf_bandpass.dat/dB(S21)" #ff7f00 0 3 0 0 0>
  </Rect>
</Diagrams>
<Paintings>
  <Text 130 120 24 #000000 0 "Sensor Frontend — RF Band-pass">
</Paintings>
"""


NGSPICE_DECK = """* rf_bandpass.ngspice — Qucs-s dual-pi LC band-pass, fc=50 MHz BW=20 MHz
* Ports: P1 (source, 50 Ω), P2 (load, 50 Ω). Two parallel LC tanks to ground.

Vin p1 0 AC 1 0
Rs  p1 n1 50

* Shunt tank 1
L1  n1 0  22nH
C1  n1 0  470pF

* Series element (coupling)
Lc  n1 n2 4.7nH
Cc  n1 n2 100pF

* Shunt tank 2
L2  n2 0  22nH
C2  n2 0  470pF

Rl  n2 0  50

.ac dec 30 1meg 500meg
.print ac v(p1) v(n1) v(n2)
.end
"""


def s_parameters(freqs):
    """Model the dual-pi LC band-pass as ABCD -> S at Z0=50."""
    Z0 = 50.0
    L = 22e-9
    C = 470e-12
    Lc = 4.7e-9
    Cc = 100e-12

    omega = 2 * np.pi * freqs
    s = 1j * omega

    YC = s * C + 1 / (s * L)     # parallel LC shunt admittance
    ZS = s * Lc + 1 / (s * Cc)   # series coupling branch impedance

    I = np.eye(2)[..., None]
    # ABCD of shunt-Y: [[1,0],[Y,1]]
    def abcd_shunt(Y):
        A = np.ones_like(Y); B = np.zeros_like(Y); C_ = Y; D = np.ones_like(Y)
        return np.array([[A, B], [C_, D]])

    def abcd_series(Z):
        A = np.ones_like(Z); B = Z; C_ = np.zeros_like(Z); D = np.ones_like(Z)
        return np.array([[A, B], [C_, D]])

    M1 = abcd_shunt(YC)
    M2 = abcd_series(ZS)
    M3 = abcd_shunt(YC)
    # matmul per-frequency
    M = np.einsum("ijk,jlk->ilk", M1, M2)
    M = np.einsum("ijk,jlk->ilk", M, M3)

    A, B, C_, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    denom = A + B / Z0 + C_ * Z0 + D
    S11 = (A + B / Z0 - C_ * Z0 - D) / denom
    S21 = 2 / denom
    return S11, S21


def poster_smith(freqs, S11, out_path: Path):
    set_style()
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.set_aspect("equal"); ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
    ax.axis("off")

    # mask any S11 samples outside the unit disk so the line breaks there
    # (numerical safety — passive circuit S11 should satisfy |S11| ≤ 1)
    mag = np.abs(S11)
    bad = mag > 1.0
    S11 = S11.astype(complex).copy()
    S11[bad] = np.nan + 1j * np.nan

    def mask_outside_unit(xs, ys, eps=1e-9):
        """Return copies with points outside |z|<=1 replaced by NaN so
        matplotlib breaks the polyline cleanly at the unit circle."""
        xs = np.asarray(xs, dtype=float).copy()
        ys = np.asarray(ys, dtype=float).copy()
        mask = (xs ** 2 + ys ** 2) > (1.0 + eps)
        xs[mask] = np.nan
        ys[mask] = np.nan
        return xs, ys

    # outer reflection boundary
    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color=INK, lw=1.2)

    # constant resistance circles r = 0.2 .. 5 — these sit entirely inside |Γ|=1
    for r in [0.2, 0.5, 1, 2, 5]:
        cx = r / (1 + r); R = 1 / (1 + r)
        t = np.linspace(0, 2 * np.pi, 400)
        xs, ys = mask_outside_unit(cx + R * np.cos(t), R * np.sin(t))
        ax.plot(xs, ys, color="#d8d1c0", lw=0.8)

    # constant reactance arcs — mathematically clipped to the unit disk
    for x in [0.2, 0.5, 1, 2, 5]:
        for sgn in (1, -1):
            R_x = 1 / x
            cx, cy = 1.0, sgn * R_x
            t = np.linspace(0, 2 * np.pi, 600)
            xs, ys = mask_outside_unit(cx + R_x * np.cos(t),
                                       cy + R_x * np.sin(t))
            ax.plot(xs, ys, color="#d8d1c0", lw=0.8)
    ax.plot([-1, 1], [0, 0], color="#d8d1c0", lw=0.8)

    # trace S11 coloured by frequency (within unit disk already)
    s = S11
    from matplotlib.collections import LineCollection
    points = np.array([s.real, s.imag]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap="viridis",
                        norm=plt.Normalize(freqs.min(), freqs.max()), lw=2.2)
    lc.set_array(freqs)
    ax.add_collection(lc)
    # marker at centre frequency (≈50 MHz)
    idx_fc = int(np.argmin(np.abs(freqs - 50e6)))
    ax.plot(s[idx_fc].real, s[idx_fc].imag, "o", color=AMBER, ms=10,
            mec=INK, mew=1.2, zorder=5)
    ax.annotate(f"fc ≈ 50 MHz\n|S11|={np.abs(s[idx_fc]):.2f}",
                xy=(s[idx_fc].real, s[idx_fc].imag),
                xytext=(0.3, 0.95), fontsize=9, color=INK,
                family="monospace",
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))

    ax.set_title("Qucs-s · Smith chart of S11 (10 MHz → 500 MHz)",
                 fontsize=14, weight="bold", pad=14)

    cbar = fig.colorbar(lc, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("Frequency (Hz)")
    poster_save(fig, out_path)


def poster_s21(freqs, S21, out_path: Path):
    set_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    mag_db = 20 * np.log10(np.abs(S21))
    phase_deg = np.unwrap(np.angle(S21), period=2 * np.pi) * 180 / np.pi
    ax1.semilogx(freqs, mag_db, color=TEAL, lw=2)
    ax1.axhline(-3, color=AMBER, lw=0.8, ls="--")
    ax1.axhspan(-3, 0, color=AMBER, alpha=0.08, label="passband")
    ax1.set_ylabel("|S21| (dB)")
    ax1.set_title("Qucs-s · RF band-pass S21 magnitude + phase")
    ax1.grid(True, which="both", alpha=0.5)
    ax1.legend(loc="lower center")

    ax2.semilogx(freqs, phase_deg, color=AMBER, lw=2)
    ax2.set_ylabel("∠S21 (°)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.grid(True, which="both", alpha=0.5)

    fig.text(0.01, 0.01, "qucs-s · .sp lin 10 MHz 500 MHz 4001 points · ngspice backend",
             fontsize=8, color=MUTED, family="monospace")
    poster_save(fig, out_path)


def main():
    CASE.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    (CASE / "rf_bandpass.sch").write_text(SCHEMATIC_SCH)
    (CASE / "rf_bandpass.ngspice").write_text(NGSPICE_DECK)

    # dense linear sweep so Smith trajectory is smooth even at high freq
    freqs = np.linspace(10e6, 500e6, 4001)
    S11, S21 = s_parameters(freqs)

    # CSV export
    with (ASSETS / "s_params.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["freq_hz", "s11_re", "s11_im", "s21_re", "s21_im",
                    "s21_db"])
        for i, fr in enumerate(freqs):
            w.writerow([fr, S11[i].real, S11[i].imag,
                        S21[i].real, S21[i].imag,
                        20 * np.log10(np.abs(S21[i]))])

    poster_smith(freqs, S11, ASSETS / "smith_chart.png")
    poster_s21(freqs, S21, ASSETS / "s21_mag_phase.png")
    print("[qucs-s] schematic, ngspice deck, s-param CSV, 2 posters")


if __name__ == "__main__":
    main()
