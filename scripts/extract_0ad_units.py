#!/usr/bin/env python3
"""Resolve 0 A.D. unit templates and dump a flat stats table."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ZEROAD_ROOT = Path(os.environ.get("ZEROAD_ROOT", "/tmp/0ad-src/0ad"))
sys.path.append(str(ZEROAD_ROOT / "source/tools/entity"))
from scriptlib import SimulTemplateEntity  # noqa: E402

ROOT = ZEROAD_ROOT
MODS = ROOT / "binaries/data/mods"
TEMPLATES = MODS / "public/simulation/templates"
OUT = Path(os.environ.get("OUT_CSV", "data/0ad_units_resolved.csv"))

ATTACK_TYPES = ["Hack", "Pierce", "Crush", "Poison", "Fire"]

PLAYABLE = [
    "achae", "athen", "brit", "cart", "gaul", "germ", "han", "iber",
    "kush", "mace", "maur", "ptol", "rome", "sele", "spart",
]


def text(el, default=""):
    return (el.text or default) if el is not None else default


def num(el, default=0.0):
    if el is None or el.text in (None, ""):
        return default
    try:
        return float(el.text)
    except ValueError:
        return default


def tokens(el):
    if el is None or not el.text:
        return []
    return [t for t in el.text.split() if t]


def dps(damage_sum, repeat_ms):
    if not repeat_ms:
        return 0.0
    return damage_sum * 1000.0 / repeat_ms


def classify(path: str, classes: list[str], visible: list[str]) -> str:
    blob = " ".join([path] + classes + visible).lower()
    if "hero" in blob:
        return "hero"
    if "siege" in blob or "ram" in blob or "onager" in blob or "bolt" in blob:
        return "siege"
    if "ship" in blob:
        return "ship"
    if "elephant" in blob and "champion" in blob:
        return "champion_elephant"
    if "champion" in blob and "cavalry" in blob:
        return "champion_cavalry"
    if "champion" in blob:
        return "champion_infantry"
    if "cavalry" in blob:
        return "citizen_cavalry"
    if "infantry" in blob:
        return "citizen_infantry"
    if "civilian" in blob or "female" in blob or "support" in blob:
        return "support"
    return "other"


def extract_attack(template, kind):
    node = template.find(f"./Attack/{kind}")
    if node is None:
        return {}
    dmg = {t: num(node.find(f"./Damage/{t}")) for t in ATTACK_TYPES}
    total = sum(dmg.values())
    repeat = num(node.find("./RepeatTime"))
    bonuses = []
    bnode = node.find("./Bonuses")
    if bnode is not None:
        for bonus in bnode:
            bonuses.append(
                {
                    "name": bonus.tag,
                    "classes": text(bonus.find("Classes")),
                    "mult": num(bonus.find("Multiplier"), 1.0),
                }
            )
    return {
        "kind": kind,
        "range": num(node.find("./MaxRange")),
        "repeat_ms": repeat,
        "dps": round(dps(total, repeat), 3),
        **{f"dmg_{t.lower()}": dmg[t] for t in ATTACK_TYPES},
        "bonuses": "; ".join(f"{b['name']}:{b['mult']}x vs {b['classes']}" for b in bonuses),
    }


def main():
    sim = SimulTemplateEntity(MODS, None)
    rows = []
    unit_files = sorted(TEMPLATES.glob("units/*/*.xml"))
    print(f"found {len(unit_files)} unit xml files")
    for fp in unit_files:
        rel = str(fp.relative_to(TEMPLATES)).replace("\\", "/")
        vfs = rel[:-4]
        civ = fp.parent.name
        if civ not in PLAYABLE:
            continue
        if fp.stem.endswith("_a") or fp.stem.endswith("_e"):
            continue
        try:
            template = sim.load_inherited("simulation/templates/", vfs, ["public"])
        except Exception as exc:
            print(f"FAIL {vfs}: {exc}")
            continue
        ident = template.find("./Identity")
        classes = tokens(ident.find("Classes") if ident is not None else None)
        visible = tokens(ident.find("VisibleClasses") if ident is not None else None)
        role = classify(rel, classes, visible)
        melee = extract_attack(template, "Melee")
        ranged = extract_attack(template, "Ranged")
        primary = ranged if ranged else melee
        res = template.find("./Resistance/Entity/Damage")
        cost = template.find("./Cost/Resources")
        row = {
            "civ": civ,
            "template": vfs,
            "name": text(ident.find("GenericName") if ident is not None else None) or fp.stem,
            "specific": text(ident.find("SpecificName") if ident is not None else None),
            "rank": text(ident.find("Rank") if ident is not None else None),
            "role": role,
            "classes": " ".join(classes + visible),
            "hp": num(template.find("./Health/Max")),
            "walk": num(template.find("./UnitMotion/WalkSpeed")),
            "train_s": num(template.find("./Cost/BuildTime")),
            "pop": num(template.find("./Cost/Population"), 1),
            "food": num(cost.find("food") if cost is not None else None),
            "wood": num(cost.find("wood") if cost is not None else None),
            "stone": num(cost.find("stone") if cost is not None else None),
            "metal": num(cost.find("metal") if cost is not None else None),
            "res_hack": num(res.find("Hack") if res is not None else None),
            "res_pierce": num(res.find("Pierce") if res is not None else None),
            "res_crush": num(res.find("Crush") if res is not None else None),
            "atk_kind": primary.get("kind", ""),
            "range": primary.get("range", 0),
            "repeat_ms": primary.get("repeat_ms", 0),
            "dps": primary.get("dps", 0),
            "dmg_hack": primary.get("dmg_hack", 0),
            "dmg_pierce": primary.get("dmg_pierce", 0),
            "dmg_crush": primary.get("dmg_crush", 0),
            "bonuses": primary.get("bonuses", ""),
        }
        row["total_res"] = row["food"] + row["wood"] + row["stone"] + row["metal"]
        row["dps_per_100res"] = round(row["dps"] / row["total_res"] * 100, 3) if row["total_res"] else 0
        row["hp_per_100res"] = round(row["hp"] / row["total_res"] * 100, 3) if row["total_res"] else 0
        rows.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise SystemExit("no rows")
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
