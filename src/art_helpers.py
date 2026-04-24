"""Shared helpers for the EDA portfolio generators.

- Editorial palette (teal / amber / ink / paper)
- matplotlib rcParams preset
- Poster frame writer
- Small schematic / PCB mock renderers
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

TEAL = "#2E7A7B"
AMBER = "#D9A441"
INK = "#141A21"
PAPER = "#F7F4ED"
MUTED = "#5C6672"
GREEN = "#4F8F5B"
RED = "#B25050"


def set_style():
    plt.rcParams.update({
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "font.family": "DejaVu Sans",
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": "#d6cfbf",
        "grid.alpha": 0.7,
        "legend.frameon": False,
    })


def poster_save(fig, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---- simple schematic mock (used as KiCad / LibrePCB preview image) ---------
def draw_schematic_mock(title: str, out_path: Path, flavour: str = "kicad"):
    set_style()
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    # title bar
    ax.add_patch(Rectangle((0, 6.1), 14, 0.8, facecolor=TEAL, edgecolor="none"))
    ax.text(0.3, 6.5, title, fontsize=16, color=PAPER, weight="bold", va="center")
    flavour_label = {"kicad": "KiCad 8 · .kicad_sch",
                     "librepcb": "LibrePCB 1.0 · .lp"}[flavour]
    ax.text(13.7, 6.5, flavour_label, fontsize=10, color=PAPER,
            family="monospace", va="center", ha="right")

    # grid
    for x in np.arange(0.5, 14, 0.5):
        ax.plot([x, x], [0.2, 5.9], color="#d8d1c0", lw=0.4, zorder=0)
    for y in np.arange(0.2, 6, 0.5):
        ax.plot([0, 14], [y, y], color="#d8d1c0", lw=0.4, zorder=0)

    # symbols: instrumentation amp (centre), RC filter in, RC filter out, output buffer
    def ic(cx, cy, w, h, pins_l, pins_r, label, sub=""):
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PAPER, edgecolor=INK, lw=1.5))
        ax.text(cx, cy + 0.05, label, fontsize=11, ha="center", weight="bold")
        if sub:
            ax.text(cx, cy - 0.22, sub, fontsize=8, ha="center",
                    family="monospace", color=MUTED)
        for i, p in enumerate(pins_l):
            py = cy + h / 2 - (i + 1) * h / (len(pins_l) + 1)
            ax.plot([cx - w / 2 - 0.3, cx - w / 2], [py, py], color=INK, lw=1.2)
            ax.text(cx - w / 2 - 0.35, py, p, fontsize=7, ha="right", va="center",
                    family="monospace")
        for i, p in enumerate(pins_r):
            py = cy + h / 2 - (i + 1) * h / (len(pins_r) + 1)
            ax.plot([cx + w / 2, cx + w / 2 + 0.3], [py, py], color=INK, lw=1.2)
            ax.text(cx + w / 2 + 0.35, py, p, fontsize=7, ha="left", va="center",
                    family="monospace")

    # RC filter (input high-pass)
    # cap C1
    ax.plot([1.0, 1.0, 1.0], [3.5, 3.3, 3.2], color=INK, lw=1.4)
    ax.plot([0.7, 1.3], [3.2, 3.2], color=INK, lw=1.5)
    ax.plot([0.7, 1.3], [3.1, 3.1], color=INK, lw=1.5)
    ax.plot([1.0, 1.0], [3.1, 2.8], color=INK, lw=1.4)
    ax.text(1.4, 3.0, "C1 100n", fontsize=8, family="monospace")
    # resistor R1
    ax.plot([1.0, 2.0], [2.8, 2.8], color=INK, lw=1.2)
    ax.add_patch(Rectangle((2.0, 2.68), 0.8, 0.24, facecolor=PAPER,
                           edgecolor=INK, lw=1.2))
    ax.text(2.4, 2.52, "R1 1M", fontsize=8, family="monospace", ha="center")
    ax.plot([2.8, 3.5], [2.8, 2.8], color=INK, lw=1.2)
    ax.plot([3.5, 3.5], [2.8, 4.0], color=INK, lw=1.2)

    # IN label
    ax.text(0.4, 3.6, "IN", fontsize=10, weight="bold", color=AMBER)
    ax.plot([0.4, 1.0], [3.6, 3.6], color=INK, lw=1.2)

    # InAmp U1
    ic(5.0, 4.0, 2.2, 1.6, ["IN+", "IN-", "RG"], ["OUT", "REF"],
       "U1", "INA128 / AD620")
    ax.plot([3.5, 3.9], [4.0, 4.0], color=INK, lw=1.2)  # wire into IN+

    # IN-: tied to virtual ground mid-rail via R2
    ax.plot([3.9, 3.5, 3.5, 3.0], [3.7, 3.7, 1.5, 1.5], color=INK, lw=1.2)
    ax.add_patch(Rectangle((2.0, 1.38), 0.8, 0.24, facecolor=PAPER,
                           edgecolor=INK, lw=1.2))
    ax.text(2.4, 1.22, "R2 1M", fontsize=8, family="monospace", ha="center")
    ax.plot([2.0, 1.0, 1.0], [1.5, 1.5, 0.6], color=INK, lw=1.2)
    # GND
    for i, off in enumerate((-0.25, -0.15, -0.05)):
        ax.plot([1.0 + off, 1.0 - off], [0.55 - i * 0.08, 0.55 - i * 0.08],
                color=INK, lw=1.2 - i * 0.3)
    ax.text(1.0, 0.2, "GND", fontsize=7, ha="center", family="monospace")

    # Low-pass after InAmp
    ax.plot([6.1, 7.2], [4.2, 4.2], color=INK, lw=1.2)
    ax.add_patch(Rectangle((7.2, 4.08), 0.8, 0.24, facecolor=PAPER,
                           edgecolor=INK, lw=1.2))
    ax.text(7.6, 3.92, "R3 10k", fontsize=8, family="monospace", ha="center")
    ax.plot([8.0, 9.0], [4.2, 4.2], color=INK, lw=1.2)
    # C2 to ground
    ax.plot([8.5, 8.5], [4.2, 3.6], color=INK, lw=1.2)
    ax.plot([8.2, 8.8], [3.6, 3.6], color=INK, lw=1.5)
    ax.plot([8.2, 8.8], [3.5, 3.5], color=INK, lw=1.5)
    ax.plot([8.5, 8.5], [3.5, 3.0], color=INK, lw=1.2)
    ax.text(8.95, 3.55, "C2 15n", fontsize=8, family="monospace")

    # Output buffer U2
    ic(10.2, 4.2, 1.6, 1.2, ["+", "−"], ["OUT"], "U2", "OPA2348")
    ax.plot([9.0, 9.4], [4.2, 4.2], color=INK, lw=1.2)
    ax.plot([9.0, 9.4], [3.9, 3.9], color=INK, lw=1.2)  # feedback
    ax.plot([9.4, 9.0, 9.0, 11.0, 11.0, 11.0], [3.9, 3.9, 3.4, 3.4, 3.4, 4.2],
            color=INK, lw=1.2)
    ax.plot([11.0, 12.5], [4.2, 4.2], color=INK, lw=1.2)
    ax.text(12.6, 4.2, "AOUT", fontsize=10, weight="bold", color=AMBER, va="center")

    # Power rails
    ax.plot([0.4, 13.6], [5.4, 5.4], color=AMBER, lw=1.2)
    ax.text(0.4, 5.55, "+3V3", fontsize=9, color=AMBER, weight="bold")
    ax.plot([5.0, 5.0], [5.4, 4.8], color=AMBER, lw=1.0)
    ax.plot([10.2, 10.2], [5.4, 4.8], color=AMBER, lw=1.0)
    ax.plot([0.4, 13.6], [0.6, 0.6], color=TEAL, lw=1.2)
    ax.text(13.5, 0.75, "GND", fontsize=9, color=TEAL, weight="bold", ha="right")

    # footer
    ax.text(0.3, -0.1, "sheet 1/1  ·  sensor_frontend.kicad_sch  ·  seed 0xED2A",
            fontsize=8, color=MUTED, family="monospace")

    poster_save(fig, out_path)


# ---- PCB layout mock --------------------------------------------------------
def draw_pcb_mock(title: str, out_path: Path, flavour: str = "kicad"):
    set_style()
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")

    # title bar
    ax.add_patch(Rectangle((0, 8.2), 14, 0.8, facecolor=INK, edgecolor="none"))
    ax.text(0.3, 8.6, title, fontsize=16, color=PAPER, weight="bold", va="center")
    flavour_label = {"kicad": "KiCad 8 · .kicad_pcb",
                     "librepcb": "LibrePCB 1.0 · .lp (layout)"}[flavour]
    ax.text(13.7, 8.6, flavour_label, fontsize=10, color=PAPER,
            family="monospace", va="center", ha="right")

    # board outline (2-layer, rounded)
    ax.add_patch(FancyBboxPatch((1.0, 1.0), 12, 6.6,
                                boxstyle="round,pad=0.04,rounding_size=0.25",
                                facecolor="#0d5a36", edgecolor=INK, lw=1.8))
    # silkscreen title
    ax.text(7.0, 7.0, "SENSOR FRONTEND R1", fontsize=14, color="#e8e2cc",
            ha="center", family="monospace", weight="bold")

    rng = np.random.default_rng(0xED2A)
    # traces (orange amber for top, teal for bottom)
    for _ in range(22):
        segs = rng.integers(2, 5)
        x0 = rng.uniform(1.5, 12.5)
        y0 = rng.uniform(1.5, 6.6)
        pts_x, pts_y = [x0], [y0]
        for _ in range(segs):
            dx = rng.choice([-1.2, -0.8, 0.8, 1.2, 0])
            dy = rng.choice([-0.8, 0.8, 0])
            if dx == 0 and dy == 0:
                dx = 0.8
            pts_x.append(np.clip(pts_x[-1] + dx, 1.4, 12.6))
            pts_y.append(np.clip(pts_y[-1] + dy, 1.4, 6.7))
        col = AMBER if rng.random() < 0.55 else TEAL
        ax.plot(pts_x, pts_y, color=col, lw=1.6, solid_capstyle="round", alpha=0.9)

    # footprints
    def soic(cx, cy, w, h, pins, label):
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h,
                               facecolor="#2a2b2d", edgecolor="#e8e2cc", lw=0.8))
        ax.text(cx, cy, label, fontsize=8, ha="center", va="center",
                color="#e8e2cc", family="monospace")
        for i in range(pins // 2):
            py = cy - h / 2 + (i + 0.5) * h / (pins / 2)
            ax.add_patch(Rectangle((cx - w / 2 - 0.18, py - 0.06), 0.18, 0.12,
                                   facecolor="#e8c16a", edgecolor="none"))
            ax.add_patch(Rectangle((cx + w / 2, py - 0.06), 0.18, 0.12,
                                   facecolor="#e8c16a", edgecolor="none"))

    soic(4.0, 4.0, 1.1, 0.9, 8, "U1")
    soic(9.5, 4.2, 0.9, 0.7, 8, "U2")

    # 0603 passives
    def passive(cx, cy, label):
        ax.add_patch(Rectangle((cx - 0.12, cy - 0.07), 0.24, 0.14,
                               facecolor="#8a8a8a", edgecolor=INK, lw=0.5))
        ax.text(cx, cy + 0.17, label, fontsize=6, ha="center", color="#e8e2cc",
                family="monospace")

    for x, y, lbl in [
        (2.2, 5.0, "C1"), (2.8, 4.2, "R1"), (3.1, 3.1, "R2"),
        (5.1, 4.8, "R3"), (5.9, 4.3, "C2"),
        (6.8, 5.5, "C3"), (7.6, 5.5, "C4"),
        (10.9, 4.8, "Rout"), (11.5, 3.8, "Cout"),
        (2.0, 2.0, "TP1"), (12.0, 2.0, "TP2"),
    ]:
        passive(x, y, lbl)

    # connectors
    ax.add_patch(Rectangle((1.2, 1.6), 0.3, 1.2, facecolor="#d1a04a", edgecolor=INK))
    ax.text(1.35, 1.4, "J1 IN", fontsize=7, ha="center", color="#e8e2cc",
            family="monospace")
    ax.add_patch(Rectangle((12.5, 1.6), 0.3, 1.2, facecolor="#d1a04a", edgecolor=INK))
    ax.text(12.65, 1.4, "J2 OUT", fontsize=7, ha="center", color="#e8e2cc",
            family="monospace")

    # vias
    for _ in range(16):
        vx = rng.uniform(1.5, 12.5)
        vy = rng.uniform(1.6, 6.6)
        ax.add_patch(plt.Circle((vx, vy), 0.06, facecolor="#8a6020", edgecolor=INK, lw=0.4))

    # dimensions
    ax.annotate("", xy=(1.0, 0.7), xytext=(13.0, 0.7),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.8))
    ax.text(7.0, 0.45, "50.0 mm", fontsize=8, ha="center", family="monospace")
    ax.annotate("", xy=(13.5, 1.0), xytext=(13.5, 7.6),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.8))
    ax.text(13.75, 4.3, "27.5 mm", fontsize=8, rotation=90, va="center",
            family="monospace")

    ax.text(0.3, 0.05, "board outline  ·  2-layer · 1.6mm FR-4  ·  27 footprints · 64 nets",
            fontsize=8, color=MUTED, family="monospace")

    poster_save(fig, out_path)
