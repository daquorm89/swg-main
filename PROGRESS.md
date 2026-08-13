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

**Exit criteria:** Pilot set spends and gates on H/A/M from tables; P6.5 policy recorded; P6.8 remains deferred unless scope explicitly expands.

---

## Completed projects

_None yet. When a project finishes, move it here like this:_

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
