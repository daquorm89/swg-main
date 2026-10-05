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
- **P12.10 Park on exit:** `exitBesideShipOnGround` now calls `space_transition.parkShipHover` -> hull hovers at terrain+5 m (`GROUND_SHIP_ABOVE_PLAYER_Y`) after Exit Ship / Leave Station. Ship is not marked landed (landed sinks meshes). Pitch/roll are not levelled.
- Also: `ShipComponentDataManager ... hutt_heavy_s02_chassis_token.iff is not a component` warnings are a separate data issue (chassis token listed in a component table), not related to this fix.

**Exit criteria:** P12.6-P12.7 verified in game; P12.8 done or consciously deferred.

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
