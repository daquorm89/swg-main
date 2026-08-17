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


#### 3) Cost retune + armor tax + food/buff modified

**Commit:** `Pre-CU soft SQF: cost retune, armor tax, food/buff modified mods`

**Files:** `combat_data.tab`, `combat.java`, `buff.tab`

**What it does:**
- 97 Pre-CU action-only specials get Health/Mind costs (0.8× / 0.6× Action)
- Armor fire-rate penalty reduces effective SQF (heavy armor = higher costs)
- Food `*_modified` mods count toward SQF; selected foods gain `quickness_modified` / `focus_modified`

**Pull + deploy:**

```bash
cd ~/repos/swg-main/dsrc
git fetch origin
git checkout feature/precu-soft-sqf-ham
git pull origin feature/precu-soft-sqf-ham

cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/combat.java
# also rebuild combat_engine + skill if not already on this branch deploy

cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/combat
~/repos/swg-main/build/bin/DataTableTool -i combat_data.tab
SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.iff
find ~/repos/swg-main -name 'combat_data.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;

cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/buff
~/repos/swg-main/build/bin/DataTableTool -i buff.tab
SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/buff/buff.iff
find ~/repos/swg-main -name 'buff.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;
# pack combat_data.iff + buff.iff into client TRE if shared
# full GameServer restart (+ client)
```

**Smoke / balance pass:**
- [ ] Naked Pre-CU special: Action ~40–125 plus Health/Mind on retuned rows
- [ ] Brawler/marksman novice + racial: measurable cost drop vs naked
- [ ] Wear heavy armor (fire-rate penalty active): costs rise vs same skills naked
- [ ] Eat caf / air cake / havla: further cost drop via modified mods
- [ ] NGE expertise specials with 2000+ Action unchanged (not retuned)

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

| Step | Status |
|------|--------|
| Retune base H/A/M on Pre-CU rows | Done (commit 3) |
| Armor → soft SQF penalty | Done (fireRatePenalty tax) |
| Food / buff modified targets | Done (selected foods + `*_modified` wiring) |
| In-game balance smoke | **Your turn** — checklist under commit 3 |

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

1. [ ] Checkout `feature/precu-soft-sqf-ham` (all 3 commits)
2. [ ] Rebuild `combat.java`, `combat_engine.java`, `skill.java`
3. [ ] Rebuild `skills.iff`, `combat_data.iff`, `buff.iff` + copy; client TRE
4. [ ] Restart GameServer; relog / re-grant novices
5. [ ] Balance smoke checklist (commit 3 section)
6. [ ] Merge to master only after smoke looks good

---

## Notes

- Soft SQF is **not** true 9-stat HAM (P6.8 remains deferred).
- Expertise freeshot / expertise action % still apply before soft SQF on the action leg.
- `command_table` cooldowns (sample-and-cooldowns branch) are separate from SQF costs.
