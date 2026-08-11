# Pre-CU Restoration Workflow

**Project:** Modify an NGE-era SWG Source server toward authentic Pre-CU (Pre-Combat Update) gameplay while keeping an NGE-compatible client.

**Owner:** daquorm89 (`douweheuvel@gmail.com`)  
**Runnable server tree (local):** `~/repos/swg-main/`  
**GitHub (source of truth):** [daquorm89/swg-main](https://github.com/daquorm89/swg-main) (fork of SWG-Source) with submodules `dsrc`, `src`, `serverdata`, `stationapi`, `exe`/`configs`

This file is the standing operating procedure for **humans and AI agents**. Read it before changing code, data, or skills. Prefer updating this document when process changes, rather than relying on chat history.

---

## 1. Project goal (full scope)

Restore **Pre-CU skill-based professions and world rules** on top of an NGE server stack:

| Area | Pre-CU intent | Notes |
|------|----------------|-------|
| **Professions / skills** | Skill trees, boxes, XP types, titles from Pre-CU | Not NGE expertise wheels as primary progression |
| **Combat abilities** | Weapon specials, states, DoTs, posture, Jedi powers | Hybrid: `combat_data.tab` + thin Java (see §5) |
| **Combat math / balance** | Pre-CU damage, costs, ranges, defenses where practical | Reconnect dormant data; avoid full engine rewrite |
| **Commands** | Pre-CU command names, hooks, grant rules | `command_table` + scriptHooks |
| **Crafting / resources** | Pre-CU schematics, resource rules as targeted | Only when in active scope |
| **Items / weapons / armor** | Pre-CU templates, certs, mods | Client must still load assets |
| **Creatures / loot / world** | Pre-CU spawns, lairs, loot tables as needed | `serverdata` / datatables |
| **Jedi / Force** | Pre-CU visibility, costs, powers progression | Partial; Force pool may lag vigor mapping |
| **UI / client** | Must remain NGE-client compatible | No client edits unless explicitly approved |

**Combat is one subsystem among many.** Do not treat the combat hybrid as the whole project; do not break professions, grants, or world data to “finish” a combat tweak.

---

## 2. Standing rules (non-negotiable)

### 2.1 Design principles

1. **Reconnect before inventing.** Prefer dormant Pre-CU tables, scripts, and NGE columns/buffs over new frameworks.
2. **Client compatibility.** NGE client must load and play. Use NGE-safe animations, effects, and datatable schemas.
3. **Phased delivery.** Make systems *usable* first (grants fire, abilities execute, skills train), then deepen fidelity (states, pool damage, exact curves).
4. **Data-driven where possible.** Datatables and command tables first; Java only for gates, hooks, or missing engine support.
5. **No silent scope creep.** If a change touches professions + combat + loot, split into clear commits/PRs.

### 2.2 Git

- **Never commit to `main` / `master`.** Always a feature branch.
- **Author for all commits:** `daquorm89 <douweheuvel@gmail.com>`
- **Submodules matter:** Most game content lives in **`dsrc`** (scripts, datatables). Parent `swg-main` often only moves a submodule pointer.
- **PR base must be the fork:** `daquorm89/<repo>`, not upstream `SWG-Source/...`.  
  Use: `https://github.com/daquorm89/<repo>/pull/new/<branch>`  
  or: `https://github.com/daquorm89/<repo>/compare/master...<branch>`
- **Merge order:** merge the submodule repo first (e.g. `dsrc`), then parent `swg-main` if the pointer must move.
- **Do not commit tokens** into `.gitmodules` or history. Do not store PATs in project memory files.

### 2.3 Server vs GitHub

| Location | Role |
|----------|------|
| GitHub `daquorm89/*` | Source of truth, review, history |
| `~/repos/swg-main/` on the server machine | **Runnable** tree (build, DataTableTool, GameServer) |
| AI sandbox clone (e.g. `/home/claude/swg-main`) | Edit/push only; **not** the live server |

After a merge on GitHub, on the **server machine**:

```bash
cd ~/repos/swg-main
git pull origin master
git submodule update --init --recursive
# rebuild whatever changed (Java / DataTableTool) — see §7
# restart GameServer
```

### 2.4 AI agent expectations

- Read this file first.
- Confirm **which subsystem** is in scope (combat, skills, commands, loot, etc.).
- Search existing code/data before adding helpers.
- Prefer small, testable PRs with in-game smoke tests listed in the PR body.
- Update this `WORKFLOW.md` when introducing a new standing rule or completed phase.

---

## 3. Repository map

| Path / submodule | Contents |
|------------------|----------|
| `swg-main` | Build, tools, top-level config, submodule pins |
| `dsrc` | Server scripts (Java), shared datatables (`.tab`), skill/command sources |
| `src` | C++ engine sources (combat engine, objects) — change rarely; high risk |
| `serverdata` | Runtime data mirrors (e.g. compiled `.iff` trees as used by your deploy) |
| `stationapi` / `exe` (configs) | Station / process config |

### High-traffic Pre-CU paths (under `dsrc`)

```
dsrc/sku.0/sys.server/compiled/game/script/systems/combat/combat_actions.java
dsrc/sku.0/sys.server/compiled/game/script/systems/combat/combat_base.java
dsrc/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.tab
# skills, commands, crafting, etc. under analogous datatables/ and script/ trees
```

Exact skill-table and profession paths vary; always locate by name in `dsrc` before editing.

---

## 4. Subsystems (what “full Pre-CU” includes)

Work is organized by subsystem. Complete or stabilize one vertical slice before boiling the ocean.

### 4.1 Professions & skills

- Pre-CU profession lines (e.g. Marksman → Rifleman/Pistoleer/Carbineer, Brawler → …, medic, entertainer, crafters, Jedi).
- Skill boxes, prerequisites, XP types, skill mods, titles.
- Granting commands/abilities when a box is learned.
- **Expect:** skill datatables + grant scripts; avoid NGE expertise as the only progression.

### 4.2 Commands

- `command_table` (or equivalent): name, scriptHook, locomotion/state flags, target rules, range.
- scriptHook **must** match a Java method name when the command is script-driven.
- God/admin commands stay out of normal player grant paths.

### 4.3 Combat (hybrid restoration — active)

See **§5** for detail. Summary:

- Unique `combat_data.tab` rows from Core3/Pre-CU sources.
- Thin `combat_actions.java` methods calling `combatStandardAction`.
- Status effects via existing NGE `buffNameTarget` values where possible.
- **Weapon restrictions enforced in Java** (`precuWeaponOk`), not via `weaponType` alone.

### 4.4 Jedi / Force

- Powers, saber lines, visibility/hostility rules as Pre-CU requires.
- Costs may temporarily map to `vigorCost` until a true Force pool is restored.
- Prefer existing Jedi scripts/tables before new systems.

### 4.5 Crafting, resources, items

- Schematics, categories, resource classes, tool behavior.
- Weapon/armor templates and certifications aligned with Pre-CU professions.
- Keep client asset paths valid.

### 4.6 World, NPCs, loot

- Spawn tables, lair data, loot tables, quest hooks as required for Pre-CU loop.
- Changes often land in `serverdata` and shared datatables; coordinate with deploy/sync practice.

### 4.7 C++ engine (`src`)

- Only when Java/data cannot express the rule (rare).
- Requires full rebuild discipline and extra testing; treat as last resort.

---

## 5. Combat subsystem (detailed SOP)

### 5.1 Pipeline

1. Player uses command (e.g. `/actionShot1`).
2. Command table `scriptHook` → `combat_actions.java` method of the same name.
3. Optional **`precuWeaponOk(self, type, category)`** — hard weapon gate.
4. `combatStandardAction("actionShot1", self, target, params, "", "")`.
5. `combat_base` loads **`combat_data.tab`** row by `actionName`.
6. Costs, range, cone/area, damage fields, anims, `dotType`, `buffNameTarget` apply.

**Important:** `combat.canUseWeaponWithAbility` + row `weaponType` are **not** reliable equip gates for hybrid Pre-CU rows (`weaponType` is heavily used for overloaded weapon stats). Always use `precuWeaponOk` for Pre-CU specials that must require a weapon class.

### 5.2 Useful `combat_data.tab` columns

| Column | Role |
|--------|------|
| `actionName` | Matches Java method / scriptHook |
| `comments` | Tags: `precu_from_core3_lua`, `precu_status_buff` |
| `percentAddFromWeapon` / `addedDamage` | Distinct damage |
| `actionCost` / `healthCost` / `mindCost` / `vigorCost` | Costs (Force partially → vigor) |
| `attackType` / cone / range | Geometry |
| `animDefault` / `anim_*` | **NGE-safe** names only (e.g. `fire_3_single_medium`) |
| `dotType` / intensity / duration | bleeding, poison, disease, fire |
| `buffNameTarget` / strength / duration | Stun/dizzy/blind/etc. via existing buffs |

### 5.3 Combat phases (status)

| Phase | Intent | Status |
|-------|--------|--------|
| **A** | Rudimentary abilities execute (damage, cost, anim) | Largely done (~279 hybrid commands) |
| **B** | DoT tick verification / tuning | Ongoing as needed |
| **C/D** | Status effects via NGE buffs | Partially mapped (see below) |
| **E** | Weapon restrictions in Java | Done on master (`precuWeaponOk`) |
| **Later** | Pool-specific damage, true Force pool, posture API fidelity | Not done |

### 5.4 Status effect buff mapping (current)

| Pre-CU state | `buffNameTarget` | Examples |
|--------------|------------------|----------|
| STUN | `bh_stun` | stunAttack, wildShot*, fullAuto* |
| DIZZY | `bh_fumble` | dizzyAttack, flurryShot*, mindBlast* |
| BLIND | `co_flash_bang` | blindAttack, eyeShot |
| INTIMIDATE | `bh_intimidate` | intimidate*, wookieeRoar |
| NEXTATTACKDELAY | `co_supressing_handler` | warcry1/2, panicShot |
| KNOCKDOWN (interim) | `charge_stun_debuff` | knockdownAttack, chargeShot* |
| POSTUREDOWN (interim) | `en_sweeping_pirouette_root` | actionShot*, saberSlash* |

True posture/KD may need a posture API later; buffs are interim.

### 5.5 Weapon type constants (Java)

| Weapon | Constant (typical) |
|--------|----------------------|
| Pistol | `WEAPON_TYPE_PISTOL` |
| Carbine | `WEAPON_TYPE_LIGHT_RIFLE` |
| Rifle | `WEAPON_TYPE_RIFLE` |
| Heavy | `WEAPON_TYPE_HEAVY` |
| Unarmed | `WEAPON_TYPE_UNARMED` |
| 1h / 2h / polearm | `WEAPON_TYPE_1HAND_MELEE` / `_2HAND_MELEE` / `_POLEARM` |
| Sabers | `WEAPON_TYPE_WT_*_LIGHTSABER` |
| Force powers | category `combat.MELEE_WEAPON` (no guns) |

If compile fails on a constant name, grep this tree’s `combat_base` / base class for the actual symbol.

### 5.6 Combat helper scripts (agent artifacts)

Historically kept under agent `artifacts/` (not always in git):

- `generate_precu_combat_hybrid.py` — Core3 Lua → rows + Java stubs  
- `patch_precu_status_effects.py` — buff mappings  
- `patch_combat_actions_weapon_check.py` — inject `precuWeaponOk`  
- Python target: **3.5+** compatible (older server VMs)

Prefer checking these into `tools/` or `docs/scripts/` on a feature branch if they become long-term.

---

## 6. Standard change workflow (any subsystem)

### 6.1 Before coding

1. Read this document.
2. Name the subsystem and success criteria (one sentence).
3. Locate existing Pre-CU or NGE data/code to reconnect.
4. Create a feature branch from updated `master`.

### 6.2 Implement

- **Data:** edit `.tab` (or generate via script); keep schema column counts intact.
- **Scripts:** thin methods; match scriptHook names exactly.
- **Engine (`src`):** only with explicit justification.

### 6.3 Build on the server machine

```bash
# Java example (combat)
cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/systems/combat/combat_actions.java

# Datatable example
cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/combat/
~/repos/swg-main/build/bin/DataTableTool -i combat_data.tab
# Sync .iff into the path your GameServer actually reads (often serverdata/) if required
```

### 6.4 Git publish

1. Commit in the correct repo (usually **`dsrc`**).
2. Push feature branch; open PR vs **`daquorm89/...` `master`**.
3. If needed, bump submodule pointer on **`swg-main`** in a second PR.
4. After merge: pull + submodule update on **server**, rebuild, restart, smoke-test.

### 6.5 Definition of done

- [ ] Feature branch + PR on correct fork/base  
- [ ] Merged to master (submodule then parent if both)  
- [ ] Server tree updated and rebuilt  
- [ ] In-game smoke test notes (pass/fail)  
- [ ] `WORKFLOW.md` updated if rules/phases changed  

---

## 7. Smoke tests (examples)

### Combat

| Equip | Command | Expect |
|-------|---------|--------|
| Rifle | `/actionShot1` | Fail — wrong weapon |
| Pistol | `/actionShot1` | Works |
| Carbine | `/fullAutoSingle1` | Works |
| — | `/warcry1` | Fires; suppressing-style buff if status patch applied |

### Skills / grants

- Train a Pre-CU box → listed commands appear and are callable.
- Prerequisites block invalid training order.

### Regression

- Default attack, NGE leftover commands you still rely on, login, and one non-combat profession action still work.

---

## 8. Common pitfalls

1. Treating combat-only fixes as the entire Pre-CU project.  
2. Assuming `combat_data.weaponType` blocks wrong weapons for hybrid rows.  
3. Core3 animation names without NGE mapping (`*_medium`, etc.).  
4. PR compare UI defaulting to upstream **SWG-Source** — force `daquorm89` base.  
5. Editing parent repo only while the real change is in **`dsrc`**.  
6. Forgetting **DataTableTool** / `.iff` sync after `.tab` edits.  
7. Forgetting **`git submodule update`** on the server after merge.  
8. Inventing git author identities — always `daquorm89 <douweheuvel@gmail.com>`.  
9. Large C++ changes without a rollback plan.  
10. Breaking NGE client assumptions (missing anims, bad datatable schema).

---

## 9. Suggested roadmap (high level)

Order is guidance, not a rigid schedule:

1. **Profession/skill grant spine** — can train Pre-CU lines and receive commands.  
2. **Combat hybrid** — abilities execute, weapons gated, basic DoTs/buffs (in progress).  
3. **Balance pass** — costs/damage/XP feel Pre-CU-like.  
4. **Jedi / Force** — powers and visibility rules.  
5. **Crafting & economy** — schematics/resources as needed for the loop.  
6. **World/loot** — support the profession loop in open world.  
7. **Engine fidelity** — only remaining gaps that data/Java cannot cover.

---

## 10. Document maintenance

- **Owner:** project lead (daquorm89).  
- **Agents:** update this file in the same PR when adding a permanent rule, phase completion, or path change.  
- **Do not** replace this with chat-only tribal knowledge.

---

*End of WORKFLOW.md*
