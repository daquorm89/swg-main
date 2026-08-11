# Project Progress

Living status board for the NGE → Pre-CU restoration. **Humans and AI agents must read and update this file** when starting or finishing work.

Canonical process rules: [`WORKFLOW.md`](./WORKFLOW.md).

---

## How to use this file

1. **Active projects** have a short goal, owner/notes, and a list of **sub-targets**.
2. Mark a sub-target done with `[x]` when it is **merged to master, rebuilt on the server tree, and smoke-tested** (not when merely coded in a branch).
3. Add new sub-targets as discovery requires; keep them small and verifiable.
4. When **every** sub-target under a project is `[x]`:
   - Move the whole project block into **Completed projects**.
   - Replace the sub-target list with a one-line summary + completion date.
   - Do not leave empty shells under Active.
5. Do **not** invent projects outside [`WORKFLOW.md`](./WORKFLOW.md) scope (no loot/world/crafting until scope expands).
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

**Goal:** Pre-CU combat specials execute through NGE `combatStandardAction` + unique `combat_data.tab` rows, with weapon gates and usable status effects. Combat **math may stay NGE-based** if feel is acceptable and nothing conflicts with grants/abilities.

**Primary paths:** `dsrc` → `combat_actions.java`, `combat_data.tab`

| ID | Sub-target | Status |
|----|------------|--------|
| P1.1 | Generate hybrid `combat_data.tab` rows from Core3/Pre-CU command data | [x] |
| P1.2 | Add Java entry points in `combat_actions.java` calling `combatStandardAction` | [x] |
| P1.3 | Basic in-game fire (damage/cost/anim) for bulk of hybrid specials | [x] |
| P1.4 | Explicit weapon restrictions via `precuWeaponOk` (not data `weaponType` alone) | [x] |
| P1.5 | Map common Pre-CU states to existing NGE buffs (`buffNameTarget`) | [~] |
| P1.6 | Verify DoTs (`dotType` bleeding/poison/disease/fire) tick as intended | [ ] |
| P1.7 | Smoke-test matrix: wrong weapon fails, right weapon works, sample specials per weapon family | [ ] |
| P1.8 | Tune costs/damage only where hybrid rows feel broken vs intended Pre-CU role (no full math rewrite) | [ ] |
| P1.9 | Document remaining ability gaps (missing commands, bad anims, unmapped states) | [ ] |

**Notes**

- Weapon-check merged (`precuWeaponOk`): wrong weapon blocks damage/aggro and shows `no_attack_wrong_weapon`. Follow-up branch `feature/precu-weapon-fail-no-anim` calls `clearQueue()` on reject to reduce client-predicted hit/fire anim (verify after merge).
- Status buffs are interim (e.g. warcry → suppressing-style buff; KD/posture may be stand-ins).
- Out of scope here: pure Pre-CU combat curves, true Force pool, creatures/loot/world.

**Exit criteria:** P1.5–P1.9 all `[x]`, then move P1 to Completed.

---


### P3 — Project process & agent onboarding

**Goal:** Any human or AI can find rules, scope, build commands, and live status without chat archaeology.

| ID | Sub-target | Status |
|----|------------|--------|
| P3.1 | Add `WORKFLOW.md` (full scope, git, build, combat SOP) | [x] |
| P3.2 | Narrow build docs to real commands (`build_java_single.sh`, `make serverGame` / `SwgGameServer` in `x/`) | [x] |
| P3.3 | Scope: loot/world/crafting deferred; combat math may stay NGE | [x] |
| P3.4 | Add this `PROGRESS.md` and keep it updated with PRs | [~] |
| P3.5 | Merge workflow/progress docs to `master` on `daquorm89/swg-main` | [ ] |

**Exit criteria:** P3.4–P3.5 `[x]`, then move P3 to Completed (ongoing updates happen in place without a new “process” project unless SOP changes).

---

## Completed projects

### P2 — Pre-CU profession / skill grant spine (completed 2026-08-11)

Project lead reports profession/skill grant spine already working for current needs (train Pre-CU lines, receive commands). Re-open a new project only if a specific line/grant gap appears.

---


---

## Deferred (explicitly not projects until scope says so)

Per `WORKFLOW.md` — do not open Active projects for these without a scope change:

- Creatures / spawns / lairs (leave NGE)
- Loot tables (leave NGE)
- World / planet content (leave NGE)
- Crafting / resources / schematics (leave NGE)
- Full Pre-CU combat math replacement (only if NGE simulation fails)
- C++ engine rewrites (last resort)

---

## Changelog (status file only)

| Date | Change |
|------|--------|
| 2026-08-11 | Initial PROGRESS.md: P1 combat hybrid, P2 skill spine, P3 process docs |
| 2026-08-11 | P2 marked completed (professions already done). Note residual wrong-weapon client anim; clearQueue follow-up |
