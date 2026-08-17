# Pre-CU Soft SQF + Deploy Todo

Living checklist for the soft Strength/Quickness/Focus HAM approximation and related open branches.

**Repos (2026-08-17):** Soft SQF cost formula + racial/profession grants are on `feature/precu-soft-sqf-ham` (not yet merged to master unless noted).

---

## How to use this file

1. Pull the branch for the change you want.
2. Run the **Deploy commands** for that commit (Java rebuild and/or DataTableTool + iff copy).
3. Full **GameServer restart** after class changes; **client TRE** when shared tables change.
4. Mark done only after in-game smoke test.

Canonical rules: `WORKFLOW.md`. Status board: `PROGRESS.md`.

---

## Soft SQF — current branch (do this first)

### PR / compare links

| Repo | Branch | Compare / PR |
|------|--------|----------------|
| dsrc | `feature/precu-soft-sqf-ham` | https://github.com/daquorm89/dsrc/compare/feature/precu-soft-sqf-ham |
| swg-main (docs) | `feature/progress-soft-sqf-ham` | https://github.com/daquorm89/swg-main/compare/feature/progress-soft-sqf-ham |

### Commits on `feature/precu-soft-sqf-ham` (apply in order)

#### 1) Cost formula + H/A/M drain

**Commit:** `Pre-CU soft SQF: approximate Strength/Quickness/Focus via skill mods on HAM costs`

**Files:** `combat_engine.java`, `combat.java`

**What it does:** Loads `healthCost`/`mindCost`; `finalCost = base * (1 - mod/1400)`; drains Health+Action+Mind.

**Pull + deploy:**

```bash
cd ~/repos/swg-main/dsrc
git fetch origin
git checkout feature/precu-soft-sqf-ham
git pull origin feature/precu-soft-sqf-ham

cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/combat.java
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/combat_engine.java
# full GameServer restart
```

**Smoke:** Use a special with `actionCost > 0`; Action should drop. With 0 SQF mods, cost = table base.

#### 2) Racial + profession SQF grants

**Commit:** `Pre-CU soft SQF: racial + profession skill-mod grants for strength/quickness/focus`

**Files:** `skill.java`, `skills.tab`

**What it does:** Racial strength/quickness/focus from `racial_mods.tab` applied as skill mods on Pre-CU pool recalc; modest novice profession grants.

**Pull + deploy (after commit 1 on same branch):**

```bash
cd ~/repos/swg-main/dsrc
git fetch origin
git checkout feature/precu-soft-sqf-ham
git pull origin feature/precu-soft-sqf-ham

cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/skill.java

cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/skill
~/repos/swg-main/build/bin/DataTableTool -i skills.tab
SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/skill/skills.iff
find ~/repos/swg-main -name 'skills.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;
# pack same skills.iff into client TRE if you use shared skills UI
# full GameServer restart
# re-grant profession novices so new SKILL_MODS apply; relog so recalcPlayerPools runs
```

**Smoke:** Human/Wookiee/Bothan etc. should show different special costs; brawler novice should reduce Health-cost specials slightly vs naked non-brawler.

### REVERT soft SQF entirely

```bash
cd ~/repos/swg-main/dsrc
git fetch origin
git checkout master
git pull origin master
# or: git revert the two soft-SQF commits on the feature branch

cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/combat.java
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/combat_engine.java
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/skill.java

cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/skill
~/repos/swg-main/build/bin/DataTableTool -i skills.tab
SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/skill/skills.iff
find ~/repos/swg-main -name 'skills.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;
# restart GameServer
# optional: clear objvars precu.soft_sqf.racial_strength / _quickness / _focus on toons
```

Details also in `PROGRESS.md` under **P6 soft-SQF**.

---

## Soft SQF — next steps (not coded yet)

| Step | Goal |
|------|------|
| Armor encumbrance → soft SQF penalty | Heavy armor raises special costs again |
| Food / doctor / buff targets | Buff strength/quickness/focus mods |
| Retune base healthCost/actionCost/mindCost | Pre-CU-ish baselines on hybrid combat_data rows |
| In-game balance pass | Naked vs invested vs armored special economy |

---

## Other recent Pre-CU branches (dsrc)

Pull pattern for any branch:

```bash
cd ~/repos/swg-main/dsrc
git fetch origin
git checkout <branch>
git pull origin <branch>
# then Java / DataTableTool as required by that change
```

| Branch | Compare link | Typical deploy |
|--------|--------------|----------------|
| `feature/precu-soft-sqf-ham` | https://github.com/daquorm89/dsrc/compare/feature/precu-soft-sqf-ham | combat.java, combat_engine.java, skill.java, skills.tab |
| `feature/precu-sample-and-cooldowns` | https://github.com/daquorm89/dsrc/compare/feature/precu-sample-and-cooldowns | survey_tool_script.java, command_table.tab (+ client TRE) |
| `feature/precu-jedi-saber-xp` | https://github.com/daquorm89/dsrc/compare/feature/precu-jedi-saber-xp | xp.java |
| `feature/precu-jedi-reconnect-retire-nge` | https://github.com/daquorm89/dsrc/compare/feature/precu-jedi-reconnect-retire-nge | skills.tab, combat.java, combat_weapon.java, base_player.java, … |
| `feature/precu-jedi-saber-equip-diagnostic` | https://github.com/daquorm89/dsrc/compare/feature/precu-jedi-saber-equip-diagnostic | combat.java, combat_weapon.java, nomove_base.java, skill_template.java |
| `feature/wire-empty-jedi-saber-schematic-groups` | https://github.com/daquorm89/dsrc/compare/feature/wire-empty-jedi-saber-schematic-groups | schematic_group.tab |
| `feature/fix-missing-powerup-schematic-refs` | https://github.com/daquorm89/dsrc/compare/feature/fix-missing-powerup-schematic-refs | schematic_group.tab, crafting_quests.tab |
| `feature/precu-ham-racial-core3` | https://github.com/daquorm89/dsrc/compare/feature/precu-ham-racial-core3 | skill.java, racial_mods.tab, attribute_limits.tab |
| `feature/precu-ham-pools-core3` | https://github.com/daquorm89/dsrc/compare/feature/precu-ham-pools-core3 | skill.java (pool baselines) |
| `feature/precu-posture-requires-target` | https://github.com/daquorm89/dsrc/compare/feature/precu-posture-requires-target | combat posture Java / data as in branch |
| `feature/precu-schematic-groups-restore` | https://github.com/daquorm89/dsrc/compare/feature/precu-schematic-groups-restore | schematic_group.tab |

Many of these may already be **merged to master** — always:

```bash
cd ~/repos/swg-main/dsrc
git fetch origin
git log origin/master --oneline -20
git merge-base --is-ancestor origin/<branch> origin/master && echo MERGED || echo NOT_MERGED
```

### Generic DataTable rebuild + copy

```bash
# Example: command_table
cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/command
~/repos/swg-main/build/bin/DataTableTool -i command_table.tab
SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/command/command_table.iff
find ~/repos/swg-main -name 'command_table.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;
# pack into client TRE for shared tables; restart client
```

### Generic single-file Java rebuild

```bash
cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/<path>/<File>.java
# confirm timestamp under data/sku.0/sys.server/compiled/game/...
find ~/repos/swg-main/data -name '<File>.class' | xargs ls -la
# full GameServer restart
```

---

## swg-main doc branches

| Branch | Compare |
|--------|---------|
| `feature/progress-soft-sqf-ham` | https://github.com/daquorm89/swg-main/compare/feature/progress-soft-sqf-ham |
| `feature/progress-precu-jedi` | https://github.com/daquorm89/swg-main/compare/feature/progress-precu-jedi |
| `feature/workflow-client-jedi-fs-skills` | https://github.com/daquorm89/swg-main/compare/feature/workflow-client-jedi-fs-skills |

```bash
cd ~/repos/swg-main
git fetch origin
git checkout feature/progress-soft-sqf-ham
git pull origin feature/progress-soft-sqf-ham
# docs only — no server rebuild required
```

---

## Client-tools (Windows)

Repo: https://github.com/daquorm89/client-tools  

Example Jedi/FS skills UI branch (from prior sessions):

```powershell
cd "E:\swg-source VM\SWGSource Client v3.0\client-tools"
git fetch https://github_pat_TOKEN@github.com/daquorm89/client-tools.git feature/precu-skills-show-jedi-fs
git checkout feature/precu-skills-show-jedi-fs
# VS 2013: src\build\win32\swg.sln → Release|Win32 → Build SwgClient
# Deploy new SwgClient_r.exe (backup first)
```

Shared table client TRE: after any shared `.iff` change, pack the same file the server uses into the client TRE and restart the client.

---

## Recommended deploy order right now

1. [ ] Merge or checkout `feature/precu-soft-sqf-ham` (both commits)
2. [ ] Rebuild `combat.java`, `combat_engine.java`, `skill.java`
3. [ ] Rebuild `skills.iff` + copy; client TRE if needed
4. [ ] Restart GameServer; relog / re-grant novices
5. [ ] Smoke: special costs with/without profession; species differences
6. [ ] Only then: armor soft-SQF penalty / cost retune

---

## Notes

- Soft SQF is **not** true 9-stat HAM (P6.8 remains deferred).
- Expertise freeshot / expertise action % still apply before soft SQF on the action leg.
- `command_table` cooldowns (sample-and-cooldowns branch) are separate from SQF costs.
