# 0 A.D. civilization stats workbook

Template-resolved unit, building, gather, and technology data for the fifteen playable civilizations in current [0 A.D.](https://play0ad.com/) `main`, plus a 1–5 scorecard rebuilt from those numbers instead of forum tier lists.

**Rebuild the workbook** from the committed sheets:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/csv_to_xlsx.py   # writes data/0AD_civ_strengths.xlsx
```

`csv_to_xlsx.py` reads `data/sheets/*.csv`, or `*.csv.gz.b64` when a raw CSV is packed (all_units, buildings, all_techs).

**Sheet CSVs:** [`data/sheets/`](data/sheets/)

**Repo:** https://github.com/jeremy-karisai/0ad-civ-stats

The binary `.xlsx` is not stored in git (GitHub contents API is text-oriented). A ready-made copy is also in [Google Drive](https://docs.google.com/spreadsheets/d/1C5JfnjCoz8MNxMP7V6SZsDX4Dao9PGth/edit?usp=drivesdk).

This is a fan analysis of Wildfire Games' free, open-source RTS. It is not an official WFG release.

## Snapshot

| Field | Value |
|---|---|
| Game tree | [`gitea.wildfiregames.com/0ad/0ad`](https://gitea.wildfiregames.com/0ad/0ad) `main` |
| Cloned | 2026-08-31, sparse (templates + civ JSON + technologies only; no LFS art) |
| Resolver | Official `SimulTemplateEntity` from `source/tools/entity/scriptlib` |
| Playable civs | `achae` (Achaemenid Persians), `athen`, `brit`, `cart`, `gaul`, `germ`, `han`, `iber`, `kush`, `mace`, `maur`, `ptol`, `rome`, `sele`, `spart` |
| Persians | Folder/code is `achae`, not `pers`. Confirmed via Achaemenid catafalque, Satrapy Tribute, Darics. |

Release 28 (“Boiorix”) shipped Germans. This dump is **current main shortly after that**, not a frozen `r28` tag. Some older wiki claims are already stale here — Athens has a battering ram and a siege catapult in this tree.

## What is in the workbook

| Sheet | Contents |
|---|---|
| Readme | Snapshot and method |
| Scorecard | 1–5 axes: Early, Eco, Infantry, Cavalry, Ranged, Siege, Navy, Late, Defense, Flex |
| Scoring rules | Exact bump rules for each axis |
| All units | Inherited combat stats for 499 templates (basic citizen ranks + champs/heroes/siege/ships) |
| Citizen infantry / Champions / Siege and crush / Ships | Slices of the same table |
| Houses | Resolved house HP, build time, wood cost, population bonus |
| Buildings | ~490 structures (CC, barracks, walls, unique buildings) |
| Gather rates | `ResourceGatherer` rates on civilians and a citizen-soldier proxy |
| Civ bonuses | `simulation/data/civs/*.json` |
| Civ-gated techs | Technology JSON files whose requirements mention a civ |
| All techs | 177 technologies |
| Roster matrix | Presence/absence of slings, bows, rams, dogs, crush units, warships |

## How the numbers were built

0 A.D. units are XML templates with parents and mixins (`parent="hoplite|template_unit_infantry_melee_spearman"`). Child files override or apply `op="add"` / `op="mul"`. Reading a single civ file without walking the parent chain gives the wrong HP, cost, and damage.

Pipeline:

1. Sparse-clone `0ad/0ad` with `GIT_LFS_SKIP_SMUDGE=1` and check out `binaries/data/mods/public/simulation/{templates,data}` plus `source/tools/entity`.
2. `scripts/extract_0ad_units.py` loads every `units/<civ>/*.xml` (skipping `_a` / `_e` promotion ranks) through `SimulTemplateEntity.load_inherited()`.
3. DPS is `(Hack + Pierce + Crush + Poison + Fire) * 1000 / RepeatTime_ms`. Prepare time, projectile spread, accuracy, splash, resistance, forge upgrades, and formations are **not** folded in.
4. `scripts/build_0ad_workbook.py` resolves house/CC/military/wall templates the same way, parses 177 technology JSON files, reads civ bonus JSON, and writes the `.xlsx`.
5. The 1–5 scorecard is a documented model on top of those tables. Rules live on the **Scoring rules** sheet.

### What the raw templates actually showed

- Most citizen soldiers share generic parents. Non-merc citizen infantry DPS stdev in this dump is about **1.8**. A “stronger slinger civ” is usually a roster hole or a unique/merc, not a different slinger XML.
- Generic slinger: 50 HP, 45 m, 8.4 DPS, 50 food / 20 wood, 10 s.
- Generic spearman: 100 HP, 4 m, 8.5 DPS, 50 food / 50 wood, 10 s.
- Generic archer: 50 HP, 60 m, 5.76 DPS. Mauryan Longbowman matches this parent. The extra range is **Archery Tradition** (`MaxRange +10`, Village, civs `kush` / `maur` / `achae`), not a unique longbow template.
- Civilian gather rates are shared (fruit 1, grain 0.5, wood 0.7, stone/metal 0.35). Eco identity is worker elephants / supply wagons, house parent, and civ-gated farm/minister/trade techs.
- Houses use two parents: small (30 s, 75 wood, 800 HP, +5 pop) and big (50 s, 150 wood, 1200 HP, +10 pop).
- German Village crush is real XML: Cimbrian Clubman (7 crush) and Log Ram (120 crush, 300 HP, 200 wood / 75 metal, 20 s).
- Ramming ships were excluded from the siege score so “has a navy ram” does not count as a siege ladder.

### Scorecard (this snapshot)

| Civ | Early | Eco | Inf | Cav | Range | Siege | Navy | Late | Def | Flex | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ptolemies | 4 | 4 | 4 | 4 | 5 | 5 | 5 | 4 | 4 | 5 | 4.4 |
| Carthaginians | 3 | 3 | 4 | 4 | 5 | 5 | 5 | 4 | 5 | 5 | 4.3 |
| Han | 3 | 4 | 4 | 4 | 5 | 5 | 3 | 4 | 4 | 4 | 4.0 |
| Athenians | 3 | 3 | 4 | 3 | 5 | 5 | 5 | 4 | 4 | 3 | 3.9 |
| Germans | 5 | 4 | 4 | 4 | 3 | 5 | 3 | 4 | 4 | 3 | 3.9 |
| Seleucids | 3 | 3 | 4 | 4 | 4 | 5 | 3 | 4 | 4 | 5 | 3.9 |
| Romans | 3 | 3 | 5 | 4 | 2 | 5 | 4 | 4 | 4 | 4 | 3.8 |
| Macedonians | 3 | 3 | 4 | 4 | 5 | 5 | 3 | 4 | 4 | 3 | 3.8 |
| Achaemenids | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 3.6 |
| Iberians | 4 | 3 | 4 | 4 | 3 | 3 | 3 | 4 | 5 | 3 | 3.6 |
| Kushites | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| Britons | 5 | 3 | 4 | 4 | 3 | 3 | 2 | 4 | 4 | 3 | 3.5 |
| Mauryans | 3 | 4 | 4 | 4 | 4 | 3 | 2 | 4 | 4 | 3 | 3.5 |
| Gauls | 4 | 3 | 4 | 4 | 3 | 3 | 2 | 4 | 4 | 3 | 3.4 |
| Spartans | 3 | 3 | 5 | 3 | 2 | 4 | 2 | 4 | 2 | 1 | 2.9 |

Averages are not a tier list. Sparta is supposed to look empty on Flex / Navy / Range.

## Reproduce

You need a checkout of 0 A.D. `main` (templates + `source/tools/entity` is enough).

```bash
python3 -m pip install -r requirements.txt
export ZEROAD_ROOT=/path/to/0ad
python3 scripts/extract_0ad_units.py
python3 scripts/build_0ad_workbook.py
```

`build_0ad_workbook.py` expects the official `scriptlib.SimulTemplateEntity` on `sys.path` and writes `data/0AD_civ_strengths.xlsx`.

To rebuild a workbook from the committed sheet CSVs only (no 0 A.D. checkout):

```bash
python3 scripts/csv_to_xlsx.py
```

## What this still does not include

- Forge `soldier_attack_*` stacks applied onto unit rows
- Hero / structure auras
- Formation bonuses
- Live lobby win rates or Petra AI strength
- A frozen R28 tag (this is `main`)

## License

- Analysis scripts and workbook layout in this repo: MIT (see `LICENSE`).
- Underlying 0 A.D. templates and engine code: [GPL-2.0-or-later](https://gitea.wildfiregames.com/0ad/0ad).
- 0 A.D. art (not shipped here): CC BY-SA 3.0.

0 A.D. is a trademark of Wildfire Games. This project is independent.
