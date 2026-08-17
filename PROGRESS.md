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
