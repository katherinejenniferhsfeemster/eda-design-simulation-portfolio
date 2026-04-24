"""LibrePCB case: second layout of the same sensor frontend netlist, using
LibrePCB's native project format (UUID-indexed s-expression files under
a `.lppz`-style directory tree).

LibrePCB's project is a **directory** with:
- project/project.lpp          (project metadata)
- project/metadata.lp          (s-expr metadata)
- circuit/circuit.lp           (netlist)
- boards/default/board.lp      (board layout)
- library/                     (embedded symbol/footprint copies)

We emit a minimal but schema-valid tree.
"""
from __future__ import annotations

import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT / "cases" / "librepcb" / "sensor_frontend.lpp"
ASSETS = ROOT / "assets" / "librepcb"


def u() -> str:
    return str(uuid.uuid4())


PROJECT_LPP = """(librepcb_project (version "1.0.0")
  (name "Sensor Frontend")
  (author "Katherine Feemster")
  (version_str "R1")
  (created "2026-04-24T10:00:00Z")
  (attribute "DESCRIPTION" (type string) (unit "")
    (value "ECG-style analog frontend · second layout in LibrePCB"))
)
"""


def circuit_lp() -> str:
    return f"""(librepcb_circuit (version "1.0.0")
  (netclass {u()} (name "default"))

  (component {u()}
    (name "U1") (value "INA128") (lib_cmp {u()})
  )
  (component {u()}
    (name "U2") (value "OPA2348") (lib_cmp {u()})
  )
  (component {u()} (name "R1") (value "1M"))
  (component {u()} (name "R2") (value "1M"))
  (component {u()} (name "R3") (value "10k"))
  (component {u()} (name "C1") (value "100nF"))
  (component {u()} (name "C2") (value "15nF"))
  (component {u()} (name "J1") (value "IN"))
  (component {u()} (name "J2") (value "AOUT"))

  (netsignal {u()} (name "GND")       (auto_name false))
  (netsignal {u()} (name "+3V3")      (auto_name false))
  (netsignal {u()} (name "IN")        (auto_name false))
  (netsignal {u()} (name "V_FILT_HP") (auto_name false))
  (netsignal {u()} (name "V_AMP")     (auto_name false))
  (netsignal {u()} (name "V_FILT_LP") (auto_name false))
  (netsignal {u()} (name "AOUT")      (auto_name false))
)
"""


def board_lp() -> str:
    return f"""(librepcb_board (version "1.0.0")
  (uuid {u()})
  (name "default")
  (design_rules
    (stopmask_clearance_ratio 0.0)
    (stopmask_min_clearance 0.1)
    (stopmask_max_clearance 0.15)
    (creammask_clearance_ratio 0.1)
  )

  (outline
    (vertex (position "0.0mm" "0.0mm"))
    (vertex (position "50.0mm" "0.0mm"))
    (vertex (position "50.0mm" "27.5mm"))
    (vertex (position "0.0mm" "27.5mm"))
    (vertex (position "0.0mm" "0.0mm"))
  )

  (device {u()} (component_uuid {u()}) (lib_device {u()})
    (position "12.0mm" "14.0mm") (rotation "0.0") (mirror false))
  (device {u()} (component_uuid {u()}) (lib_device {u()})
    (position "38.0mm" "14.0mm") (rotation "0.0") (mirror false))

  (plane {u()} (layer "bot_cu") (net {u()})
    (vertex (position "1.0mm" "1.0mm"))
    (vertex (position "49.0mm" "1.0mm"))
    (vertex (position "49.0mm" "26.5mm"))
    (vertex (position "1.0mm" "26.5mm"))
    (vertex (position "1.0mm" "1.0mm"))
  )
)
"""


METADATA_LP = f"""(librepcb_metadata (version "1.0.0")
  (uuid {u()})
  (description "Second layout of the sensor frontend netlist in LibrePCB.")
  (keywords "eda pcb librepcb analog afe")
)
"""


def main():
    PROJ.mkdir(parents=True, exist_ok=True)
    (PROJ / "project").mkdir(exist_ok=True)
    (PROJ / "circuit").mkdir(exist_ok=True)
    (PROJ / "boards" / "default").mkdir(parents=True, exist_ok=True)
    (PROJ / "library").mkdir(exist_ok=True)

    (PROJ / "project" / "project.lpp").write_text(PROJECT_LPP)
    (PROJ / "project" / "metadata.lp").write_text(METADATA_LP)
    (PROJ / "circuit" / "circuit.lp").write_text(circuit_lp())
    (PROJ / "boards" / "default" / "board.lp").write_text(board_lp())
    (PROJ / ".librepcb-project").write_text("1")  # marker file

    ASSETS.mkdir(parents=True, exist_ok=True)
    from art_helpers import draw_pcb_mock, draw_schematic_mock
    draw_schematic_mock("Sensor Frontend — LibrePCB re-layout",
                        ASSETS / "schematic.png", flavour="librepcb")
    draw_pcb_mock("Sensor Frontend — LibrePCB placement",
                  ASSETS / "pcb.png", flavour="librepcb")

    print("[librepcb] project tree + posters")


if __name__ == "__main__":
    main()
