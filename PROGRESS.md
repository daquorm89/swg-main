# Project Progress

Living status board for the NGE → Pre-CU restoration. **Humans and AI agents must read and update this file** when starting or finishing work.

Canonical process rules: [`WORKFLOW.md`](./WORKFLOW.md).

**Reference only (do not merge code from):** [swgemu/Core3](https://github.com/swgemu/Core3) — behavior/spec reference for Pre-CU combat, queue, targeting, HAM. Implement on NGE `dsrc`/`src` hooks only.

---

## How to use this file

1. **Active projects** have a short goal, owner/notes, and a list of **sub-targets**.
2. Mark a sub-target done with `[x]` when it is **merged to master, rebuilt on the server tree, and smoke-tested** (not when merely coded in a branch).
3. Add new sub-targets as discovery requires; keep them small and verifiable.
4. When **every** sub-target under a project is `[x]`:
   - Move the whole project block into **Completed projects**.
   - Replace the sub-target list with a one-line summary + completion date.
   - Do not leave empty shells under Active.
5. Scope expansions (queue / targeting / HAM reconnect) are tracked here once opened; still follow reconnect-over-rewrite and Core3-reference-only rules in `WORKFLOW.md`.
6. Update this file in the **same PR** as the work when practical; otherwise open a tiny follow-up PR so status stays honest.

**Checkbox meaning**

| Mark | Meaning |
|------|---------|
| `[ ]` | Not done / not verified on runnable server |
| `[x]` | Done on master + server verified |
| `[~]` | In progress / partial (optional; prefer splitting into smaller `[ ]` items) |

---

## Active projects

### P1 — Pre-CU combat hybrid (abilities on NGE pipeline)

**Goal:** Pre-CU combat specials execute through NGE `combatStandardAction` + unique `combat_data.tab` rows, with weapon gates, posture specials, and usable status effects. Combat **math may stay NGE-based** where acceptable; posture and state effects should match Pre-CU intent.

**Primary paths:** `dsrc` → `combat_actions.java`, `combat_data.tab`, `command_table.tab`

| ID | Sub-target | Status |
|----|------------|--------|
| P1.1 | Generate hybrid `combat_data.tab` rows from Core3/Pre-CU command data | [x] |
| P1.2 | Add Java entry points in `combat_actions.java` calling `combatStandardAction` | [x] |
| P1.3 | Basic in-game fire (damage/cost/anim) for bulk of hybrid specials | [x] |
| P1.4 | Explicit weapon restrictions via `precuWeaponOk` (not data `weaponType` alone) | [x] |
| P1.5 | Map common Pre-CU states to existing NGE buffs (`buffNameTarget`) | [~] |
| P1.6 | Verify DoTs (`dotType` bleeding/poison/disease/fire) tick as intended | [ ] |
| P1.7 | Smoke-test matrix: wrong weapon fails, right weapon works, sample specials per weapon family | [ ] |
| P1.8 | Tune costs/damage only where hybrid rows feel broken vs intended Pre-CU role | [ ] |
| P1.9 | Attacker posture specials (diveShot / kipUpShot / rollShot): server posture + client visual in sync | [~] |
| P1.10 | Voluntary posture (`stand` / `kneel` / `prone`) responsive; no multi-second false delay from deprecated `defaultTime` | [~] |
| P1.11 | Tumble commands (`tumbleToProne` / `Kneeling` / `Standing`) implemented and usable | [~] |
| P1.12 | Posture-first then combat chain verified in-game (no upright crawl while already prone locomotion) | [ ] |

**Notes**

- **Root cause (posture lag):** `combatStandardAction` stamps `attacker_results.endPosture = getPosture()` at shot time; changing posture *after* the shot leaves the client on the combat visual while server locomotion already matches the new pose. Engine `defaultTime` is **ignored** (`CommandTable.cpp`, deprecated 2005); use `warmupTime` / `executeTime` / `ClientImmediate` / posture-before-combat.
- Branches of record (dsrc): `feature/precu-posture-hard-fix`, `feature/precu-posture-then-combat` (merge + deploy + smoke before `[x]`).
- Core3 ref only: tumble = `setPosture` + combat anim; dive = attacker force-prone as part of attack data — reimplement on NGE hooks, do not import Core3 sources.
- Shared `combat_data.iff` / `command_table.iff` need **server + client TRE** when those tables change (`WORKFLOW.md`).

**Exit criteria:** P1.5–P1.12 done or explicitly deferred; posture specials and tumbles verified in-game.

---

### P2 — Pre-CU skill spine (grants + progression)

**Goal:** Profession skill boxes grant the hybrid commands and progression works for train→use loops.

**Primary paths:** `skills.tab`, trainers, `command_table` / scriptHooks

| ID | Sub-target | Status |
|----|------------|--------|
| P2.1 | Inventory which Pre-CU profession lines are already present vs NGE-only | [ ] |
| P2.2 | Ensure skill boxes grant the hybrid combat commands (scriptHook names match Java) | [ ] |
| P2.3 | Prerequisites / XP types work for at least one full combat line (e.g. Marksman → elite) | [ ] |
| P2.4 | Same for one non-combat or support line if in scope (medic/entertainer/etc.) | [ ] |
| P2.5 | Titles / skill mods for trained boxes verified in-game | [ ] |
| P2.6 | Document how to add the next profession line (pointer in WORKFLOW or here) | [ ] |

**Notes**

- Items/certs only if a box cannot function without them (minimal).
- Schematic-group work (weaponsmith etc.) was handled in earlier dsrc PRs; keep skill grants aligned with live `command_table` names.

**Exit criteria:** At least one complete Pre-CU combat profession train→grant→use loop is verified; P2.1–P2.6 done or consciously deferred into a new project.

---

### P3 — Project process & agent onboarding

**Goal:** Any human or AI can find rules, scope, build commands, and live status without chat archaeology.

| ID | Sub-target | Status |
|----|------------|--------|
| P3.1 | Add `WORKFLOW.md` (full scope, git, build, combat SOP) | [x] |
| P3.2 | Narrow build docs to real commands (`build_java_single.sh`, DataTableTool, client TRE for shared tables) | [x] |
| P3.3 | Scope: loot/world deferred; combat hybrid + queue/targeting/HAM reconnect tracked in this file | [x] |
| P3.4 | Add this `PROGRESS.md` and keep it updated with PRs | [~] |
| P3.5 | Merge workflow/progress docs to `master` on `daquorm89/swg-main` | [ ] |

**Exit criteria:** P3.4–P3.5 `[x]`, then move P3 to Completed (ongoing updates happen in place).

---

### P4 — Pre-CU-style command queue cadence

**Goal:** Combat specials and related commands use the existing NGE `CommandQueue` with Pre-CU-like warmup / execute / cooldown / queue membership — data-driven first, C++ last resort.

**Evidence (do not re-litigate without new findings):**

- Engine: `CommandQueue.cpp` states Waiting → Warmup → Execute; `CP_Immediate` bypass; `m_addToCombatQueue`.
- `CommandTable.cpp`: **`defaultTime` forced to 0** (deprecated 2005); timing from **`warmupTime` / `executeTime`**.
- `command_table.tab`: ~873 rows with `executeTime > 0`; only ~9 with `warmupTime > 0` — cadence is under-specified vs Pre-CU feel.
- Core3 ref: `QueueCommand` priorities IMMEDIATE / FRONT / NORMAL; fail codes e.g. INSUFFICIENTHAM, INVALIDTARGET.

**Primary paths:** `dsrc` → `command_table.tab` (+ client TRE); only if required `src` → `CommandQueue` / `CommandTable`

| ID | Sub-target | Status |
|----|------------|--------|
| P4.1 | Document live queue rules (immediate vs combat queue, which columns matter) in WORKFLOW or here | [ ] |
| P4.2 | Audit combat specials: `addToCombatQueue`, `defaultPriority`, `warmupTime`, `executeTime`, cooldown groups | [ ] |
| P4.3 | Retune a pilot set (e.g. marksman pistol specials + posture-related) for Pre-CU-like queue feel | [ ] |
| P4.4 | In-game verify: queue order, clearability, no false multi-second locks from ignored columns | [ ] |
| P4.5 | Expand retune to remaining hybrid combat commands | [ ] |
| P4.6 | Engine change only if tables cannot express required policy (justify in PR) | [ ] |

**Exit criteria:** Pilot set verified; either P4.5 done or remaining commands listed as follow-ups with owners.

---

### P5 — Pre-CU-style targeting

**Goal:** Offensive specials respect stricter Pre-CU-like target / range / LOS rules using existing NGE validation (`validateTarget`, `cachedCanSee`, range, `validTarget`).

**Evidence:**

- `combat_data.tab` `validTarget`: STANDARD ~1083, NONE ~384, FRIEND ~51, etc.
- `combat_base.java`: `getTarget` / `getIntendedTarget`, LOS (`ALLOWED_LOS_FAILURES = 10`), maxRange, cone/area fields.
- `command_table` `targetType`: often `optional` on NGE rows (soft targeting).
- Core3 ref: `QueueCommand` targetType, maxRangeToTarget, INVALIDTARGET / locomotion masks before execute.

**Primary paths:** `combat_data.tab`, `command_table.tab`, `combat_base.java` / `combat.java` only if table flags insufficient

| ID | Sub-target | Status |
|----|------------|--------|
| P5.1 | Inventory targetType / validTarget / range for hybrid combat commands vs Pre-CU expectations | [ ] |
| P5.2 | Tighten pilot profession specials (require enemy target, range, LOS) where Pre-CU demanded it | [ ] |
| P5.3 | In-game: no target / out of range / LOS fail messages and no silent success | [ ] |
| P5.4 | AoE / cone specials: defender list still correct after tighter primary target rules | [ ] |
| P5.5 | Roll out to remaining hybrid combat commands | [ ] |
| P5.6 | Client soft-tab behavior documented (server cannot fully fix client tab); note limits | [ ] |

**Exit criteria:** Pilot line feels Pre-CU on target errors; P5.6 limits written so agents do not chase client-only bugs in server PRs.

---

### P6 — HAM reconnect (Health / Action / Mind)

**Goal:** Reconnect existing NGE attribute pools and combat cost columns toward Pre-CU HAM spending and gating, without requiring a full Core3 9-stat clone in the first phase.

**Evidence:**

- Engine `Attributes.def`: Health, Constitution, Action, Stamina, Mind, Willpower; `POOLS[] = {H, A, M}`; `CreatureObject` has attributes + **`m_shockWounds`**.
- `combat_data.tab` (~1608 actions): nonzero **actionCost ~1244**, **healthCost ~163**, **mindCost ~153**, all three ~141.
- Live path: `getActionCost` / `drainCombatActionAttributes` / `canDrainCombatActionAttributes` — **Action-centric** (+ expertise freeshot / action mods); Mind second arg used in drain helper; Health cost columns often unused by gate.
- Dormant: `combat_base_old.java` multi-pool cost checks (`intHealthCost` / `intActionCost` / `intMindCost`).
- Core3 ref: 9 primaries (adds Strength, Quickness, Focus); damage and costs across H/A/M; cost adjustment from secondaries.

**Primary paths:** `combat.java`, `combat_base.java`, `combat_data.tab`; optional lessons from `combat_base_old.java`; client UI is a **later** dependency for full feel

| ID | Sub-target | Status |
|----|------------|--------|
| P6.1 | Document current drain path vs table columns (what is charged in-game today) | [ ] |
| P6.2 | Prototype: honor `healthCost` / `actionCost` / `mindCost` on a small command set without expertise freeshot bypass | [ ] |
| P6.3 | Gate execution when any required pool insufficient (Pre-CU-like fail, not only Action) | [ ] |
| P6.4 | In-game verify bars/pools move as expected for pilot set (server logs if client bars lag) | [ ] |
| P6.5 | Decide expertise interaction policy (strip, scale, or keep for NGE hybrid) and apply consistently | [ ] |
| P6.6 | Expand to hybrid combat_data rows; retune absurd NGE action costs if needed | [ ] |
| P6.7 | Shock wounds / wound healing interaction audit (engine + healing scripts) | [ ] |
| P6.8 | Full Core3 9-stat + client HAM UI — **explicitly later / separate phase** | [ ] |

| P6.9 | **Soft SQF (no 9-stat engine)** — approximate Pre-CU Strength/Quickness/Focus via skill mods on ability HAM costs | [~] |

**P6 soft-SQF implementation note (REVERTIBLE)**

Goal: closest Pre-CU HAM *feel* without expanding engine attributes 6→9.

What this is:
- Skill-mod cost formula only (not real Strength/Quickness/Focus attributes)
- Formula (Core3/SWGANH-style): `finalCost = baseCost * (1 - mod/1400)`, clamped to [0, base]
- Mapping: `strength` → Health costs; `quickness` (fallback `agility`) → Action costs; `focus` → Mind costs
- `combat_data.healthCost` / `mindCost` are now loaded and spent (were table columns only; NGE path zeroed them)
- `canDrain` / `drain` gate and spend Health + Action + Mind (Health via `setAttrib`; Action/Mind via native `drainAttributes`)

What this is NOT:
- Full Pre-CU 9-pool HAM (P6.8 stays deferred)
- Automatic grants of strength/quickness/focus on every profession (mods must exist to matter; NGE level `strength`/`agility` may apply for templated chars; pure Pre-CU skill-box chars need grants next)

Files (dsrc branch `feature/precu-soft-sqf-ham`):
- `script/combat_engine.java` — load/store `healthCost`/`mindCost` on `combat_data`
- `script/library/combat.java` — `PRECU_SOFT_SQF_DIVISOR`, `getSoftSqfMod`, `applySoftSqfCost`, full-pool drain/gate, both `getActionCost` overloads

**How to REVERT if it fails:**
1. Revert / drop commits on `feature/precu-soft-sqf-ham` (or restore the two files from master)
2. Rebuild: `./utils/build_java_single.sh` for `combat.java` and `combat_engine.java`
3. Restart GameServer
4. Expected pre-change behavior: Action-only costs; `cost[0]`/`cost[2]` always 0; no SQF formula

Later soft-SQF steps: armor encumbrance penalty to soft mods; food/buff targets; combat_data base cost retune.

**Grants (second commit on `feature/precu-soft-sqf-ham`):**
- Racial strength/quickness/focus from `racial_mods.tab` applied in `recalcPlayerPools` (Pre-CU path) via skill mods; objvars `precu.soft_sqf.racial_*` prevent stacking
- Profession novice SKILL_MODS: brawler strength=50; marksman quickness=50; medic focus=50; scout 25/25; artisan/entertainer focus=25; padawan strength=25,focus=50

See also repo root `todo.md` for PR links and per-commit deploy commands.


**Exit criteria:** Pilot set spends and gates on H/A/M from tables; P6.5 policy recorded; P6.8 remains deferred unless scope explicitly expands.

---


### P7 — Pre-CU Jedi reconnect (retire NGE/CU Jedi)

**Goal:** Players progress on Pre-CU `jedi_*` skill trees (Padawan → Journeyman → Master) with hybrid combat abilities; NGE Force Sensitive class / expertise and CU Force Discipline are not offered as the live Jedi path.

**Primary paths:** `dsrc` → `skills.tab`; combat already hybrid via `combat_data.tab` + `combat_actions.java` for `jedi_combat_data` names.

| ID | Sub-target | Status |
|----|------------|--------|
| P7.1 | Unhide Pre-CU `jedi_*` skill boxes (clear GOD_ONLY / IS_HIDDEN) | [x] (branch `feature/precu-jedi-reconnect-retire-nge`) |
| P7.2 | Hide/retire `force_discipline_*` (CU) | [x] |
| P7.3 | Hide/retire `class_forcesensitive_*` (NGE FS class) | [x] |
| P7.4 | Hide/retire `expertise_fs_*` (NGE FS expertise) | [x] |
| P7.5 | Fix `forceIntimidate` grant → `forceIntimidate1` | [x] |
| P7.6 | Leave Pre-CU `force_sensitive_*` trees available (FS before Padawan) | [x] (unchanged) |
| P7.7 | Rebuild `skills.iff`, smoke-test train Padawan + use saberSlash1 / force power | [ ] |
| P7.8 | Padawan trials / holocron unlock path audit (eligibility → grant novice) | [ ] |
| P7.9 | Force power pool spend on hybrid specials (table costs vs `jedi.drainForcePower`) | [ ] |
| P7.10 | Optional: deepen hybrid rows from dormant `jedi_combat_data.tab` / `jedi_actions.tab` | [ ] |
| P7.11 | Existing characters on NGE FS / discipline — migration or strip guidance | [ ] |

**Notes**

- Combat: ~59 `jedi_combat_data` ability names were already hybrid-wired (command_table + combat_data + Java). Gap was skill visibility, not ability rows.
- `jedi_padawan_novice` still costs **250** skill points (classic whole-pool unlock) — confirm desired balance after smoke test.
- Cert grants (`cert_onehandlightsaber`, etc.) do not need combat_data rows.
- Do not import Core3 Jedi manager; reconnect tables/scripts only.

**Exit criteria:** P7.7 verified in-game; P7.8–P7.11 done or explicitly deferred.

---

### P9 — Droid command module: stale submodule pointer + corrupted obj_attr_n.stf

**Goal:** Multi-droid command module grants the correct number of extra call-out slots, and `obj_attr_n.stf` loads cleanly (no fallback `obj_attr_n:key` text anywhere).

**Primary paths:** `dsrc` submodule pointer (top-level `swg-main`); `serverdata/string/en/obj_attr_n.stf`

| ID | Sub-target | Status |
|----|------------|--------|
| P9.1 | Diagnose why crafted module showed rating "3", droid showed "12", but only granted 1 extra slot | [x] |
| P9.2 | Bump `swg-main`'s `dsrc` submodule pointer from `81aff3771` (pre-#136) to `master` (`c96ae1e6c`), which already contains PRs #137–#140 fixing the schematic's `droid_command_module` experiment range (`10..100` → `0..5`) and `MAX_EXTRA_DROID_COMMAND_SLOTS` (`100` → `5`) | [x] (branch `feature/bump-dsrc-droid-command-fixes`) |
| P9.3 | Diagnose `obj_attr_n.stf` corruption: a locally-edited copy had duplicate id `1492` in the id-table, which fails `LocalizedStringTable::load_0001`'s duplicate-key insert check and aborts loading the **entire table** — explains why *all* attributes showed raw `obj_attr_n:key` text, not just the new ones | [x] |
| P9.4 | Provide corrected `obj_attr_n.stf` (original 1491 entries + 3 new entries with clean unique ids 1492–1494: `recolor_remaining`, `droid_command_module`, `pet_stats.droid_command_module`) | [x] |
| P9.5 | Merge `feature/bump-dsrc-droid-command-fixes` PR, pull on server tree, rebuild Java + recompile `shared_multi_droid_command_module.tpf` → `.iff`, rebuild CRC string table, push to client, restart | [ ] |
| P9.6 | Deploy corrected `obj_attr_n.stf` to server + client string paths, restart | [ ] |
| P9.7 | Re-craft a fresh multi-droid command module post-deploy (existing crafted modules still carry the old bad `10..100`-scale rating baked into their objvar and will not self-correct) and smoke-test: rating 1–5 on the module → same value on the droid's `module_data.droid_command` → call up to `1 + rating` droids | [ ] |
| P9.8 | **New bug found, distinct from P9.2/schematic range:** `dsrc`'s `calcAndSetPrototypeProperties()` (`crafting_base.java`) fires multiple times per single craft (each `OnCraftingExperiment` click, twice inside `OnManufacturingSchematicCreation`, once in `OnFinalizeSchematic`). The `droid_command_module` case in `crafting_base_droid.java` did `setObjVar(prototype, "module_data.droid_command", existing + cmd)` — additive — instead of overwriting like every other attribute case in that switch (`storage_module`, `personality_module`, etc). Each re-fire during the same craft stacked another `+cmd`, so a genuinely-correct module rating of `3` (post-P9.2 fix, 0–5 range working correctly) still ended up as `12` on the resulting droid (~4x from repeated hook calls) — which is why the symptom persisted even after the P9.2 pointer bump. Fixed: branch `feature/fix-droid-command-module-accumulation` on `dsrc` (overwrite instead of add). Compare: https://github.com/daquorm89/dsrc/compare/feature/fix-droid-command-module-accumulation | [ ] (branch pushed, needs merge + swg-main pointer bump + deploy) |
| P9.9 | **Multi-droid formations stack on one spot.** `pet_lib.doPetFormation` passed slot `0` for every `CALLABLE_TYPE_COMBAT_OTHER` (all droids), and `ai_lib.followInWedgeFormation` / `followInColumnFormation` clamp slot `< 1` to `1`, so every droid got the identical follow offset. Fix: new `pet_lib.getDroidFormationPosition(droid, master)` = index in `getActiveDroidVector(master)`, skipping slot 1 if a creature pet is out and slot 2 if a familiar is out (they keep fixed slots 1/2). Branch `feature/droid-formation-slots` on `dsrc` (commit `33a1b101f`, based on `dsrc` master `57c2aeba5`). Compare: https://github.com/daquorm89/dsrc/compare/feature/droid-formation-slots. Deploy: `./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/pet_lib.java`, restart GameServer (no tables, no client files). Smoke: call 2-3 droids (optionally with a pet), say `wedge formation` / `column formation` while on foot and mounted; each droid should hold a different spot. **Unverified:** not compiled (no JDK in sandbox), not tested in game. Possible follow-up: spacing is `getObjectCollisionRadius(master) * 2.25` and may be too tight while mounted | [ ] (**merged** as dsrc PR #184; needs swg-main pointer bump + deploy + smoke) |
| P9.10 | **Droid slot cap + guard only works for first droid.** (a) `module_data.droid_command` is the stacked total of all installed command modules (6 x up to +4 = 24) but `pet_lib.getDroidCommandExtraSlots` treated >5 as a legacy craft and rescaled `(rating+19)/20`, so a displayed `+24` gave only +2 extra droids; cap was also `5`. Fix: rating maps 1:1 to extra slots, `MAX_EXTRA_DROID_COMMAND_SLOTS = 24` (max 25 droids out); attribute displays in `pet.java` / `pet_control_device.java` now show the real computed slot count. (b) `ai/pet_master.java` `getOutCombatCallables` used `callable.getCallable()`, which returns ONE `COMBAT_OTHER` droid, so only the first droid out joined guard assist (`OnAttackerCombatAction` / `OnDefenderCombatAction`). Now includes every droid from `pet_lib.getActiveDroidVector`. (c) `pet_lib.doCommandNum(master, cmd)` (the `droid_guard` / `droid_follow` / `droid_stay`... slash commands) looked up `CALLABLE_TYPE_COMBAT_PET`, but droids are `COMBAT_OTHER`; now fans out to all active droids (release/transfer stay on the first droid). Branch `feature/multi-droid-slots-and-guard` on `dsrc` (commit `892fb9657`, based on `dsrc` master `9e10dfa56`). Compare: https://github.com/daquorm89/dsrc/compare/feature/multi-droid-slots-and-guard. Compiles clean with javac 17 against the dsrc sourcepath (4 files). Deploy: `./utils/build_java_single.sh` for `pet_lib.java`, `pet_master.java`, `pet.java`, `pet_control_device.java` (all under `dsrc/sku.0/sys.server/compiled/game/script/`), restart GameServer; no tables or client files. Smoke: module showing `+24` -> call out >3 droids; `guard` by speech and `/droid_guard`; attack a mob and confirm every droid joins; wedge/column with many droids. **Unverified in game.** Open: 25 AI objects following one player is a server-load risk to watch; old crafted modules keep whatever rating is baked in their objvar (now read 1:1, a bad `12` now gives +12) | [ ] (branch pushed, needs merge + swg-main pointer bump + deploy + smoke) |

**Notes**

- Root cause of P9.1/P9.2: `dsrc` itself was never broken — the fix already existed on `dsrc` master via PR #140. `swg-main`'s submodule pointer just never moved past the earlier `feature/precu-droid-command-module-rebase` merge (#136), so the locally-running server tree was still building the old broken schematic/constant even though upstream `dsrc` was fine. No new source edits were needed, only the pointer bump.
- Root cause of P9.3: confirmed against the actual C++ loader (`LocalizedStringTable::load_0001` / `LocalizedStringTableRW::write` in `src/external/ours/library/localization/src/shared/`). Format is: header (magic `0xabcd` + version + nextId + numEntries) → id-table (ascending, unique ids required) → name-table (alphabetical `key → id`). A duplicate id in the id-table causes the whole-file load to fail via a `std::map` insert-collision check, which is why the symptom was "every attribute string is now raw text," not just the newly-added ones.
- `serverdata/string/en/obj_attr_n.stf` in the repo (and `string/ja/obj_attr_n.stf`) were **not** touched by the corruption — they still match the known-good baseline. The corrupted file only existed in a local/uncommitted working copy.
- Root cause of P9.8: two *separate* bugs were stacking on top of each other. P9.2 fixed the schematic's experiment range so the module itself rolls a genuine 0–5 (confirmed: module showed a correct `3`). But the transfer-to-droid code in `crafting_base_droid.java` re-applied that value additively every time the shared craft hook re-fired within the same craft session, multiplying it up to `12` by the time the droid was finished. The `getDroidCommandExtraSlots()` legacy-rescale fallback (`(rating+19)/20` for anything above 5) then silently absorbed the inflated `12` down to `extra=1`, which is exactly why testing kept showing "only 1 extra droid" even after the P9.2 pointer bump — the accumulation bug was never part of PRs #137–140.

**Exit criteria:** P9.5–P9.8 done; module rating verified end-to-end in-game (module rating == droid's `module_data.droid_command` == no multiplication) with no `obj_attr_n:` fallback text anywhere in the attribute UI.

---

### P10 — AT-XT (craftable walker) fire while driven: mob targeting + ground marker

**Goal:** A driver of the crafted AT-XT can (a) fire without the client auto-aim toggle and (b) get the heavy-weapon-style ground marker and hit the marked spot.

**Primary paths:** `dsrc` -> `command_table.tab` (shared + server), `combat_data.tab`, `combat_actions.java` (`at_xt_vehicle_blaster`), `at_xt_combat.java`

| ID | Sub-target | Status |
|----|------------|--------|
| P10.1 | Investigate why fire failed without auto-aim and why the ground marker never showed | [x] |
| P10.2 | Convert `at_xt_vehicle_blaster` to a location command (`targetType=location`, LOCATION egg, `hoth_scout_cannon` pattern) | [~] (dsrc branch `feature/at-xt-location-ground-target`, commit `0535e3966`) |
| P10.3 | Merge dsrc PR, bump `swg-main` dsrc pin, deploy (Java single-file + DataTableTool + iff copies + client files) | [ ] |
| P10.4 | In-game smoke: marker appears while driving; fires with auto-aim OFF at ground and at a mob; splash hits mobs at marker; auto-aim ON still fires at locked target | [ ] |
| P10.5 | Tune splash radius (`coneLength`), damage, `maxRange`/`maxRangeToTarget` after smoke test | [~] (radius 7.2, cooldownTime now 10.0s) |
| P10.6 | Component-based AT-XT recipe: droid engineer (motive system x2, brain, sensor), architect (generator turbine, heavy weapon mount stabilizer), shipwright (fusion reactor mk1, medium blaster x2) + steel/iron | [~] (dsrc commit on same branch; needs TemplateCompiler + client shared IFF + in-game craft test) |

**Notes**

- Root cause (marker): client shows the ground reticle for an *overridden* default attack only if that command's `targetType == location` (`CreatureObject::getPrimaryActionWantsGroundReticule`). The AT-XT command was `required` (earlier attempts used `optional` + `validWeapon=GROUND_TARGETTING`, which is checked against the driver's *held* weapon, and none is equipped while driving).
- Root cause (no fire without auto-aim): `required` makes the server drop the command (`CEC_TargetType`) when no target id is sent, and the client needs a mob under the cursor with auto-aim off.
- Unverified suspicion: with auto-aim off the client may pick the AT-XT itself as the first object under the cursor (`findAllTargettableObjects`). If mob targeting still fails after P10.4, check that in client-tools before touching the server again.
- Files needed on client after DataTableTool: `combat_data.iff`, `command_table.iff` (shared tables; see WORKFLOW.md staging section). Full client restart.
- Revert: restore the three edited rows and Java method from `dsrc` master (`40f8dd73a`).

### P11 — Space wingmen: tiered droid programs that spawn escort fighters

**Goal:** A pilot learns wingman **droid programs** (same mechanism as the reactor/weapon/shield programs) at each droid-interface skill tier of the **Freelancer / Alliance / Imperial** tracks. Running a program spawns **3 fighters** of matching strength that follow and guard the pilot's ship.

**Verdict:** Feasible with **Java + datatables only, no C++.** Follows the existing droid-program path and the bomber-strike player-commanded-squad pattern.

**Wingmen last until any of:** all 3 destroyed / program re-sent (replaces the current set, no stacking) / pilot leaves space, hyperspaces or zones / pilot's ship is destroyed or pilot logs out.

**How it maps onto existing code (all under `~/repos/swg-main/dsrc/sku.0/`)**

| Piece | Existing mechanism | Wingmen work |
|-------|--------------------|--------------|
| Learning | `sys.shared/compiled/game/datatables/skill/skills.tab` `COMMANDS` column on `pilot_neutral_droid_01..04` (Freelancer), `pilot_rebel_navy_droid_01..04` (Alliance), `pilot_imperial_navy_droid_01..04` (Imperial). `space_combat.getDroidCommands` lists any granted command containing `droidcommand`; the player burns it onto a memory chip (`script/space/crafting/droid_memory_module.java`). | Add one wingmen program per tier to those 12 boxes (4 tiers x 3 tracks) |
| Program definition | `sys.server/compiled/game/datatables/space_combat/droid_commands.tab` (row per program; `strMessageHandlerOnPlayer` = handler on the player, like `zoneToKessel`). Memory cost in `sys.shared/compiled/game/datatables/space_command/droid_program_size.tab`. | New rows: handler `callWingmen`, `fltBaseDelay` as cooldown; sizes in the existing 5/10/20/25 scale |
| Execution | client `/droid <name>` -> `combat_ship_player.droid()` -> `space_combat.performDroidCommands` -> `doDroidPreCheck` (interface installed + enabled, droid present, program on datapad, cooldown) -> handler | New handler `callWingmen` in `script/space/combat/combat_ship_player.java` |
| Spawn | `space_create.createSquadHyperspace` + `squads.tab` rows (`squad_plyr_cmd_*`); tier-numbered mobiles `escort_tie_*_tier1..5` (Imperial) and `reb_awing_tier1..5` etc. (Alliance) already exist | New `squad_plyr_wingmen_<track>_<tier>` rows, 3 ships each, member script like `space.command.player_cmd_tie_bomber_escort` |
| Kill credit | `space_combat.registerDamageDoneToShip` credits AI ships that carry a `commanderPlayer` objvar to that player | Set `commanderPlayer` on each wingman |
| Cleanup | `OnLogout` -> `space_combat.strikeBomberCleanup`; member script `OnDestroy` notifies commander | Add wingmen cleanup to the same hooks |

| ID | Sub-target | Status |
|----|------------|--------|
| P11.1 | Feasibility check against dsrc/src | [x] |
| P11.2 | Programs: rows in `droid_commands.tab` + `droid_program_size.tab` (4 tiers, per-track names or one shared name per tier) + `COMMANDS` grants in `skills.tab` (12 boxes) | [x] |
| P11.3 | Strings in `space/droid_commands` (`_commandname`, `_chipname`, `_description`, spam text) | [~] server `.stf` done; **client** copy still needed |
| P11.4 | Squad rows + fighter mobiles: 3 ships per tier per track; **Freelancer has no ready `neutral` fighter set** (see risks) | [x] |
| P11.5 | `callWingmen` handler + `space_combat` spawn helper (spawn behind pilot, tag `commanderPlayer`, store squad id on the pilot) | [x] |
| P11.6 | Behaviour: `ship_ai.squadFollow` the player's ship; attack pilot's target (`getLookAtTarget` + `squadSetPrimaryTarget`); retaliate on `OnShipWasHit` | [x] |
| P11.7 | Lifecycle: despawn on resend, leave-space, hyperspace/zone, ship destroyed, logout, droid interface removed | [~] see notes |
| P11.8 | Kill credit, cooldown, time cap; balance vs. the pilot | [~] 20 s cooldown + `commanderPlayer` tag only |
| P11.9 | Deploy (shared tables go to the client too) + in-game smoke test per track and tier | [ ] |

**Notes / risks**

- **Guard pattern differs for players.** The bomber-strike escorts use `squadSetGuardTarget`, which takes a **squad id**; a player's ship is not in a squad. Use follow + attack-my-target + retaliate instead.
- **Freelancer fighters:** mobiles exist for `imperial` (321 rows) and `rebel` (209) but none with `space_faction = neutral`. Needs new mobile rows with a faction that is hostile to what the pilot fights.
- **Shared tables:** `skills.tab` and `droid_program_size.tab` are under `sys.shared`; after DataTableTool the client needs the new `.iff` copies (see WORKFLOW.md staging section).
- **Droid memory:** program size must fit the droid interface capacity; check how capacity scales per interface tier before fixing the sizes.
- **Assumption to confirm:** re-sending the program replaces the existing wingmen (no stacking).
- Not yet verified: the exact hooks for zoning/hyperspace and ship destruction (`OnHyperspaceToHomeLocation`, `OnSpaceEjectPlayerFromShip`, `OnLogout`, `OnImmediateLogout` exist in `combat_ship_player.java`).
- Related: P9 (droid command module) touches the same program-chip path; confirm it is fixed before testing.
- Verified natives (earlier pass): `ship_ai.squadFollow` accepts any object as the followed unit (not only AI ships), plus `squadSetAttackOrders`, `squadSetPrimaryTarget`, `space_create.createSquadHyperspace`, formations CLAW/WALL/SPHERE/DELTA/BROAD/X, `OnShipWasHit` on `combat_ship`.
- C++ caveat: `SpaceSquad::setGuardTarget` requires a target squad. Revisit C++ only if follow + explicit targeting proves insufficient.
- Supersedes the first P11 draft (single summon/dismiss command, 1-3 wingmen by interface rating): design is now one program per tier, 3 fighters each.

**Implementation status (2026-09-29) - code complete, compiles, NOT yet deployed or smoke-tested**

- dsrc branch `feature/space-wingmen` (latest `d1b52d3f8`): tables, `script/library/space_wingmen.java`, `script/space/command/player_cmd_wingman.java`, hooks in `combat_ship_player.java` and `combat_ship.java`. All four Java files compile against the dsrc source tree (javac, syntax and symbols only; no in-game run).
- serverdata branch `feature/space-wingmen` (latest `800ccaa7c`): `string/en/space/droid_commands.stf` (droidcommand_wingmenone..four + `_chipname`/`_commandname`/`_description`, spam keys `wingmen_one..four`) and `string/en/cmd_n.stf` + `cmd_d.stf` (skill-window / program display names; without these the raw key `droidcommand_wingmenone` is shown).
- Programs `droidcommand_wingmenone..four` (memory 10/15/20/25). Skill grants on `pilot_neutral_droid_01..04`, `pilot_rebel_navy_droid_01..04`, `pilot_imperial_navy_droid_01..04`.
- Fighters (matched to the hulls each droid tier's starships box unlocks; 3 of the same per call): Freelancer Dunelizard (medium hutt) / Kimogila (heavy hutt) / Ixiyen (medium black sun) / Rihkxyrk (heavy black sun); Alliance Y-wing / Y-wing (long probe) / X-wing / A-wing; Imperial TIE fighter / TIE fighter (improved, closest row, no `tie_in` mobile hull exists) / TIE interceptor / TIE advanced. Pilot AI tier = program tier. Rows `wingman_<track>_tier1..4`, squads `squad_plyr_wingmen_<track>_<tier>`. No XP, no loot, friendly faction, taunts off. Scyk/Kihraxz are not used (Scyk is the novice ship, Kihraxz shares the tier-2 box).
- Behaviour: **60 s arrival countdown** after running the program (messages at call, 30 s, 10 s), then the squad hyperspaces in behind the ship. One pending call at a time; running it again while wingmen are out replaces them only when the new set arrives. Wingmen follow the pilot's ship (leash 16000, follow re-issued when idle and more than 200 m away) and **only engage whatever hits the pilot's ship** (not the look-at target); the engagement ends when the attacker dies, is over 1200 m away, or has not hit the pilot for 20 s, then they re-follow. **Speed:** the server AI drives a ship at `pilottype.nonCombatMaxSpeedPercent` (0.5 on every stock pilot type) of its engine speed while not attacking, which includes following, so stock pilots only reach half speed. Wingmen therefore have their own pilot types `wingman_<track>_tier1..4` in `ship/pilottype.tab` (percent 1) and `ship/ship_debug.tab` (engine_speed = 1.5 x expected player speed 60/65/70/80 -> 90/97.5/105/120). At runtime, speed and acceleration are also raised every 3 s to the pilot ship's (booster max while boosting) x1.5, never lowered. Needs `pilottype`, `ship_debug`, `space_mobile` compiled to .iff on the server. **Combat tuning** (same `pilottype.tab` rows): stock tier 1-4 pilots fire once per 2 s per ship, miss deliberately 20-30%, and break off after 5 shots / 4 s on the tail then evade up to 12 s. Wingman pilots: fire delay 0.5, fire cone 14, miss angle 4/3/3/2, miss chance 0.15/0.12/0.1/0.1, chase max time 20, max shots 20, max on-tail 18, evade max 4. If still weak, next levers are the hull weapon loadouts (damage) and the attack-squad behaviour in `src` (C++, needs a server rebuild).
- Despawn: all 3 dead, resend, `OnLogout`, `OnHyperspaceToHomeLocation`, `OnSpaceEjectPlayerFromShip`, player ship destroyed (`killSpacePlayer`); these also cancel a pending call (`space_wingmen.endWingmen`). Each wingman also self-destructs within about 10 s if its commander or the commander's ship is no longer in the scene (covers zoning/hyperspace to another system). **Not handled:** droid interface removed while wingmen are out.

**Still open (before P11.9 smoke test)**

- Client needs the new `space/droid_commands.stf`, `cmd_n.stf`, `cmd_d.stf` and the new `skills.iff` / `droid_program_size.iff` (shared tables). Chip name and skill-box command list come from these.
- Confirm in game that all three tracks' wingmen spawn friendly (Freelancer uses `mercenary`), that the tier-1 first test (Scyk, too weak) is fixed by the hull matching, and that the 60 s countdown length feels right (`ARRIVAL_DELAY_SECONDS`).
- Droid memory: sizes 10/15/20/25 not yet checked against droid interface capacity.
- Flight commands window lists every droid program twice: the readable name plus a second line from `space/droid_commands:[droid+<program>]`. `droid_commands.stf` now has a `droid+` key for all 70 programs (text = the cmd_n name), so no raw lines remain; the duplicate readable line is engine behaviour. All original string entries were verified byte-identical (no corruption).
- Kill credit relies on the existing `commanderPlayer` objvar path in `space_combat.registerDamageDoneToShip`; verify in game. No wingman time cap yet.
- Deploy order: merge `dsrc` and `serverdata` PRs first, then a parent PR bumping both gitlinks (WORKFLOW 2.2.1).

**Friendly-fire fix (2026-10-01, code complete, NOT merged, NOT tested in game):** dsrc branch `feature/wingmen-friendly-fire` (commit `a79f20566`). Cause: `combat_ship.OnShipWasHit` applied damage and called `ship_ai.unitAddDamageTaken(self, attacker, ...)`, so hitting a wingman put the pilot's ship on its hate list. Fix: at the top of `OnShipWasHit`, a wingman ignores hits from the pilot's ship, group members' ships and sibling wingmen (no damage, never reaches the AI); `space_wingmen` tick also removes the pilot's ship from each wingman's target list every 3 s as a safety net. Files: `combat_ship.java`, `space_wingmen.java`. Deploy: `./utils/build_java_single.sh` on each, restart GameServer. Smoke: shoot a wingman, kill the enemy, confirm they stay friendly; if they still turn, another C++ path is involved (splash/turrets).

**Exit criteria:** Each track's tier 1-4 program spawns 3 matching-strength fighters that follow and engage, and they despawn cleanly in every lifecycle case above.

---

### P12 — Atmospheric flight: fly up into space (+ Mustafar via Nova Orion)

**Goal:** A pilot flying a fighter in the atmosphere of a ground planet who climbs past the planet's `spaceTransitionAltitude` (3000 m above terrain) is launched into that planet's space scene, the same way a starport launch works. Mustafar becomes flyable and exits to `space_nova_orion` (no `space_mustafar` scene exists anywhere in the repo).

**Primary paths (under `~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/`):** `datatables/space/atmospheric_flight_planets.tab`, `script/library/space_utils.java`, `script/library/space_transition.java`, `script/space/combat/combat_ship_player.java`. Java + one datatable only, no C++.

| ID | Sub-target | Status |
|----|------------|--------|
| P12.1 | Investigate: `spaceTransitionAltitude` column and `space_utils.getAtmosphericSpaceTransitionAltitude()` already existed, nothing called them | [x] |
| P12.2 | New optional `launchPoint` column in `atmospheric_flight_planets.tab` (a `region` key of `launch_locations.tab`); `space_utils.getAtmosphericLaunchRow(planet)` resolves it, else first `launch_locations` row with matching `groundScene` | [x] (code) |
| P12.3 | Mustafar row: `allowAtmosphericFlight=1`, altitude 3000, `launchPoint=nova_orion_station` | [x] (code) |
| P12.4 | Altitude watch: 1 s repeating `handleAtmosAltitudeCheck` on the pilot, warning at 80%, trigger at 100%; started from `completeBoardShipAfterClientRefresh` (wrapper over `...Impl`) and the POB branch of `boardShipAsPilotOnGround`; generation counter drops stale loops; tolerates 5 missed checks during the client world refresh | [x] (code) |
| P12.5 | Exit: `space_transition.exitAtmosphereToSpace` validates owner, control device, target zone population, then `restoreShipToControlDevice` + `launch(...)` with gunners as passengers; on pack failure the pilot is re-seated and the check is blocked for 30 s | [x] (code) |
| P12.6 | Merge dsrc PR, bump `swg-main` dsrc pin, build Java, DataTableTool for `atmospheric_flight_planets.tab`, copy `.iff` everywhere, restart | [ ] |
| P12.7 | In-game smoke: climb on Tatooine/Naboo/Corellia/Rori/Talus -> warning at 2400 m, space at 3000 m; gunner comes along; flying down again after landing; Mustafar -> Nova Orion; owner-only; pack-failure recovery | [ ] |
| P12.8 | Interior (POB) ships: currently only a message ("cannot leave the atmosphere yet"). Packing a POB on the ground has a known portal crash, so left out of v1 | [ ] deferred |

**Implementation status (2026-10-01) - code complete, compiles with javac, NOT deployed or tested**

- dsrc branch `feature/atmos-exit-to-space` (latest `bb8e1c5ed`): the four files above. The previous session's local version was never pushed and was rebuilt from the summary and the code.
- Arrival in space reuses the existing launch path (`setLaunchInfo` -> `warpPlayer` -> `handlePotentialSceneChange` / `unpackShipForPlayer`); the ground location stored for the return trip is the point under the ship when it left.
- Deploy: `./utils/build_java_single.sh` for `space_utils.java`, `space_transition.java`, `combat_ship_player.java`; then `cd ~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/datatables/space/ && ~/repos/swg-main/build/bin/DataTableTool -i atmospheric_flight_planets.tab`, take `SRC` from the SUCCESS line and `find ~/repos/swg-main -name 'atmospheric_flight_planets.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;` (WORKFLOW 6.3). Server-only table, no client copy. Restart GameServer.
- Unverified: whether a ship at 3000 m is still piloted correctly by the existing flight code (no altitude cap was found, but not tested); whether Mustafar's existing ground content copes with ships (Call Ship, landing); the player's arrival start index for gunners.
- Revert: restore the table and the three Java files from dsrc `master`; nothing else depends on them.

**Follow-up (2026-10-04) - dsrc `feature/atmos-exit-watch-and-station-fix`, code only, NOT compiled/tested**

- Server log error `JavaLibrary::getNamedObject: no such object named 'questManager'` from `space_combat.getClosestSpaceStation` <- `space_transition.unpackShipForPlayer` <- `ship_control_device.OnObjectMenuSelect` (Call Ship on a ground planet). Cause: `liveSpaceServer=1` in `exe/linux/localOptions.cfg` removes the try/catch, and the quest manager exists only in space scenes; a stale `strLaunchPointName` script var made the ground call run. Fixed: scene check + always catch + null-check + clear stale var.
- Fly-up not triggering, likely cause: the altitude watch was started only from `completeBoardShipAfterClientRefresh` and the POB branch of `boardShipAsPilotOnGround`, not from Call Ship / `unpackShipForPlayer` seats or relogin. Now started from those too. Throttled `atmosAlt:` log line (every 10 s, `LOG space_transition`) shows altitude vs limit.
- Still to verify in game: that the `atmosAlt:` line appears while flying; if altitude never reaches 3000 m, check for a client-side height cap (client-tools).
- **P12.9 Ship Travel (dsrc `feature/atmos-ship-travel-and-park`, compiles with javac 17, untested in game):** new radial entry "Travel Locations" (`SERVER_MENU10`) on the piloting player's own menu next to Exit Ship (`combat_ship_player.java`). It opens the client instant-travel starport window; `player_travel.OnPurchaseTicketInstantTravel` routes it to `space_transition.completeAtmosShipTravel`, which moves the ship (not just the player) to the chosen starport, 25-40 m from the travel point at terrain+5 m. Same planet only, free, no ticket. Fighters re-seat through the existing world-refresh path; POB skips the refresh. Unverified: whether the pilot's `purchaseTicket` command is allowed while piloting (command_table locomotion/state), and whether the travel list shows the right starports for the departure point name.
- **P12.9b (revised):** the main entry is now on the SHIP's own radial (standing within 32 m, owner only): `combat_ship.java` `SERVER_MENU4` \"Travel Locations\". Works for a player beside the ship (ship hovers at the starport and the player is placed 6 m from it), a walking POB passenger, or a seated pilot (also on the pilot's self radial, `SERVER_MENU10`). `terminal_travel_instant` clears a stale marker.
- **P12.9c (open bug):** Travel entry reported NOT visible on the ground ship's radial. `SERVER_MENU4` is a valid slot (radial_menu.tab) and the label string `tcg:travel_locations` is already used by ITV terminals, so cause unknown. dsrc `feature/atmos-ship-travel-and-park` now logs `shipRadial: <reason>` (LOG `space_transition`) on every early return and `menuBuilt (Travel added)` when it is added. Next step: hover the ship, grep the log for `shipRadial:`.
- **P12.9d Ship Travel now uses the real starship terminal window (dsrc `feature/atmos-ship-travel-and-park`, commit `a872b90b1`, compiles with javac 17, untested in game):** the earlier instant-travel window (P12.9) and the paid starship ticket window were the wrong UI. The starship terminal flow is client-driven (`/ui action shipChoose` -> ship view -> Travel button -> `launchIntoSpace` -> `terminal_space.OnAboutToLaunchIntoSpace`) and is free. The ship's "Travel Locations" radial (`combat_ship.java` `SERVER_MENU4`) now: requires the owner beside the ship (not aboard) and a starship terminal (`GOT_terminal_space`) within 14 m; stores the ship in its datapad control device (`storeShipInControlDeviceSafe`; POB packs after 6 s); then `messageTo` -> `player_travel.msgAtmosOpenShipChoose` -> `sendConsoleCommand("/ui action shipChoose")` after 2 s (8 s POB). Fare, ticket hooks, `completeAtmosShipTravel` and the pilot-radial `SERVER_MENU10` entry were removed. Travel itself is vanilla terminal behaviour: the player is moved to the chosen starport and the ship stays in the datapad (no ship hovering at the destination). When no real starship terminal is within 14 m, a temporary one is spawned buried 4 m below the player, so it is invisible and unclickable; the client only needs it within 16 m (`space/terminal/terminal_space_temp.java`, template `terminal_space.iff` with the script swapped; owner-only, starport travel only, self-destroys after 180 s or 10 s after a launch, expiry survives restarts), so the window works anywhere (dsrc commits `5d2dd5456`, `ab84dc747`, `e195f2e44`). The temp terminal carries `travel.point_name` (avoids the server's "not registered with the planet" warning), burial is NaN-safe, and the window now opens only after polling confirms the ship is inside its control device (max 15 s). Final (dsrc `5e2669ffc`, accepted by owner): the invisible-appearance attempt did not work in game, so the temp terminal is back to normal size/appearance, spawned 2 m in front of the player, and despawns after 120 s or 10 s after a launch. Earlier update (dsrc `4e5389b3a`): the temp terminal is no longer buried; it is made invisible with `setObjectAppearance(object/tangible/theme_park/shared_invisible_object.iff)` + scale 0.05, and it stores the ship itself when a destination is chosen (`OnAboutToLaunchIntoSpace`; POB ships wait for the delayed pack via `msgAtmosTempTerminalLaunch`, max 15 s) so a ship can never be left out on the old planet. Known: the client's ship chooser only lists ships already stored in the datapad, so clicking the terminal before the ship is stored shows an empty list. Unverified in game: that the client accepts the server-sent `shipChoose` action, and the ship list shows the stored ship.
- **P12.10 Park on exit:** `exitBesideShipOnGround` now calls `space_transition.parkShipHover` -> hull hovers at terrain+5 m (`GROUND_SHIP_ABOVE_PLAYER_Y`) after Exit Ship / Leave Station. Ship is not marked landed (landed sinks meshes). Pitch/roll are not levelled.
- Also: `ShipComponentDataManager ... hutt_heavy_s02_chassis_token.iff is not a component` warnings are a separate data issue (chassis token listed in a component table), not related to this fix.

**Exit criteria:** P12.6-P12.7 verified in game; P12.8 done or consciously deferred.

---
- **P12.11 Space mouse flight: zero center deadzone (client-tools `feature/space-mouse-zero-deadzone`, not built or tested in game):** the ship mouse (virtual joystick) in `PlayerShipController.cpp` forced a center deadzone of at least 17.5% of the half reticle radius (about 60 px at the default 700 px space reticle) plus a fixed 4 px `deadZone`. The Options menu could not change it: the space reticle size is set by an optional `sliderDeadZoneSpace` slider that the options UI does not define (so it stays at the 700 default), and the ground slider only changes the ground reticle. Now the center deadzone defaults to 0; the reticle size only sets how far the cursor must travel for full deflection. Optional overrides in `[ClientGame/PlayerShipController]` of the client config: `deadZone` (pixels) and `deadZoneRatio` (fraction of the reticle half-size). Needs a `SwgClient` rebuild and a new `SwgClient_r.exe` (client-tools WORKFLOW §3). Open: a real Options slider for the ship mouse deadzone needs a UI layout change; not done.
- **P12.12 POB ship flies erratically in atmosphere (client-tools `feature/atmos-pob-ignore-interior-objects`, commit `d1ae53302`, NOT built or tested in game):** items placed inside a POB ship acted as obstacles. Cause: the atmosphere obstacle probe in `src/engine/client/library/clientGame/src/shared/collision/CollisionCallbacks.cpp` (added in client-tools `6b2b87dad`) calls `ClientWorld::collide` from the world cell. That queries the tangible sphere trees by world position only and never looks at the parent cell, and only the ship itself was passed as `excludeObject`, so furniture, terminals, droids and crew in the ship's own cells hit the probe and every hit ran `respondToCollision` (bounce). Fix: pass an exclude function (`isInsideProbeShip`) that skips anything whose attachment chain or parent-cell owner chain reaches the piloted ship. Space is unaffected (the probe is `!Game::isSpace()` only) and the GOT-matrix path is per cell, so it never saw ship interiors. Smoke test: fly a POB ship with furniture and a terminal inside in atmosphere (no shaking or drifting); fly into a building or tree (still bounces); terrain bounce unchanged. Revert: drop the `isInsideProbeShip` argument and the `ms_probeShip` assignments. Client rebuild required (full `SwgClient` Build is enough).
- **P12.13 Level ships placed on the ground (dsrc `feature/atmos-ship-level-on-ground`, commit `7aad35acf`, compiles with javac, NOT deployed or tested in game):** Call Ship and Exit Ship put the hull at terrain + `GROUND_SHIP_ABOVE_PLAYER_Y` with `setLocation`, which has no rotation, so the hull kept the pitch and roll of wherever it was last (banked / nose-up on reappearing). New `space_transition.levelShipKeepYaw(ship)` reads the heading with `getYaw` (forward vector, valid while pitched/rolled), sets the identity quaternion, then `setYaw` back, so yaw is kept and pitch/roll are zero. It is called from `raiseShipAbovePlayer` (all board/exit/call paths and `parkShipHover`) before the move, and from `snapShipToGroundAndMarkLanded`. Java only, file `dsrc/sku.0/sys.server/compiled/game/script/library/space_transition.java`. Smoke test: bank/pitch a fighter and a POB ship, Exit Ship (hull hovers level, same heading); store, then Call Ship (hull appears level, 10 m up). Unverified: a ship exiting while nose near-vertical (heading from the forward vector is arbitrary then). Revert: remove the two `levelShipKeepYaw` calls.

### P15 — Mounted combat (ranged attacks while riding a creature mount)

**Goal:** A rider on a creature mount can use basic ranged attacks (pistol, rifle, light rifle, generic ranged shot). Melee, special attacks and vehicles unchanged until this is proven in game.

**Primary paths:** `~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/command/command_table.tab` and `~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/datatables/command/command_table.tab` (data only, no Java, no C++).

| ID | Sub-target | Status |
|----|------------|--------|
| P15.1 | Root cause: the four ranged rows had `L:ridingCreature`=0 and `S:ridingMount`=0, so the command queue refuses them while mounted. Server C++ combat code and `systems/combat/combat_player.java` already support mounted riders (mount speed on enter/leave combat), so no code gate found. | [x] |
| P15.2 | Set `L:ridingCreature` (col 27) and `S:ridingMount` (col 60) to 1 for `rangedShot`, `rangedShotpistol`, `rangedShotrifle`, `rangedShotlightRifle` in both `.tab` copies. dsrc `feature/mounted-ranged-combat` | [~] data only |
| P15.3 | Merge dsrc PR, bump `swg-main` dsrc pin, rebuild BOTH `command_table.tab` with DataTableTool, deploy server IFF to server copies and shared IFF to client (see notes), restart GameServer + client | [ ] |
| P15.4 | In-game smoke: mounted rider can fire a pistol/rifle/light rifle; dismount still works; unmounted combat unchanged; check if galloping should slow or block shooting | [ ] |
| P15.5 | Optional follow-ups: allow melee / special attacks while mounted; vehicles (`L:drivingVehicle`); accuracy penalty while galloping via existing `library/combat.java` `cachedIsGalloping` (defined, currently unused) | [ ] |

**Notes**

- The server and shared `command_table.tab` differ in about 560 lines (server-only hooks such as `cppHook` `setPosture` on kneel/prone/stand). Do NOT use the generic WORKFLOW command_table step that copies the shared `.iff` over every copy: it would drop the server-only hooks. Build both, put the server build on server copies and the shared build on the client.
- Client needs the rebuilt shared `command_table.iff` at `datatables/command/command_table.iff` (client may also check the table); full client restart.
- Revert: restore both `.tab` files from dsrc `master`, rebuild, redeploy, restart.

**Investigation status (2026-10-14) - mounted ranged fire still reported NOT working after the table edit; cause not yet found, no code changed**

- Reported: tables rebuilt and the shared `command_table.iff` copied to the client; mounted ranged attack still does not work. In-game symptom not yet recorded (could not test).
- Verified by reading code/data (dsrc master `c73811d9`, src master `4e59853`, client-tools `d42d689`): the four rows have `L:ridingCreature`=1 (0-based col 26) and `S:ridingMount`=1 (col 59) in both `command_table.tab` copies; no duplicate rows; `command_table_ground.tab` (loaded after) does not override them; a rider's posture `RidingCreature` maps to locomotion `RidingCreature` (`movement_human`); the client sends `rangedShot` + weapon type (e.g. `rangedShotpistol`), matching the edited rows.
- Verified no gate: server `CreatureObject::doWarmupChecks` only checks locomotion/state/ability/target type; Java `combat_base.doCombatPreCheck` has no mount check (only `doHealingPreCheck` refuses galloping/vehicle riders); client `ClientCommandChecks` mirrors the same table checks.
- Open suspects (unverified): (1) client `getTargetUnderCursor()` picking the rider's own mount with auto-aim off (same suspicion as P10); (2) `canSee(attacker, target)` from a rider that is removed from the CollisionWorld; (3) another blocking state at fire time (`alert`, `swimming`, `stunned`, ...).
- Next test (no log needed): mount, target a hostile, type `/rangedShotpistol` (or matching weapon) with auto-aim ON and OFF. Chat message = server refused it (wording gives the reason); total silence = client dropped it; animation but no damage = Java/LOS/target validation. If inconclusive, add a temporary chat diagnostic in `combat_actions.java` `rangedShot` on a feature branch.
- Note: the server `command_table.iff` and the shared one differ (server-only hooks); deploy each to its own side (see Notes above).

**Implementation status (2026-10-16) - code complete, NOT built, NOT deployed, NOT tested in game**

- Root cause of the follow-on breakage (dismount dead, heavy weapons dead, "normal attack silent"): src master's `CreatureObject::doesLocomotionInvalidateCommand` REPLACED the locomotion with `RidingCreature` for every command while `RidingMount` is set. Any command without `L:ridingCreature=1` then fails silently (client `TC_failInvalidLocomotion` is an empty break). Table rows were patched one family at a time (ranged, then dismount + heavy fire) instead of fixing the rule.
- Fix: both the server check and the client check now run the ORIGINAL locomotion rule first, and only when it refuses the command AND the rider is mounted AND the command row has `L:ridingCreature=1` is the command accepted (union, not replacement). Commands that worked mounted before keep working.
- Branches (same name in each repo): src `feature/mounted-locomotion-union` (`cb3ff614`, `engine/server/library/serverGame/src/shared/object/CreatureObject.cpp`); client-tools `feature/mounted-locomotion-union` (`f1d8907f`, `src/engine/client/library/clientGame/src/shared/command/ClientCommandChecks.cpp`). No dsrc change: master already has the dismount / heavy-weapon table rows.
- Supersedes: client-tools `feature/mounted-attack-locomotion-fix` (forced locomotion, never merged: do NOT build the client from it) and the `movement_human.tab` branch dsrc `feature/mounted-riding-locomotion-table` (not needed, do not merge).
- The turret-guard half of src `feature/turret-native-guard-and-mount-loco-union` is NOT part of this work (turret program is a separate project); its mount hunk is identical to the src branch above.
- Not touched, still open: riders are removed from the CollisionWorld while mounted (LOS suspect if damage still fails after commands fire); src `fix-mount-posture-dismount` behaviour for kneeling/prone riders is unverified.

| ID | Sub-target | Status |
|----|------------|--------|
| P15.6 | Merge src + client-tools PRs, rebuild `serverGame` + `SwgGameServer` and `SwgClient`, deploy, restart GameServer + full client restart | [ ] |
| P15.7 | In-game smoke: mounted - pistol/rifle mouse attack fires standing and moving; heavy weapon fires; radial Dismount works; non-riding-flag commands (e.g. stand, emotes, other abilities) behave as before the forced-locomotion change | [ ] |

| P15.8 | **Creature mount radial only teleports the rider into the mount, no riding (2026-10-16 report); vehicles / droid vehicles mount fine.** Prime suspect: a `movement_human.iff` compiled earlier from the UNMERGED dsrc branch `feature/mounted-riding-locomotion-table` is still deployed on the server (every copy under `~/repos/swg-main`) and on the client (`datatables/movement/movement_human.iff`). That branch changes only the `RidingCreature` row (slow/fast filled in); vehicles use the untouched `DrivingVehicle` row, which fits. src `89a02ce2` describes the same symptom after that table change. dsrc `master` has the stock row, so compiled `.iff` and `.tab` have diverged. Fix = rebuild `movement_human.iff` from dsrc master and restore it to ALL copies incl. the client (commands in chat; WORKFLOW 6.3 datatable pattern). The union rule (P15.6) makes the mapped row unnecessary | [ ] unverified |
| P15.9 | **FIXED + VERIFIED IN GAME 2026-10-17 (data fix, pending merge/deploy): radial_menu.tab row offset.** Retest with CLIENTDIAG after compiling the fixed table: mount holds (ridingState=1, container=mount, mount_combat=true), normal radial Dismount sends exactly one `dismount` with ridingMount=1. Merge dsrc `feature/fix-radial-menu-god-teleport-row` (`0f57b5803`) and `feature/remove-mountdiag` (`d5cd346a4`, removes MOUNTDIAG from taming/base_player/base_class which had been merged to master via PRs #213/#214). Compiled `radial_menu.iff` must also be committed to serverdata and shipped to EVERY client (client-side data). Known leftovers: harmless duplicate `mount` enqueue (radial sends it directly and via the table row) gives the chat line "You cannot Mount while Riding a Mount."; why the older exe mounted is still unexplained. Original report: **Creature mount radial only teleported the rider to the mount centre after the P15.8 revert (2026-10-17 report); no server log.** Static review (dsrc master `b2765ff27`, src master `7ded134f`, client-tools main `fb96a4a`): the `mount` command row, `pet.OnObjectMenuSelect` -> `queueCommand(mount)` -> `taming.mount` -> `mountCreature` path is unchanged; src/client changes since 2026-10-02 do not touch mount start. Client source never sends `CM_setLocomotion`. Not a verified cause: since src `f17ab18f` a rider whose posture is not Upright is no longer auto-dismounted, so a posture glitch would now look like "teleported, not riding" (client only plays the riding animation when posture is Upright, `CreatureController::determineAnimationStatePath`). Diagnostic: dsrc `feature/diag-mount-radial` (`ce4bb033f`, `taming.java` only) prints `MOUNTDIAG:` chat lines + `LOG("mount")` at entry, at every silent early return, after `mountCreature` and after `setMountedMovementRate` (posture / riding state / mount id). Rebuild: `./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/player/skill/taming.java`. Remove the diagnostic once the cause is known | [ ] diagnostic run 1: server mounts OK (posture 0, ridingState 1, mountId set, no EXIT line); droid mount works, creature mount teleports. Deployed `movement_human.iff` md5 `693df102...` equals the stock file in serverdata (2020), so the table is ruled out. Run 2 (later-check, varactyl): ~1 s after a successful `mountCreature` the rider is already dismounted server-side (ridingState 0, mountId null, containedBy null, mount state 0, mount_combat script gone, dist 0.0), silently, so the bug is a server-side detach right after mount, not a client rendering issue. Next: dsrc `feature/diag-mount-radial` `a2906dd2a`+ stack-trace trap in `base_class.dismountCreature` to catch Java callers; if nothing is reported the detach is C++ (`detachRider`/`detachAllRiders`/`emergencyDismountForRider`). **Run 3 (2026-10-17, stack-trace trap):** the dismount is NOT a stray script and NOT C++: `dismountCreature` is called from `pet_lib.doDismountNow` <- `taming.dismount:298`, i.e. the server received the client `dismount` command right after the successful mount. The only client senders are `CuiRadialMenuManager` (radial mount/dismount toggle, ~line 2305, and `performDefaultDoubleClickAction` ~line 2819, which the Oct-16 left-click gate now blocks for mounts). The user reports an OLDER client exe mounts correctly against the same server, so the regression is in the client exe. Candidates in client-tools since the older build: #36 `ac4a4a58d` auto-aim LOS, #37 `1d321d206` left-click gate, #38 `f1d8907fb` locomotion union in `ClientCommandChecks::doesLocomotionInvalidateCommand` (now lets `dismount` pass client-side while mounted). Not verified which commit; need the older exe's build commit/date, or a client diagnostic at the two `hash_dismount` enqueue sites. **Checked 2026-10-17:** client-tools has NO commits dated Oct 17; newest are Oct 16 (#36 11:56, #37 13:43, unmerged forced-locomotion `733689483` 13:58, #38 20:22 +0200). Client diag pushed: client-tools `feature/diag-client-dismount` (`50dab2bae`, `ClientCommandQueue::enqueueCommand` prints `CLIENTDIAG: enqueue mount/dismount target ridingMount t` in chat; temp, do not merge). Build `SwgClient` Release\|Win32, test one mount. **MECHANISM FOUND, NOT YET VERIFIED AS THE REGRESSION (CLIENTDIAG run, 2026-10-17):** client enqueued `mount` and `dismount` (target = mount id) in the same tick with ridingMount=0. Cause is data: `datatables/player/radial_menu.tab` had no `GOD_TELEPORT` row at index 109 (dsrc `b462125d1`, 2020, appended it at the END, row 321), so every row from 109 on is one lower than the menu-type number in `menu_info_types.java` / client `CuiMenuInfoTypes.h` (both: SERVER_PET_MOUNT=288, DISMOUNT=289). After the client sends `mount` it calls `executeCommandForMenu(288)`, which read row 288 = `SERVER_PET_DISMOUNT` (command `dismount`, useRadialTarget=1) and queued a dismount. CAVEAT: the compiled `radial_menu.iff` (serverdata) is byte-identical to the stock 2020 file (md5 `314b86ac...`, 321 rows), so the offset is years old and cannot by itself explain why an older exe mounts fine. Hypothesis for what changed: dsrc `575b1157c` (2026-10-16 14:43) set `L:ridingCreature=1` on the `dismount` row, so the stray post-mount dismount (rider locomotion RidingCreature) is now accepted instead of refused. Unverified; older exe behaviour unexplained. Test: apply the table fix and re-run CLIENTDIAG; if `enqueue dismount` disappears the mechanism is confirmed. Fix: dsrc `feature/fix-radial-menu-god-teleport-row` (`0f57b5803`) moves the row to 109; verified all 322 rows match java indices. Needs `DataTableTool -i radial_menu.tab`, copy radial_menu.iff to every copy + the client folder, restart GameServer + client. NOTE dsrc master already contains the MOUNTDIAG code (PR #214 merged): remove it after verification; also drop client-tools `feature/diag-client-dismount` |

If P15.8 does not fix it: record the server log (`mounts-bug` / `mount` channels, `LOG` lines are not DEBUG_LOG) and whether the client shows the rider on the saddle for a moment before snapping off; next suspects are the Java `pet_lib.setMountedMovementRate` (commit `3af7935b`) and anything detaching the rider after `mountCreature` returns true.

**Mounted combat visuals (2026-10-17) - code complete, NOT built, NOT deployed, NOT tested in game**

| ID | Sub-target | Status |
|----|------------|--------|
| P15.10 | **Mounted heavy weapons: impact effects fixed at the mount-up spot (damage works).** Cause (static reading): `SwgCuiHud.cpp` skipped the whole ground-reticle update while `States::RidingMount` was set, so `ReticleManager` last point/cell/valid were never refreshed. The local attack playback (`GroundCombatActionManager.cpp` ~1297) used the stale point from when the player last stood on foot; no location params were sent (reticle never valid), so the server fell back to the target position. Fix: client-tools `feature/mounted-heavy-weapon-reticle` (`4a7aff52c`): reticle updates while mounted like on foot; `hitReticle()` excludes the rider's own mount from the ray; rider not turned to the reticle while mounted. Needs `SwgClient` rebuild + new exe. Behaviour change: mounted heavy shots now send location params like on-foot shots | [ ] |
| P15.11 | **Pistol/ranged projectiles vanish behind the mount model (hypothesis: depth occlusion by the mount mesh, muzzle inside mount volume).** Mitigation: client-tools same branch, separate commit `a2a62bb4f` (`FireProjectileActionTemplate.cpp`): when the muzzle->target path hits the mount appearance, start the projectile at the exit point (cast target->muzzle, skip at most half the path). Revert that commit alone if it looks wrong | [ ] unverified guess |
| P15.12 | **Double mount message "You cannot Mount while Riding a Mount."** Cause: client sends `mount` directly for `SERVER_PET_MOUNT` (`CuiRadialMenuManager.cpp` ~2309) and then `executeCommandForMenu` runs the `mount` command from the `radial_menu.tab` row. Fix already on dsrc `feature/radial-pet-mount-no-duplicate` (`75d626441`, empties that row's command; fast-forwards onto dsrc master, 4 columns kept). Needs merge, `DataTableTool -i radial_menu.tab`, `radial_menu.iff` to every server copy and every client, restart | [ ] |
| P15.13 | Heavy weapons show no projectile even on foot. NOT investigated; probably data / playback script, not mounted-specific | [ ] |
| P15.14 | **Vehicle riders could not fire at all (no bolt, no impact, no playback) while creature mounts worked.** Cause: client config `disableVehicleRiderCombatAnimationState` defaulted to true, so `CreatureController::getAnimationTarget` told vehicle riders they were never in the combat state; `GroundCombatActionManager` local attack waits for `areVisualsInCombat()` before submitting playback, so it never got there. Fix: client-tools `feature/vehicle-rider-combat-animation-state` (`0a8bf6796`, one line in `ConfigClientGame.cpp`, default now false; the cfg key `[ClientGame] disableVehicleRiderCombatAnimationState=1` restores the old behaviour). **Verified in game 2026-10-17** with the temporary MOUNTPLAYDIAG on creature mount (mountGOT=1024) and vehicle (mountGOT=65537): script accepted and playing, hits land. Heavy weapon on a vehicle not yet re-checked | [x] pending merge |
| P15.15 | **Bolt occlusion mitigation (P15.11) used the hidden creature mesh on hover vehicles.** Hover vehicles hide their own mesh (`CreatureObject::alter` `setShowMesh(false)`); the visible body is the saddle child object (`SaddleManager`). Fix: client-tools `feature/vehicle-mounted-bolt-saddle-appearance` (`108435918`, `FireProjectileActionTemplate.cpp`) tests the saddle appearance for `GOT_vehicle_hover` / `GOT_vehicle_hover_ai`. Not separately verified (bolt visibility on vehicles after P15.14 still to be confirmed by eye) | [~] pending merge |
| P15.16 | **Heavy-weapon impact location on vehicles:** reticle/impact code is identical for vehicles and mounts, and the saddle is excluded from the reticle ray with its mount, so the earlier vehicle impact miss was most likely the P15.14 stall. Re-test with a heavy weapon on a vehicle | [ ] |
| P15.17 | Temporary diagnostic MOUNTPLAYDIAG (client-tools `feature/diag-mounted-playback`, `02414928a`, `ClientCombatPlaybackManager.cpp`): prints one chat line per attack of a mounted player. **Do NOT merge; delete the branch after verification.** Finding: attackerPostureEnd and visualPosture are 0 (Upright) for both mounts and vehicles, so posture-keyed script selection was not the cause | [ ] remove |

Smoke after rebuilding the client: pistol fired in several directions across the mount keeps a visible bolt; mounted heavy weapon (auto-aim on and off) shows the reticle and impacts land on the target; mount shows no "cannot mount" message; mounted dismount and on-foot heavy shot unchanged. Temporary `HEAVYDIAG` branch dsrc `feature/diag-mounted-heavy-weapon` is not needed for this and must not be merged.

**Exit criteria:** P15.3-P15.4 and P15.6-P15.9 verified in game.
### P13 — Taming high-level creatures (Mustafar babies had no Tame option)

**Goal:** Level 70+ NGE creatures (Mustafar) can be tamed and called by a Creature Handler holding the full taming line, without a Pre-CU skill-tree or client change.

**Primary paths (under `~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/script/`):** `library/pet_lib.java` only (Java, no tables, no client files).

| ID | Sub-target | Status |
|----|------------|--------|
| P13.1 | Root cause: the four Creature Handler lines (taming/training/healing/support) plus novice+master grant `tame_level` 70 total; `getChanceToTame` returns 0 when the creature's **table** level (`create.calcCreatureLevel`, not the spawn-overridden level shown in game) is above it, so `ai.java` never adds `PET_TAME`. Calling pets uses the same gate (`canControlPetsOfLevel`). Of 91 non-elite tameable `som_` rows, 19 are <=70 and 72 are >70. Baby spawn itself works. | [x] |
| P13.2 | `pet_lib.getEffectiveTameLevel(level)` caps the level used for taming/calling at `MAX_TAME_LEVEL_CAP` = 70, applied in `getChanceToTame(int,int,int)` and the `canControlPetsOfLevel` sum. dsrc `feature/tame-cap-high-level-creatures` (compiles with javac 21; chance arithmetic checked offline) | [~] code only |
| P13.3 | Merge dsrc PR, bump `swg-main` dsrc pin, build `pet_lib.java`, restart GameServer | [ ] |
| P13.4 | In-game smoke: full-line Creature Handler sees Tame on a >70 non-aggro Mustafar baby; handler with tame_level < 70 does not; sub-70 creatures unchanged; pet can be called | [ ] |

**Notes**

- Behavior: above-70 creatures behave as level 70, so they need the full line (tame_level 70). Non-aggro chance at skill 80 is 23% (level 70+). Aggro creatures at that level show chance 5, below the `ai.java` menu threshold of 15, so aggro >~53 stay untameable (aggro skill 50, +10 wookiee/ithorian, + `tame_bonus` gear/food). Lower that threshold separately if wanted.
- Superseded: dsrc `feature/tame-scale-high-level-creatures` (level compression, built on a wrong 34 cap) must not be merged; delete it.
- Not changed: `pet_control_device.java` transfer check (~line 1939) still compares the raw level; the level shown in game can differ from the table level (spawn override), which is why some creatures displaying 80 are already tameable.
- Deploy: `./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/library/pet_lib.java`, restart GameServer. No client files.
- Revert: restore `pet_lib.java` from dsrc `master`.

**Exit criteria:** P13.3-P13.4 verified in game.

---

### P14 — Looted schematics: "you must have skl_n:[class_...] skill" messages

**Goal:** Looted / quest / generated schematics show and enforce Pre-CU skills, never NGE `class_*` names.

**Primary paths (under `~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/script/`):** `item/loot_schematic/loot_schematic.java`, `item/loot_schematic/loot_schematic_nonlimited.java`, `library/weapons.java`, `gm/cmd.java`. Java only, no tables, no client files.

| ID | Sub-target | Status |
|----|------------|--------|
| P14.1 | Diagnose: current `dsrc` master remaps `class_*` to Pre-CU on init and on use (commit `fbfc89352`, 2026-09-26), and the pre-fix code printed the raw `skill_req`, which matches the reported messages (`class_structures_phase4_novice`, `class_domestics_phase2_02`). None of the 113 `object/tangible/loot/loot_schematic/*.tpf` templates (106 have a `skill_req`) nor the 205 `skill_req` templates overall contain `class_*`. Most likely the server runs a stale compiled `loot_schematic` class (compiled `.class` files are not in git) | [x] (hypothesis, not confirmed on the server) |
| P14.2 | Remove the last hardcoded `class_munitions_phase4_master` (`weapons.createLimitedUseSchematic`, `/GmWeapon limUseSchematic`) | [~] code only |
| P14.3 | Log raw vs remapped `skill_req` on use (LOG channel `loot_schematic`, tag `build=remap-v2`) so the server log shows which build is running | [~] code only |
| P14.4 | Merge dsrc PR, bump `swg-main` dsrc pin, rebuild `loot_schematic.java`, `loot_schematic_nonlimited.java`, `weapons.java`, `cmd.java` (and `armor.java`, `vehicle.java` if not rebuilt since 2026-09-26), restart GameServer | [ ] |
| P14.5 | In-game smoke: use a looted schematic that used to show `class_structures_phase4_novice` / `class_domestics_phase2_02`; the message (if any) must now name a `crafting_*` skill; grep the server log for `build=remap-v2` | [ ] |

**Implementation status (2026-10-14) - code complete, compiles (javac 21), NOT deployed or tested**

- dsrc branch `feature/loot-schematic-skill-req-hardening` (`21815ed10`, based on dsrc master `e4d3491e7`). Compare: https://github.com/daquorm89/dsrc/compare/master...feature/loot-schematic-skill-req-hardening
- Deploy: `./utils/build_java_single.sh` on `loot_schematic.java` first (the nonlimited script calls its remap), then the other three; restart GameServer.
- If `build=remap-v2` never appears in the log after the rebuild but the old message still does, the class is not being loaded from the rebuilt tree; check the compiled `.class` timestamp under `~/repos/swg-main/data/sku.0/sys.server/compiled/game/script/item/loot_schematic/`.
- Not touched (out of scope): other `hasSkill(..., "class_*")` checks (`utils.java`, `pet_master.java`, `xp.java`, imperial crackdown scripts) and `reverse_engineering_tool.SKILL_LIST`.
- Revert: restore the four files from dsrc `master`.

**Exit criteria:** P14.4-P14.5 verified in game.

---

### P16 — Droid commands (incl. Turret Defense) on POB ships: empty Astromech tab

**Goal:** Programs loaded on a droid or flight computer must show up (and run) for the player in a POB ship such as the YT-1300, same as in a starfighter. Needed before the droid turret-defense program (`droidcommand_turretdefense`, POB only) can be tested.

**Symptom (2026-10-17, YT-1300):** programs stay loaded on the droid / flight computer (verified on the device) and the droid is installed in the ship, but the Astromech tab of the commands window is completely empty, vanilla programs included. Starfighters work.

**Cause (static, confirmed in code, not yet in game):** the Astromech tab lists the player's granted commands (`SwgCuiCommandBrowser` uses `player->getCommands()`). The server grants `droid+<program>` with `space_transition.grantDroidCommands`, which is called (1) from `unpackShipForPlayer` only when the ship has NO interior and (2) from `shipoperations_falcon` (the operations seat). The POB pilot seat (`cmdPilotShip`, atmosphere board paths) never granted them.

| ID | Sub-target | Status |
|----|------------|--------|
| P16.1 | Find why the tab is empty on POB ships | [x] |
| P16.2 | `space_transition.grantPobPilotDroidCommands` (logs droid PCD + program count), called after the POB pilot is seated: `combat_ship_player.cmdPilotShip`, `boardShipAsPilotOnGround`, 3 `completeBoardShipAfterClientRefresh` re-seat paths; revoke on Leave Station from the POB pilot seat | [x] (code, compiles) |
| P16.3 | Deploy and verify in game: pilot seat AND operations seat of the YT-1300 | [ ] |
| P16.4 | Verify `/droid turretdefense` actually runs once the tab is populated (`doDroidPreCheck`: interface slot installed and enabled, droid PCD associated, program on the datapad) | [ ] |

**Implementation status (2026-10-17) - code only, compiles with javac, NOT deployed or tested**

- dsrc branch `feature/pob-pilot-droid-commands` (commit `bf79b18c7`): `script/library/space_transition.java`, `script/space/combat/combat_ship_player.java`.
- Smoke test: with a droid/flight computer programmed and installed in the YT-1300, sit in the pilot chair: Astromech tab lists the programs; Leave Station: they disappear; operations seat still grants them. Server log (`LOG space_transition`) prints `grantPobPilotDroidCommands: ship=... droidPcd=... programs=N`; `droidPcd` invalid or `programs=-1/0` means the droid is not associated with the ship (starship terminal) or has no programs, not a grant bug.
- Still unverified: whether `isUsingCorrectComputer` accepts the player's droid for the YT-1300 (`ship_droid_assignments.tab` lists `player_yt1300.iff` as `flight_computer`, so an astromech droid is refused for it, a flight computer is needed).
- Revert: remove the `grantPobPilotDroidCommands` calls and the `revokeDroidCommands` line in `cmdLeaveStation`.

**Update (2026-10-17, after in-game test of the pilot-seat fix):** the tab is NOT empty; only programs loaded on the **ship computer (flight computer)** are missing. Static findings:

- The client Astromech tab = the player's granted `droid+<program>` names (first word before `+` must be a known command, `droid`, group `astromech`) plus table rows with `visibleToClients > 2` (only `droidcommand_turretdefense` today). Source: `SwgCuiCommandBrowser.cpp`.
- Server grants come only from `space_combat.getProgrammedDroidCommands(player)`: containing ship -> `getDroidControlDeviceForShip(ship)` -> `SLOT_DATAPAD` contents with objvar `strDroidCommand`. Same code for droid and flight computer, so a difference means the ship has no associated control device (returns null) when the grant runs.
- `revokeDroidCommands` revokes from the CURRENT ship's device, so grants made earlier (e.g. from an astromech in a starfighter) are never revoked after the device changes. This could explain "vanilla visible, ship-computer ones missing" (stale grants vs. no new grants). Unverified.
- `player_yt1300.iff` = `flight_computer`; `OnTryToEquipDroidControlDeviceInShip` refuses an astromech for it (`need_flight_computer`).
- Needed to confirm: server log line `grantPobPilotDroidCommands: ship=... droidPcd=... programs=N` when sitting in the YT-1300 pilot chair (droidPcd invalid = flight computer not associated; programs=0 = datapad read problem).
- Next if confirmed: make revoke independent of the current device (revoke every `droid+*` command the player holds) and fix association of the flight computer for POB ships.

**Update 2 (2026-10-17):** after sitting in the operations seat the programs are granted and show in the pilot seat too, but running one gives "you cannot cmd_n:[droid] while piloting a ship". Cause: `command_table_space.tab` rows `droid` and `droidcommand_turretdefense` have `S:pilotingPobShip=0` (denied) and only `S:shipOperations=1` (vanilla design: POB droid commands from the operations seat). Fix: dsrc `feature/pob-pilot-droid-command-state` (`0e96d2774`) sets `S:pilotingPobShip=1` on both rows. Needs a command table rebuild on server AND client data. Still open: the pilot seat grant itself (`grantPobPilotDroidCommands` log line) not confirmed.

**Update 3 (2026-10-17):** pilot-seat droid commands confirmed working in game. Turret Defense tuning: dsrc `feature/turret-defense-arc-hull-duration` changes `library/space_turret_defense.java` (compiles, untested): (1) 180 degree arcs: weapon 0 (upper turret) only fires at targets above the hull plane (ship-local y >= 0), weapon 1 (lower) only below, so turrets no longer shoot through the player ship; (2) `fireShipTurretServer` now passes `space_combat.SHIP` instead of component 0 (reactor): the reactor-only hits disabled ships but could not pass damage to the hull; (3) duration 45 -> 120 s (`DURATION_SEC`). Per-turret target choice from look-at target then attackers. Unverified: the arc is a hemisphere about the hull plane, not the real mount hardpoint.

**Update 4 (2026-10-17):** Turret Defense confirmed working well. Balance drawback added on the same dsrc branch (`feature/turret-defense-arc-hull-duration`): activation sets the ship capacitor to 0 ("power rerouted to the AI gunners") and, with `HOLD_CAPACITOR_DRAINED = true`, the 1.5 s tick keeps it at 0 until the program ends (120 s). Compiles, untested. Tuning knobs: `HOLD_CAPACITOR_DRAINED`, `DURATION_SEC`. Not handled: if the player leaves the ship mid-program the hold just stops (normal recharge resumes).

**Update 5 (2026-10-17):** capacitor drawback revised (same dsrc branch): activation drains the capacitor ONCE and limits its maximum to `CAPACITOR_MAX_FRACTION` (0.5) of normal for the program duration, so some charge remains for firing. Original max is stored in ship objvar `turretDef.origCapMax` and restored on expiry, on leaving the ship, or if the player object is gone. Replaces the per-tick hold. Compiles, untested. Restart safety: `combat_ship.OnInitialize` calls `space_turret_defense.restorePower`, so a reduced max left over after a server restart is restored when the ship loads (untested).

**Update 6 (2026-10-17):** in-game: halved max made the capacitor bar look full. Changed (same dsrc branch): maximum is no longer modified; activation empties the capacitor once and a 0.25 s `turretDefenseCapTick` (new handler in `combat_ship_player.java`) clamps current to `CAPACITOR_MAX_FRACTION` (0.5) of the real max until the program ends, so the bar shows the full capacity with only half usable. `restorePower` and the `combat_ship.OnInitialize` hook remain as legacy cleanup for ships left with a halved max by the previous build (start also calls it). Targeting: the pilot's target is now read with `getLookAtTarget(ship)` (player as fallback) and checked with `pvpCanAttack(ship, target)`, so a selected hostile is engaged even if it has not attacked yet. Compiles, untested. Caveat: up to ~0.25 s of recharge can show between clamps.

**Update 7 (2026-10-17):** in-game: turrets attacked anything targeted (blue ships, stations, asteroids) and fired at any distance. Fix on dsrc `feature/turret-defense-hostile-only-range` (`library/space_turret_defense.java`, compiles, untested): new `isValidTurretTarget` requires a real ship (`space_utils.isShip`), not a station (`space_pilot_command.isStation`), not `intInvincible`, not player-controlled, and an enemy by `pvpIsEnemy` (either direction, same check as `working/rdelashmit/ship_faction_debug`); ships already targeting us always count. `pvpCanAttack` was too permissive. Range: each turret now uses its installed weapon's range (`getShipComponentDescriptorWeaponRange(getShipComponentCrc(ship, slot))`, fallback `MAX_RANGE` 500 when unknown) and only fires at targets within `getDistance(ship, target)`; missile, countermeasure, mining and tractor slots are skipped. Unverified: whether range is measured center-to-center the way the game's own weapons measure it, and whether `pvpIsEnemy` flags every red target.

**Update 8 (2026-10-17):** Turret Defense mining lasers. dsrc `feature/turret-defense-mining-lasers` (`library/space_turret_defense.java`, compiles, untested): weapon slots whose component is a mining laser (`getShipComponentDescriptorWeaponIsMining`) now auto-target mining asteroids and chunks (`GOT_ship_mining_asteroid_static` / `_dynamic`) instead of hostile ships: the pilot's selected target if it is one, otherwise the nearest within the weapon range and the turret's 180 degree arc (`pickMiningTarget`). The hit is processed by the existing `space_mining` scripts' `OnShipWasHit`, which also require the pilot to have Episode 3. Tractor beams, missiles and countermeasures are still skipped. The turret tick now runs even with no hostiles so mining lasers fire on their own. Known limitations: attacker list includes any ship merely targeting us (friendly lock can draw fire); unverified that `fireShipTurretServer` on a mining laser slot yields hits the mining scripts accept.

**Update 9 (2026-10-20) - POB droid commands and maneuvers, dsrc `feature/pob-droid-commands-sync-and-maneuvers` (`1976473d3`, `0ded552f6`; compiles with javac 21, NOT deployed or tested in game):**

- Astromech tab empty for POB pilots again. Causes found by static reading: (1) `space_transition.packShip` revokes droid commands for all contained players (launch, store, zone), and `unpackShipForPlayer` re-granted only for ships WITHOUT an interior, so a POB pilot seated by unpack got nothing; (2) player commands are reference-counted (`CreatureObject::grantCommand` +1, script `revokeCommand` -1), the seat paths grant repeatedly and the old revoke only covered the current device's programs, so stale or stacked `droid+*` entries survived; (3) nothing refreshed after equipping a droid/flight computer (`OnTryToEquipDroidControlDeviceInShip`, done at a starport terminal) or after burning a chip while aboard.
- Fix: `space_transition.clearDroidCommands` (revokes every held `droid+*` until gone), `grantDroidCommands` = clear + grant once (idempotent), `revokeDroidCommands` = clear, `refreshDroidCommandsForShip`; `unpackShipForPlayer` grants for POB via `grantPobPilotDroidCommands`; `combat_ship.OnTryToEquipDroidControlDeviceInShip` refreshes after each association; `space/crafting/droid_datapad_handler.OnReceivedItem` refreshes when a program chip is added while aboard. Side effect: also clears skill-granted `droid+*` (only `pilot_spacetest` has one).
- Maneuvers as POB pilot: `command_table_space.tab` had `S:pilotingPobShip=0` on 24 pilot maneuvers (iffscramble, pumpreactor, eweapons/eshields/ethrust, epulse1-3, jstart1-3, bstrike1-3, ptrap1-2, nblast, vrepair(other), inspacerepair/reload/rr, lightEngineScramble, taunt); set to 1. Handlers use `getContainingShip(self)`, no Java change. Not changed: leaveStation, unpilotShip, openWings/closeWings, dock, inspect, waypoint/wp, escapePod, requestSpaceTrainer, kickFromShip.
- **Known limit:** `command_table_space` is loaded only in space scenes (server `ServerCommandTable.cpp`, client `ClientCommandTable.cpp`). On ground scenes (atmospheric flight) `droid`, `iffscramble` etc. do not exist for ANY ship; fixing that needs rows in `command_table_ground.tab` (server + client) and a decision on which space-only programs are allowed in atmosphere. Not done.
- Deploy: `DataTableTool -i command_table_space.tab` in `~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/command/`, copy `.iff` to every copy and to the client `datatables/command/command_table_space.iff`; `./utils/build_java_single.sh` for `space_transition.java`, `combat_ship.java`, `droid_datapad_handler.java`; restart GameServer, full client restart. Smoke (space): launch YT-1300 from a starport with a programmed flight computer, sit in pilot seat, Astromech tab lists programs; `/iffscramble` while targeted; burn a chip while seated and the tab updates.

### P17 — POB ship certifications: required by the ships, granted by nothing

**Goal:** Every player POB ship whose template requires a certification command can actually be flown by a player who earns the matching master pilot skill. Ships with no faction allegiance are granted by all three master pilot skills.

**Finding (2026-10-19, static code audit, not yet in game):** each ship's required cert is `certificationsRequired` in `~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/object/ship/player/shared_player_<ship>.tpf`, and it is checked with `CreatureObject::hasCertificationsForItem` (`hasCommand`). Only YT-1300, Decimator and Nova Courier (YKL-37R) certs were granted (by `pilot_neutral_master`, `pilot_imperial_navy_master`, `pilot_rebel_navy_master` in `~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/skill/skills.tab`, column `COMMANDS`). Five others were required but granted by nothing in dsrc: `cert_starships_yt2400`, `cert_starships_y8_mining_ship`, `cert_starships_gunship_imperial`, `cert_starships_gunship_rebel`, `cert_starships_gunship_neutral`. The Sorosuub Space Yacht template requires no cert, so there is nothing to grant.

**Primary paths:** `dsrc` -> `sku.0/sys.shared/compiled/game/datatables/skill/skills.tab`

| ID | Sub-target | Status |
|----|------------|--------|
| P17.1 | Audit all 9 player POB ships: required cert vs which skill grants it | [x] |
| P17.2 | `skills.tab`: gunship cert to its faction master (rebel / imperial / neutral = Black Sun Transport), `cert_starships_yt2400` + `cert_starships_y8_mining_ship` to all three masters. dsrc branch `feature/pob-ship-certs`, commit `7e99235a4` (code only, not compiled) | [~] |
| P17.3 | Merge dsrc PR, bump `swg-main` dsrc pin, compile `skills.tab` with DataTableTool and copy the `.iff` to every copy (`data/...sys.shared`, `serverdata/...`), restart GameServer + client | [ ] |
| P17.4 | In-game: skills grant commands when the skill is granted, so characters that already hold a master skill likely need revoke + regrant (`/revokeSkill` then `/grantSkill`) to receive the new certs (to verify). Then confirm each of the 8 ships can be boarded and flown | [ ] |
| P17.5 | Decide: Sorosuub Space Yacht stays cert-free, or gets a `certificationsRequired` (shared template, client change) | [ ] |

---

### P18 — Stationed droids: "Set Loose" a datapad droid as an autonomous NPC (stand / wander / guard)

**Goal:** From a called-out droid's radial menu the owner can **Set Loose** the droid: it stops being a follower pet, frees its datapad slot, is persisted in the world where it stands, and runs an owner-chosen mode (**Stand Here**, **Wander**, **Guard**). **Pick Up** returns it to the datapad exactly as it was. Intended use: interactive decoration / guards for houses.

**Scope decisions (user, 2026-10-20/21):** programmable = the owner sets its state (stand, wander, guard first). Later ideas, not built: patrol routes (reuse `pet.patrolPoints`), module-based orders (barker, entertainer, ...). Unanswered questions, defaults taken: pick-up by owner only; guard fights hostile creatures; max 10 loose droids per player; droids in ships/POB blocked. **Revised 2026-10-21 (user):** cap is now **25** per player, droids **are allowed in ships and POB** (`ALLOW_IN_SHIPS = true`), and loose droids are **downable but never killable** (a downed droid always recovers after ~45 s).

**Key finding:** a droid's inventory, datapad (program chips), power level and stored damage live on its **pet control device (PCD)**, not on the droid creature. The PCD is therefore never destroyed: while loose it is **parked in the droid's own inventory** (unused for droid pets) with `ai.pet_control_device` / `ai.pcd_ping_response` detached (`ai.pet_control_device.OnTransferred` destroys the linked droid whenever the PCD moves). The droid is persisted first (`ServerObject::persist` recurses into children), then the PCD is parked, then `ai.pet_ping` + `ai.pet` are detached and `ai.stationed_droid` attached. A failed park rolls the droid back into the datapad.

| ID | Sub-target | Status |
|----|------------|--------|
| P18.1 | Feasibility study (pet lifecycle, PCD contents, persistence, AI hooks) | [x] |
| P18.2 | `library/stationed_droid.java`: gate, per-player registry, setLoose, pickUp, rescuePcd, setMode/applyMode | [~] (written, compiles, untested) |
| P18.3 | `ai/stationed_droid.java`: radial menu, guard scan + defence of owner, return-to-post, incap recovery, PCD rescue on destroy | [~] (written, compiles, untested) |
| P18.4 | `ai/pet.java`: Set Loose entry (`SERVER_MENU8`) in the droid options submenu | [~] (written, compiles, untested) |
| P18.5 | Strings: 15 `stationed_*` keys appended to `serverdata/string/en/pet/pet_menu.stf` (tool: `tools/stf_tool.py`); deploy to client `string/en/pet/pet_menu.stf` too | [~] (written, original 206 entries verified unchanged) |
| P18.6 | Merge dsrc + serverdata PRs, bump swg-main pins, deploy, restart GameServer, full client restart | [ ] |
| P18.7 | In-game smoke tests (below) | [ ] |
| P18.8 | Droids in ships and POB: enabled (`ALLOW_IN_SHIPS = true`, dsrc branch `feature/stationed-droids-tweaks`). Still to verify in game what ship pack/unpack does to a persisted NPC in a cell | [~] (enabled, untested) |
| P18.9 | Downable but not killable: `ai/ai.java` `OnIncapacitated` skips its kill + inventory wipe for loose droids (it would otherwise kill them and empty the inventory holding the parked PCD); `ai.stationed_droid` revives after 45 s. Cap raised 10 -> 25 | [~] (compiles, untested) |
| P18.10 | Patrol mode (wander up to 15 m + attack aggressive creatures within 20 m on sight; guard now only fights when owner or droid is attacked); script-driven roaming replaced the engine loiter (dsrc `feature/stationed-droids-patrol`, merged) | [x] merged, owner confirmed droids walk |
| P18.11 | Movement fixes after first in-game test (dsrc `feature/stationed-droids-movement`, `559c8555f`, `03309ad6d`, `a6fab46bc`): (a) roam only to spots in line of sight (`canSee`), short hops (2-6 m, 2-3.5 m indoors), range check vs post, outdoor rise limit; (b) retry in 1.5-3.5 s when no spot is visible or the path is rejected, not the old 6-14 s; (c) `ai.ai.OnMovePathNotFound` warps a creature to its AI home on every failed path = the visible teleport: overridden in `ai.stationed_droid` (returns `SCRIPT_OVERRIDE`) AND the engine AI home is set to the droid's current spot before each hop as a second safeguard; (d) casual speed: walk at 60-100 % of walk speed, 15 % chance of a slow jog (50-75 %), 4-12 s pause after each hop (20 % chance of a 15-30 s idle); full speed restored (`resetSpeed`) for combat and `applyMode`; (e) POB packing: loose droids aboard are returned to the owner's datapad right before the hull is packed (`space_transition.packShip` and `restoreShipToControlDevice` call `stowLooseDroidsAboard`); if the datapad is full they are placed beside the ship instead. Superseded by P18.12: the stowed droids now come back by themselves | [~] (compiles, untested) |
| P18.12 | Droids in POB ships come back by themselves after pack + call (dsrc `feature/stationed-droids-pob-restore`, 6 commits, tip `17067fcef`). **Pack** (`space_transition.packShip` / `restoreShipToControlDevice` -> `stationed_droid.stowDroidsAboard`): each loose droid aboard is stowed: its PCD goes back to the owner's datapad and is LOCKED (`stationed.aboardShip` objvar on the PCD, calling it from the datapad is refused with a message), a record `pcd|owner|cellName|x|y|z|yaw|mode` is written on the SHIP (`stationed.aboard`, String[]; post = the droid's home, so a wandering droid returns to its post), `ai.stationed_ship_restore` is attached to the ship, and the droid object is destroyed. The datapad droid cap is not applied to the stow (locked PCDs cannot be called; the loose cap of 25 still holds). If the owner is offline or the datapad refuses the PCD, the old fallback applies (droid placed beside the ship). **Call** (`space_transition.unpackShipForPlayer`, all 3 success exits, and after a FAILED pack): `restoreLooseDroidsAboard` schedules `handleRestoreLooseDroids` on the ship after 3 s. `stationed_droid.restoreDroidsAboard` creates ONE droid per pass with `pet_lib.createPetFromData(pcd)` (it must be serial: `makePet` destroys a droid created while the owner is at the active-droid cap), puts it on its post in the recorded cell, removes record + lock, and 1.5 s later (`handleFinishLooseDroid`, after the pet setup messages ran) `finishAboardRestore` runs the normal `setLoose` (quiet), restores mode, home and facing, then the next droid starts. Owner seated / in combat / at the active-droid cap: retried every 5 s for 2 min, then given up (lock released, PCD stays in the datapad, message). Owner offline or ship in space: records are kept for a later unpack. `OnInitialize` on the ship retries after a server restart. Failure never loses a droid: the PCD is always in the owner's datapad. No serverdata / client / table / C++ changes, strings are plain system messages | [~] (compiles, record format unit-tested, untested in game) |
| P18.13 | Droids in POB ships: 2nd droid not stowed / droid falls through the hull on the next call, nothing stowed when the ship is stored by Ship Travel (dsrc `feature/stationed-droids-pob-robust`). **Root cause (from code, not yet confirmed by a log):** a restore takes ~3 s + 1.5 s per droid, one droid at a time, while Store / Ship Travel pack the POB hull after a fixed 6 s delay (`handleAtmosDelayedStore`). A droid that is created but not yet set loose is an ordinary follower pet, so `stowDroidsAboard` (which only looked for `stationed.owner` droids in `getContents(cell)`) skipped it; the hull was packed with the droid still in a cell, and the engine drops cell contents of a ship that is placed again, so the droid fell through (and its PCD stayed parked in it, so nothing showed in the datapad). Ship Travel hits it most because the ship is typically stored right after Call. **Fixes:** (1) in-flight marker on the ship (`stationed.restoring.droid/.record/.time`) set when a droid is created, cleared when it is loose; `stowDroidsAboard` / `sweepPackedShip` put a half-restored droid back via `pet_lib.storePet` and re-write its record + PCD lock (`restowInFlight`), so it returns on the next unpack; a finish step that finds the ship packed again does the same. (2) droid discovery = cell contents + the owner's loose-droid registry (`findDroidsAboard`, checks the container chain), and plain follower droids left in the hull are stored. (3) post-pack safety net `space_transition.sweepPackedShipDroids` after every successful `packShip` / `restoreShipToControlDevice`. (4) a restored droid is never set loose unless it really is inside the hull (`isAboard`): retried up to 10 times, then put back in the datapad with a message. (5) `recoverFallenDroids` at the start of each restore: a registered droid standing outside while its post (`stationed.home`) is in a cell of this ship is moved back to its post. (6) only one restore runs at a time (stale marker after 20 s is re-stowed). (7) every `stowDroid` failure now logs its reason (`stationed_droid` log category). No serverdata / client / table / C++ changes | [~] (compiles, untested in game) |

| P18.14 | Droids still end up outside POB ships and are not brought back; weird movement (dsrc `feature/stationed-droids-hull-containment`, tip `adf4b1a2d`). **Cause found by reading engine + script code (not yet confirmed by log):** (a) `AICreatureController::moveAlongGround` only collision-tests moves inside a city pathfinding region (or when following/fleeing); a roaming droid inside a hull is not in one, so it walks without collision and can cross a portal into the world cell or leave the cell geometry. (b) `ai.stationed_droid.pickRoamSpot` and `OnMovePathNotFound` then OVERWROTE the post (`stationed.home`) with the droid's current spot, so the outside became its post and every stow / recover routine (which trust the post) saw nothing wrong: this is why fallen droids were never brought back. (c) guard/patrol scanned 20 m and chased creatures outside the ship through the door. **Fixes (script only, no C++):** post inside a ship is never re-homed; `stationed_droid.recoverIfFallen` is now a POSITION leash (same cell as the post and within roam range + 3 m, else `setLocation` back to the post; a container check cannot see a droid that left through a wall but is still a child of the cell); watchdog every 3 s for droids with a ship post (10 s elsewhere), also checked at each roam tick and hop end, in `applyMode` and on `OnMovePathNotFound`; `mayEngage`: a droid with a ship post only fights targets aboard the same ship. **Movement:** the droid now turns to face the spot (and waits turn-angle / 150 deg/s, max 1.6 s) before each hop, because the server snaps the facing while the client turns gradually (sideways sliding, turning halfway). Always-running animation NOT explained by code (server sets walk correctly, droid templates have walk 2 / run 6-8): a throttled `[droid] hop: walkSpeed=.. runSpeed=.. chosen=..` line is sent to the owner once per minute, please report it. Droids already out with a corrupted post must be picked up and set loose again. Optional C++ follow-up (not done): `testCollisions` also true for creatures in a non-world cell in `moveAlongGround` **Owner chat log 2026-10-22 22:45 (checked against the code):** (1) no `[droid]` debug line appears at all although `DEBUG_MESSAGES = true` since P18.13c, and the only droid messages are the P18.12 ones, so that test ran on a server WITHOUT the P18.13c build (verify with `grep -c -a "[droid] " ~/repos/swg-main/data/sku.0/sys.server/compiled/game/script/library/stationed_droid.class`, must be above 0). (2) the failures happen with the ship OUT in the world and the droids wandering: 3 droids on Wander, owner leaves the ship, droids drop to the planet surface within seconds; a stowed + restored droid (`back at its post aboard the ship`) is gone again after boarding. Stow works (single droid stowed and restored fine); a droid that already walked out is never stowed because its post was overwritten outside (fixed in P18.14). Likely exit route: a hop target in line of sight beyond a door portal (`canSee` passes portals) and uncollided AI movement crosses it. P18.14 returns such a droid within 3 s but does not yet stop the attempt; next step if still seen: validate hop targets with `isRelativePointOnSameFloorAsObject` (needs the ship yaw to turn cell offsets into world offsets) | [~] (compiles, untested in game) |

- **P18.14 deploy incident (2026-10-22):** the owner test of 22:45 ran on OLD classes: `utils/build_java_single.sh` on the server was a 0-byte file (cause unknown), so every rebuild silently did nothing. Added `utils/build_java_checked.sh` (loud failure checks), `stationed_droid.BUILD_TAG` (`[droid P18.14-1]` in every debug message) and WORKFLOW 2.4.1. After the fixed rebuild on 2026-10-22 both classes contain the P18.14 code (`recoverIfFallen: droid`, `handleRoamGo`); in-game result of P18.14 still pending.

- **P18.15 (dsrc `feature/stationed-droids-natural-speed`, tag `P18.15-2`):** owner test of P18.14 (build verified): spawning, storing and position repair work reasonably; movement still slides sideways mid-hop. **Client source read (RemoteCreatureController::realAlter):** the client does not walk along its facing; it moves straight toward the LAST SERVER POSITION, turns separately at the turn rate, and when it lags more than its own max walk speed (metres) behind the server position it RUNS at full run speed to catch up. Scaling walk speed to 60-100 % shrank that threshold (run bursts, slides) and jogs of 3-14 m/s on 2-3.5 m hops made it worse (logged `hop:` lines: walk 1.0-1.9, run 6.4-14, chosen up to 7.1). Fix: walk at 100 %, `ROAM_JOG_CHANCE = 0`. **Owner decision 2026-10-23:** roam range stays at the full `WANDER_MAX` / `PATROL_MAX` inside ships (a smaller range was tried and rejected; it is not the fix for the sliding). Instead, `isHeldAtPost` treats another room of the SAME ship as held, and `pickRoamSpot` moves the post into that room (the post still never leaves the ship); only a droid outside the ship (world cell or foreign cell) or far from its post inside the same cell is put back. Tag `P18.15-2`. **Open:** right after every restore ("back at its post") all droids were found in the WORLD (cell 0) at the owner's position (3 droids on the identical coordinate in one round) within seconds, i.e. something warps them to the owner after set-loose; `recoverIfFallen` repairs it, now with a 1 s watch for 20 s after set-loose and the owner position in the `[droid]` line to confirm. Note: the server sends creature speed as int8 (`static_cast<int8>`), so speeds below 1 m/s arrive as 0. | [~] compiles, untested in game |

- **P18.16 (dsrc `feature/stationed-droids-roam-feel`, tag `P18.16-1`):** owner test 2026-10-23 13:07 on verified build P18.15-2. Works: stow of 3 droids, restore of 3 droids, recovery. **Still wrong:** (1) movement still slides sideways mid-hop even at plain walk speed `chosen=2.0` (speed is NOT the cause, owner was right). Ruled out by reading code: server sends a transform on every change (no sparse updates), server turn is instant and the path inside a cell is one straight segment when `canMove` passes, client turn rate is 180 deg/s at walk. Open hypotheses, none confirmed: client-side collision slide around furniture the server walks through (server `testCollisions` is false for creatures in a non-world cell and no script `canMove` exists, `canSee` only tests eye-height line of sight), or a path through cell graph nodes when `canMove` fails. Discriminating question for the owner: does a normal NPC/creature walking in the same place slide too (client) or only droids (script/engine)? (2) after EVERY restore the droids are found in the world at the OWNER's exact position (log: droid and owner coordinates identical to the last decimal) a second or less after "back at its post"; no script sends `handleMoveToMaster` and no other script warps a pet to its master, so the source is not found; `recoverIfFallen` (1 s watch for 20 s after set-loose) repairs it. **Changes now:** roam hops more frequent and longer (pause 1.5-5 s, 10 % long pauses 6-12 s; step 3-9 m, 3-7 m indoors) as requested by the owner, and the first 5 spot tries are within +/-75 deg of the facing direction (`ROAM_FORWARD_CONE_DEG`) so direction changes are gentle. **Separate finding, JVM crashes:** 715 `exe/linux/hs_err_pid*.log` (645 non-empty), mostly 2026-07-24 (433) and 2026-08-19 (114), 14 on 2026-10-21; problematic frames: `cfree` in libc (334) and `ExpertiseManagerNamespace::loadExpertiseTable(DataTable const&)` in SwgGameServer (309), `Archive::ByteStream::Data::getNewData` (2); last crash 2026-10-21 15:34 after 9 h 15 min uptime. Not related to droids, not investigated. Stray untracked files in the server checkout: `rc serverdata` (263 bytes, 2026-10-02), `src/tart GameServer` (200 bytes, 2026-10-16), pasted command lines. | [~] compiles, untested in game |

- **P18.17 (dsrc `feature/stationed-droids-restore-hold`, tag `P18.17-1`):** owner 2026-10-23: movement is fine for now (P18.16 deployed). Droids still appear at one spot where the OWNER stood a moment after the ship appeared (same spot for all droids when the owner stands still, an earlier owner position when moving). **Cause (from code, not yet confirmed in game):** a restored droid is created by `pet_lib.createPetFromData` at the owner's position, its AI home (`ai.ai.initializeScript`) is that spot and `makePet`/`petFollow` queue a follow behaviour towards the owner. Two engine paths then move it there: `ai.ai.OnMovePathNotFound` does `setLocation(self, aiGetHomeLocation(self))` for a calm creature, and `AiMovementFollow::alter` warps to its waypoint (the owner) when the creature is stuck 5 times (it cannot path from a hull cell to the world). My code only re-synced the AI home inside `applyMode`/before each hop and a single `stop()` at creation cannot cancel a follow that is still queued. **Fix:** `aiSetHomeLocation(droid, post)` right at creation, at finish and after every recovery; new ship-side loop `handleHoldRestoringDroid` (`stationed_droid.holdRestoringDroid`, every 0.25 s up to 10 s, until the droid is set loose): `stop()`, AI home on the post, and `setLocation` back to the post when anything moved it (logs `restore: hold put droid .. back on its post`). Files to build: `library/stationed_droid.java`, `ai/stationed_droid.java`, `ai/stationed_ship_restore.java`. Test: call the ship, stand still, watch for droids on the ground at your position; `[droid P18.17-1] restore: hold put droid` lines show the warp is still happening and from where. | [~] compiles, untested in game |

- **P18.17 test result 2026-10-23 14:17 (verified build P18.17-1, server restarted):** droids still land outside. Log: two droids (`...563693`, `...563815`) found in the world cell at the IDENTICAL coordinate (-2753.6711, 6.586618, 2732.3977), 3.15 m from the owner's position at that moment; NO `restore:` line and NO `restore: hold put droid` line in the pasted part, so it is open whether the warp happens during a restore (hold loop would have logged) or after the droid is set loose, or whether these droids were loaded from before a server restart. Tag `P18.17-2` (branch `feature/stationed-droids-warp-diag`) adds to the `recoverIfFallen` line: ship location, droid AI home, AI movement state and follow flag, so the next log shows whether the spot is the ship, the AI home, or an old owner position. Also found, **dsrc commit `d0738977c` (2026-08-11, author daquorm89, message `describe your dsrc changes`)** is a sweep-everything commit (`git add -A` style): 5723 files, of which 5674 are compiled `.class` files (still tracked in dsrc master, `.gitignore` does not cover them), 2 `*.bak_precu_20260809_*` backups, `magic.mgc` (4.9 MB), and the empty stray files `-C`, `cp`, `find`, `ls`, `mkdir`, `tar`; it also carries real source edits (pet.java, ai.java, cmd.java, command tables, ...). The message is an unfilled placeholder, so a template command was probably pasted literally. The stray names look like leftovers of botched shell lines (`tar -C`, `cp`, `find`, `ls`, `mkdir` taken as file names), not of a script in the repo (nothing in swg-main tooling uses that message). `rc serverdata` and `tart GameServer` were only ever untracked local files, never committed, and are deleted. The cause of the emptied `build_java_single.sh` is still unknown. **Owner decision 2026-10-23:** the 5674 tracked `.class` files in dsrc are intentional (the whole local project was pushed to GitHub) and MUST stay; only the stray files are removed: dsrc branch `feature/dsrc-remove-stray-files` deletes the empty `-C`, `cp`, `find`, `ls`, `mkdir`, `tar` and `magic.mgc` (a compiled copy of the `file(1)` database, header f11e041c, referenced by nothing in the build or tools; its `BEGIN OPENSSH PRIVATE KEY` text is a detection pattern, not a key). WORKFLOW 2.2 rule (branch `feature/workflow-no-git-add-all`): never `git add -A`, explicit paths and `git status` before every commit. | [~] diagnostics only |

- **P18.18 (dsrc `feature/stationed-droids-clear-follow`, tag `P18.18-1`) - cause of the "droids appear on me" warp found.** Owner log 2026-10-23 14:33 with the P18.17-2 diagnostics: droids `...563735` and `...563637` were found in the world cell at the owner's EXACT position (ship 10 m above, at the same x/z), with `aiHome` correctly inside the ship cell (so the AI-home theory of P18.17 is refuted), `movementState 3` (= `MOVEMENT_FOLLOW`) and `following true` (= objvar `ai.persistantFollowing`). **Cause:** the pet follow code leaves `ai.persistantFollowing` (target = owner) on the droid; `setLoose` never removed it; `ai.ai.doDefaultCalmBehavior` (run whenever a droid calms down, e.g. after `resumeDefaultCalmBehavior`) does `if (ai_lib.isFollowing(npc)) ai_lib.resumeFollow(npc)`, restarting the follow towards the owner; a hull room has no path to the world, the follow gets stuck 5 times and `AiMovementFollow::alter` warps the droid onto the owner. **Fix:** `stationed_droid.clearFollowState` removes `ai.persistantFollowing`, `ai.formationType`, `ai.inFormation`; called in `setLoose`, `applyMode`, the restore hold loop, `finishAboardRestore`, `recoverIfFallen` and before every roam hop. Ship watch interval 3 s -> 1.5 s (`WATCH_TICK_SHIP_SEC`). **Second finding, unchanged:** one droid (`...563735`, `movementState 5` = MOVE) was found in the world at the ship's altitude (y 13.6, ship at y 15.2, 13 m from the ship's x/z) while hopping, i.e. it walked out of the hull through a doorway or wall in mid air, then was put back by `recoverIfFallen` "after a few seconds". Also seen: roaming droids before the ship was called ("no droid should be out"): droids whose post is in a packed ship cannot be recovered (`recoverIfFallen` needs the ship out in the world) and keep roaming where they stand; they go back when the ship is called. Not yet addressed. | [~] compiles, untested in game |

- **P18.19 (dsrc `feature/stationed-droids-area-scan`, tag `P18.19-1`):** owner 2026-10-23 (P18.18 merged, NOT yet built on the server): droid sounds are heard near the owner even when the ship is stored, the droids are not seen. So droid objects are still alive in the world after the pack. The stow only finds droids in the ship's cells or in the owner's objvar list `stationed.droids`, so a droid that fell out of the hull and is not in that list is never stowed or recovered (also: droids whose post was overwritten outside by the old rehome bug, droids from older builds). **Added:** `stationed_droid.areaDroidsOfShip` (200 m scan around the ship with `getCreaturesInRange`, loose droids of the same owner whose post is in this ship) used by `findDroidsAboard` (stow) and `recoverFallenDroids` (ship call). With the debug flag on it reports every loose droid of the owner in the area: `area scan: loose droid <id> in the world at <loc> (terrain y ..), post in this ship: true/false` and a summary line. **Not covered:** loose droids whose post is NOT in this ship (old rehome bug) are only reported, not touched; they must be picked up by hand; hidden droids (underground or far away) cannot be picked up, the scan output shows their position.  **Owner follow-up:** all droids are HEARD (random droid sounds near the owner) while the ship is stored but none is seen, "as if the physical droid is removed but the voices stay attached to me". Server side: `stowDroid` ends with `destroyObject(droid)` (verified), `storePet` only sends `handlePackRequest` to a droid that no longer has `ai.pet`, no script in the droid/pet code plays droid sounds. So either a server droid object survives somewhere or the CLIENT keeps a ghost creature object (destroy message lost). Discriminating test for the owner (no deploy): after the sounds start, relog; sounds gone after relog = client ghost object, sounds still there = server object. Tag `P18.19-2` also audits non-stationed droid creatures that still have the owner as master in the area scan (`area scan: droid creature <id> (not stationed) template .., master .., at ..`). | [~] compiles, untested in game |

**Implementation status (2026-10-21) - code only, compiles with javac against the dsrc sourcepath, NOT deployed or tested in game**

- Branch `feature/stationed-droids` in three repos: `dsrc` (head `0ed22f413`, 6 commits: library x4, ai script, pet.java hook), `serverdata` (`bb5c43535`, strings), `swg-main` (this file + `tools/stf_tool.py`).
- Compare: https://github.com/daquorm89/dsrc/compare/master...feature/stationed-droids , https://github.com/daquorm89/serverdata/compare/master...feature/stationed-droids , https://github.com/daquorm89/swg-main/compare/master...feature/stationed-droids
- Deploy: `./utils/build_java_single.sh` for `library/stationed_droid.java`, `ai/stationed_droid.java`, `ai/pet.java` (all under `dsrc/sku.0/sys.server/compiled/game/script/`); copy `serverdata/string/en/pet/pet_menu.stf` to the server string path and the client; restart GameServer, full client restart. No tables, no templates, no C++.
- Smoke tests: (1) call a droid out, radial > Droid Options > Set Loose: message, droid stays, datapad slot freed. (2) Stand / Wander / Guard each behave; Guard: aggressive creature walks up, droid engages, then returns to post. (3) Open storage and datapad from the loose droid's radial: contents intact. (4) Pick Up: droid vanishes, PCD back in datapad, Call works, chips/items/damage preserved. (5) Restart GameServer with a loose droid: it is still there with the same mode. (6) Incapacitate a loose droid: recovers after ~45 s. (7) 11th droid is refused. (8) Another player sees no owner menu. (9) Kill/destroy a loose droid (`/destroy`): PCD must reappear in the owner's datapad.
- **Unverified, highest risk first:** (a) `putIn(pcd, droidInventory)` accepted by the engine (volume / arrangement of an intangible in a creature inventory), rollback exists if refused; (b) a persisted AI creature restores its mode and master after restart (`OnInitialize` re-applies both); (c) `pvpCanAttack` / `aiIsAggressive` pick sensible guard targets; (d) a loose droid killed while its owner is offline loses its PCD (owner datapad not loaded, `rescuePcd` logs and gives up).
- **Tweaks branch (2026-10-21):** `feature/stationed-droids-tweaks` in `dsrc` (commit `1692c70ea`) and `swg-main`. Cap 25, ships/POB allowed, and a fix for a bug in the first version: a loose droid is no longer a pet (`ai.pet` detached clears the `ai.pet` objvar, so `pet_lib.isPet` is false), so `ai.ai.OnIncapacitated` would have killed it and emptied its inventory (the parked PCD included). The engine only incapacitates at 0 health (`CreatureObject::testIncapacitation`); death comes from scripts (`kill`/`reallyKill`) or environment (lava). The remaining death paths (lava, GM `/destroy`) still hit the PCD rescue in `OnDeath`/`OnDestroy`. Extra smoke tests: (10) shoot a loose droid to 0 health: it goes down, stays in the world with its inventory, and stands up after ~45 s; (11) set loose inside a POB cell and on a ship, restart the server and, for ships, pack/unpack the ship: droid still present; (12) set loose 25 droids, the 26th is refused.
- Known limits: no power drain while loose; loose droids do not count against droid-slot limits; the registry (`stationed.droids` on the player) only shrinks on pick up or droid destruction; if the droid was the commanding droid, setting it loose recalls the linked army (existing `removeActiveDroid` behaviour).
- **Movement-fix smoke tests (P18.11):** (17) wander outdoors: droid walks short hops, pauses a few seconds between, speed varies, mostly walking. (18) wander inside a house / narrow room: droid never walks into walls and never snaps back to its post; if boxed in it stands and retries every few seconds. (19) [superseded by 23-28]. (20) owner offline when the ship is packed: droid appears beside the ship. (21) patrol/guard fight: droid runs at full speed in combat and goes back to casual speed afterwards. (22) set loose droids still pick up and restart persistence as before. **POB restore tests (P18.12):** (23) set a droid loose inside a POB ship (Stand), Store the ship: system message says it was stowed; the datapad shows its PCD; choosing Call on it says it is stationed aboard the ship. (24) Call the ship again and wait ~5-10 s: the droid is standing on the same spot in the same room, still loose (radial menu works), with the same mode; the datapad slot is free again; no "now loose" message, one "back at its post" message. (25) same with Wander and Patrol: mode is kept, post is the original spot (a wandering droid returns to its post, not where it was when the ship was stored). (26) three loose droids in two rooms, Store, Call: all three return, one after another (a few seconds apart), each in its own room. (27) Store and Call the ship twice in a row, and board the ship (boarding re-seats the pilot with a pack + unpack): droids are never duplicated or lost. (28) Pick up the droid after restore: PCD in datapad, Call works, chips and cargo intact. (29) Call the ship while a droid is already out as your follower (at the droid cap): the loose droid waits and retries; store your follower and it appears; after 2 minutes without a free slot it gives up and the PCD is simply in the datapad (message). (30) delete the PCD from the datapad while the droid is stowed, then call the ship: nothing appears, no error loop in the GameServer log.
- **P18.13 smoke tests:** (31) two loose droids (mouse droid + droideka) in different rooms, Store, Call: both come back, none appears on the ground under the ship. (32) Call the ship and press Store (or Ship Travel > Travel Locations) within 3-8 s, i.e. while the droids are still being restored: after the pack both PCDs show in the datapad (locked), no droid is left in the hull; Call again: both come back. (33) repeat (32) three times in a row. (34) Ship Travel with two droids aboard: both stowed before the starship window opens; on arrival call the ship: both return. (35) a called-out follower droid standing in the ship when it is stored goes back into the datapad as a normal stored droid. (36) GameServer log check: lines `stowDroidsAboard: ... candidates=N`, `restore: created droid=... aboard=true`, no `restowInFlight` in a calm Store/Call cycle; any `stowDroid: droid ... not stowed: <reason>` line says why a droid was not stowed.
- **P18.11 unverified:** whether `canSee(obj, location)` behaves in cells and on terrain (a safety valve takes a 2 m blind hop toward the post after 6 empty ticks in a row); whether `setMovementWalk` + `setMovementPercent` changes the speed of a droid at all (if droids still move at the same speed, check the GameServer log and send it); trigger order of `ai.stationed_droid` vs `ai.ai` for `OnMovePathNotFound` (covered by the AI-home safeguard either way); what the engine does with creatures in a packed POB (stow avoids it). **P18.12 unverified:** `createPetFromData` + `setLocation` into a cell of a ship that was only just placed in the world; whether the 1.5 s finish delay is long enough for `handleAddMaster` (`getSetLooseBlocker` retries the finish up to 10 times, so a late master link is covered); `getCellName`/`getCellId` round trip for every POB cell name; `setYaw` inside a cell (cosmetic only); that `getContainedBy(ship)` is invalid for a ship placed by Call (otherwise the restore pass returns early and the droid stays in the datapad: check the GameServer log for `restore:` lines and tell me); the droid owner is not the ship owner case (the droid owner must be online, upright and on the same planet server when the ship is called, otherwise the record waits for a later unpack).
- **P18.13c (owner test 2026-10-22 16:39: still only one droid stored):** cause not found by reading the code. `stowDroidsAboard` / `sweepPackedShip` now handle every droid in its own try/catch (before, one exception skipped all remaining droids). `stationed_droid.DEBUG_MESSAGES = true` sends every stow / sweep / restore decision to the owner as a `[droid] ...` system message (also logged), e.g. `stow: 2 droid(s) found aboard`, `stowDroid: droid X not stowed: <reason>`, `restore: created droid=... aboard=true`. Set the flag to false once stable. When reporting a failure, paste the `[droid]` lines of that Store / Call.
- **P18.13b (owner test: loose droids still fall through the hull and are not stored with the ship):** the first P18.13 pass only saw droids still standing in a cell. Now: (a) `findDroidsAboard` also returns registered droids whose post (`stationed.home`) is in the hull although they stand outside, and `stowDroid` files the record under the post, so a fallen droid is stowed on Store; (b) `needsRestorePass` makes every Call run `recoverFallenDroids` even without records; (c) every loose droid runs a 10 s `handleWatchTick` that calls `recoverIfFallen` (moves it back to its post when the ship is out in the world and the droid is outside it). Still unknown: the exact moment droids fall. If it still happens, the log line `recoverIfFallen: droid ... stands outside ship ...` shows how often and when. Test 37: set a droid loose in a POB, Call/Store 3 times: droid always ends up inside; a droid pushed outside is back within ~10 s.
- **P18.13 unverified:** that `space_transition.getContainingShip(droid)` returns the ship for a droid standing in a cell of a ship that was just placed (if not, `isAboard` falls back to the cell location, and a droid that is really inside could be retried 10 times and then put back in the datapad with a message: look for `restore: droid ... is not aboard ship` in the log); `pet_lib.storePet` on a droid standing in a packed hull (it relies on the pet's `handlePackRequest` message running there); that the ship's `getOwner` is the droid owner (recovery and registry discovery use the ship owner's registry only); `getCellName` is non-empty for every POB cell (a droid in an unnamed cell is ejected beside the ship, see the `unusable cell name` log line). The failure the owner saw is derived from reading the code; if smoke test 32 still loses a droid, send the `stationed_droid` log lines around the Store.
- Revert: remove the `SERVER_MENU8` lines in `ai/pet.java`; existing loose droids can still be picked up through their own radial menu, so do not delete the two new scripts while any are out.

---

## Completed projects

### P8 — client-tools: fix startup access violation in Transceiver message dispatch (completed 2026-08-15)

**Repo:** [daquorm89/client-tools](https://github.com/daquorm89/client-tools) (see its own `WORKFLOW.md`)

A local sync of client-tools onto GitHub surfaced a pre-existing bug: `TransceiverBase::getGlobalReceiverInfo()` in `Transceiver.cpp` had been changed to ignore its `typeId` and return one shared static `GlobalReceiverInfo` for every `Transceiver<MessageType, IdentifierType>` instantiation in the engine, instead of a per-type entry (keyed by `typeid.name()` in a `std::map`, as designed). This caused message-type cross-talk — e.g. a `bool` push-to-talk message invoking an auction-bid callback with the wrong payload — producing a 0xC0000005 access violation very early in client startup (`CuiIoWin::resetInputMaps` / `CuiMessageBox` construction), with a callstack that looked corrupted because of the type confusion.

- Fixed: restored the original per-type `std::map<const char * const, GlobalReceiverInfo>` lookup in `Transceiver.cpp` (PR `fix/restore-per-type-receiver-registry`, commit `9a4ca6fd1`).
- Also restored `Transceiver()`'s constructor call to `getGlobalReceiverInfo(typeid(this))` to match true upstream (PR `fix/restore-upstream-transceiver-ctor`, commit `75280c00a`) — an earlier local commit had disabled this call with a `"TEMPORARY: disabled to bypass early-startup RTTI crash"` comment that was itself part of the same broken commit, not a genuine upstream safeguard.
- **Documented fallback** (in commit `75280c00a` message and `6ff027afb`/`24addb980` history): if a similar early-startup RTTI/access-violation crash reappears and the `Transceiver.cpp` registry isn't the obvious cause, commenting out `getGlobalReceiverInfo(typeid(this));` in the `Transceiver()` constructor is a known, working short-term mitigation that got the client launching before the real cause was found. Not a substitute for finding the real cause if it happens again.
- Other changes bundled in the same local sync (`PlayerCreatureController.cpp`, `CreatureObject.cpp/h`, `SkillObject.cpp/h`, `LocalizedStringTable.cpp/h`, new `SwgCuiSkills.cpp/h` ~2000 lines, etc.) are intentional in-progress work and were left as-is — not reviewed as part of this fix.
- **`SwgGodClient` project changes are deprioritized** — see Deferred below.

```markdown
### Px — Title (completed YYYY-MM-DD)

Summary of what shipped. Link key PRs/commits if useful.
```

---

## Deferred (explicitly not full projects until scope says so)

- Creatures / spawns / lairs (leave NGE baseline)
- Loot tables (leave NGE baseline)
- World / planet content (leave NGE baseline)
- Full world crafting economy (schematic grants may still be fixed as combat/profession blockers)
- **Full** Pre-CU combat math replacement (to-hit, armor, multi-pool damage split like Core3) — only if NGE simulation fails after hybrid + HAM reconnect
- **Full** Core3 9-stat attribute model + client HAM chrome — tracked as P6.8, not active work until P6.1–P6.7 settle
- C++ engine rewrites (last resort after table/script reconnect)
- Importing or linking Core3 binaries/sources into this tree
- **`SwgGodClient`** (client-tools dev/admin tool) — its project file changes are not being pursued for now; risk of destabilizing the main `SwgClient` build outweighs current value. Leave as-is unless explicitly revisited.

---

## Evidence snapshot (combat systems survey)

Captured for agents so scope estimates stay tied to the trees (NGE `dsrc`/`src` vs Core3 ref only). Refresh when findings change.

| Topic | NGE finding | Core3 ref finding |
|-------|-------------|-------------------|
| Attribute pools | 6 stats; H/A/M pools + shock wounds in engine | 9 primaries including Str/Qui/Foc |
| Combat costs | `healthCost`/`actionCost`/`mindCost` columns widely present | Cost multipliers per command Lua/C++ |
| Live drain | Action-first + expertise | Full H/A/M spend and damage pools |
| Command queue | Full queue in C++; defaultTime dead; exec/warmup columns | QueueCommand per ability |
| Targeting | validateTarget + LOS + range in combat_base | QueueCommand target checks + CombatManager |
| Combat entry surface | `combat_actions.java` ~15k lines; `combat_data` ~1608 rows | ~856 command headers; CombatManager ~3.6k lines |
| Dormant NGE | `combat_base_old.java` ~2.8k lines (older multi-pool costs) | — |

---

## Changelog (status file only)

| Date | Change |
|------|--------|
| 2026-08-11 | Initial PROGRESS.md: P1 combat hybrid, P2 skill spine, P3 process docs |
| 2026-08-13 | P1 posture sub-targets P1.9–P1.12; add P4 command queue, P5 targeting, P6 HAM reconnect; evidence snapshot; deferrals clarified |
| 2026-08-15 | Added P8 (completed): client-tools Transceiver message-dispatch startup crash fix; linked client-tools repo + its own WORKFLOW.md from this file; deferred SwgGodClient |
| 2026-08-16 | P6.9 soft-SQF: skill-mod Strength/Quickness/Focus cost approximation (no 9-stat engine). Branch `feature/precu-soft-sqf-ham`. Explicit REVERT steps in P6 notes. |
| 2026-08-17 | Soft SQF retune+armor tax+food modified; grants: racial mods + profession novice strength/quickness/focus; added todo.md with PR links and deploy commands. |
| 2026-09-29 | Added P10: AT-XT fire while driven (location-target command for ground marker + fire without auto-aim). dsrc branch `feature/at-xt-location-ground-target`. |
| 2026-09-29 | Added P11: space wingmen as tiered droid programs (Freelancer/Alliance/Imperial), 3 escort fighters per tier. Feasibility done, no code yet. |
| 2026-09-29 | Added P11: space wingmen feasibility (verified) + plan. Branch `feature/progress-p11-space-wingmen`. |
| 2026-09-29 | P11 implemented (code only): dsrc + serverdata branches `feature/space-wingmen`; P11.2-P11.7 done or partial, P11.8-P11.9 open. Earlier local work had never been pushed and was rebuilt. |
| 2026-10-01 | P11: wingmen friendly-fire fix on dsrc `feature/wingmen-friendly-fire`. Added P12: atmospheric fly-up-to-space exit + Mustafar -> Nova Orion, dsrc `feature/atmos-exit-to-space` (code only). |
| 2026-10-02 | P9.9: multi-droid formation slots (droids stacked on one spot). dsrc `feature/droid-formation-slots` (code only, uncompiled/untested). |
| 2026-10-02 | P9.10: droid slot cap 5 -> 24 (1:1 rating), guard assist + droid slash commands reach every droid. dsrc `feature/multi-droid-slots-and-guard` (compiles, untested in game). Earlier unpushed attempt was lost and redone. |
| 2026-10-04 | P12 follow-up: fix questManager exception on ground Call Ship; start altitude watch on all pilot-seat paths. dsrc `feature/atmos-exit-watch-and-station-fix` (code only). |
| 2026-10-04 | P12.9/P12.10: Ship Travel radial (starport picker) and 5 m hover parking on exit. dsrc `feature/atmos-ship-travel-and-park` (compiles, untested). |
| 2026-10-05 | Skill trainer no longer lists already-learned skills in the learn list (dsrc `feature/trainer-hide-learned-skills`, compiles, untested). Ship radial diagnostics added (P12.9c). |
| 2026-10-05 | P12.9d: Ship Travel opens the real starship terminal window (free) instead of the ticket window. dsrc `feature/atmos-ship-travel-and-park` (compiles, untested). |
| 2026-10-06 | P12.11: space mouse flight now has a zero center deadzone (client-tools `feature/space-mouse-zero-deadzone`, untested). |
| 2026-10-10 | Added P13: creatures above table level 70 (most of Mustafar) untameable because full Creature Handler tame_level is 70; cap level at 70 in taming/call math. dsrc `feature/tame-cap-high-level-creatures` (compiles, untested). |
| 2026-10-14 | Added P14: looted schematics showing NGE `class_*` skill names; hardening + diagnostic log on dsrc `feature/loot-schematic-skill-req-hardening` (compiles, untested). |
| 2026-10-14 | P15: mounted ranged combat still failing after the table edit; static investigation recorded (no cause found yet), next in-game test steps listed. |
| 2026-10-16 | P15: forced-RidingCreature rule replaced by a union rule (server + client); src and client-tools `feature/mounted-locomotion-union` (code only, untested). |
| 2026-10-17 | P15.9: creature-mount radial teleport bug still open; static review found no mount-start regression; temporary MOUNTDIAG diagnostic on dsrc `feature/diag-mount-radial` awaiting an in-game run. |
| 2026-10-17 | P15.9 run 3: stack trap shows server runs `taming.dismount` (client `dismount` command) ~1 s after mount; older client exe mounts fine, so the cause is a client-tools regression (candidates #36/#37/#38), not server code. |
| 2026-10-17 | P15.9 FIXED: radial_menu.tab GOD_TELEPORT row moved to index 109; verified in game (no stray dismount, mount holds, dismount works). Cleanup branch `feature/remove-mountdiag` removes the temporary diagnostics. Next: P15.6-P15.7 mounted-combat retests (heavy weapon, pistol, dismount). |
| 2026-10-17 | P15.10-P15.13: mounted heavy-weapon impact location (stale reticle point), projectile-vs-mount occlusion mitigation, double-mount radial fix identified. client-tools `feature/mounted-heavy-weapon-reticle`, dsrc `feature/radial-pet-mount-no-duplicate` (code only, untested). |
| 2026-10-17 | P15.14-P15.17: vehicle riders could not fire because `disableVehicleRiderCombatAnimationState` defaulted to true (attack stalled before playback). Fixed in client-tools `feature/vehicle-rider-combat-animation-state`, verified in game with MOUNTPLAYDIAG on a mount and a vehicle; saddle-based bolt occlusion fix on `feature/vehicle-mounted-bolt-saddle-appearance`. |
| 2026-10-17 | P12.12: POB ship erratic in atmosphere because interior items counted as obstacles in the client obstacle probe. client-tools `feature/atmos-pob-ignore-interior-objects` (code only, untested). |
| 2026-10-17 | P12.13: ships placed on the ground by Call Ship / Exit Ship are now levelled (yaw kept, pitch and roll zeroed). dsrc `feature/atmos-ship-level-on-ground` (compiles, untested). |
| 2026-10-17 | Added P16: POB pilot seat never granted programmed droid commands (empty Astromech tab on the YT-1300). dsrc `feature/pob-pilot-droid-commands` (compiles, untested). |
| 2026-10-19 | Added P17: POB ship certs (YT-2400, Y-8, 3 gunships) were required but granted by nothing; added to master pilot skills. dsrc branch `feature/pob-ship-certs` (code only). |
| 2026-10-20 | P16: POB droid commands re-granted on unpack, refcount-safe sync, refresh on equip/program add; 24 pilot maneuvers allowed in POB pilot seat. dsrc `feature/pob-droid-commands-sync-and-maneuvers` (compiles, untested). |
| 2026-10-21 | P18 tweaks: cap 25, ships/POB allowed, loose droids downable but never killable (fixes ai.ai kill on incapacitation). dsrc + swg-main `feature/stationed-droids-tweaks`. |
| 2026-10-21 | Added P18: Set Loose / Pick Up for datapad droids (stand, wander, guard). dsrc + serverdata + swg-main `feature/stationed-droids` (compiles, untested). |
| 2026-10-21 | INCIDENT: serverdata master (PR #10, `6eaca8499`) deleted 125,518 files -> GameServers crash with `appearance/defaultappearance.apt could not be found`. Restored on serverdata `fix/restore-serverdata-tree` (`fa6c4f6dc`, full tree from `74ec8240f` + patrol `pet_menu.stf`). Added WORKFLOW pitfall 9b (check file count before pushing submodule commits). |
| 2026-10-21 | P18.11: droid movement fixes (line-of-sight roaming, no warp-home on path-not-found, casual speed + pauses) and loose droids stowed to datapad when a POB ship is packed. dsrc `feature/stationed-droids-movement` (compiles, untested). |
| 2026-10-21 | P18.12: loose droids in POB ships are stowed on pack (PCD locked in the datapad, record on the ship) and restored by themselves, same spot and mode, when the ship is called out. dsrc + swg-main `feature/stationed-droids-pob-restore` (compiles, untested). |
| 2026-10-22 | P18.13: droids half-restored when a POB ship is stored (Store / Ship Travel) are put back instead of left in the hull; droids that fell out are recovered; droids are never set loose outside the hull; post-pack sweep; stow failures logged. dsrc + swg-main `feature/stationed-droids-pob-robust` (compiles, untested). |
| 2026-10-22 | P18.13b: droids that already fell out of a POB hull are now stowed with the ship (post inside the hull counts), recovered on every call (not only when records exist) and by a 10 s watchdog in `ai.stationed_droid` (`recoverIfFallen`). dsrc `feature/stationed-droids-pob-robust` (compiles, untested). |
