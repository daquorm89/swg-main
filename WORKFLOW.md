# Pre-CU Restoration Workflow

**Project:** Modify an NGE-era SWG Source server toward Pre-CU (Pre-Combat Update) **skill-based professions and combat abilities**, while keeping an NGE-compatible client and leaving stable NGE systems (loot, world, crafting, etc.) alone until needed.

**Owner:** daquorm89 (`douweheuvel@gmail.com`)  
**Runnable server tree (local):** `~/repos/swg-main/`  
**GitHub (source of truth):** [daquorm89/swg-main](https://github.com/daquorm89/swg-main) (fork of SWG-Source) with submodules `dsrc`, `src`, `serverdata`, `stationapi`, `exe`/`configs`

This file is the standing operating procedure for **humans and AI agents**. Read it before changing code, data, or skills. Prefer updating this document when process changes, rather than relying on chat history.

**Live project status (checkboxes):** see [`PROGRESS.md`](./PROGRESS.md). Update it when sub-targets are finished.

---

## 1. Project goal (current scope)

Restore **Pre-CU skill-based professions and combat presentation** on top of an NGE server stack, while **keeping NGE systems that already work** until they block Pre-CU goals.

### In scope now

| Area | Intent | Notes |
|------|--------|-------|
| **Professions / skills** | Pre-CU skill trees, boxes, XP types, titles | Not NGE expertise wheels as primary progression |
| **Commands** | Pre-CU command names, hooks, grant rules | `command_table` + scriptHooks |
| **Combat abilities** | Weapon specials, states, DoTs, posture, Jedi powers | Hybrid: `combat_data.tab` + thin Java (see §5) |
| **Combat math / balance** | **May remain NGE-based** | Allowed as long as it can *simulate* Pre-CU feel and does **not** conflict with other Pre-CU changes (abilities, states, grants, weapons) |
| **Items / weapons / armor** (as needed for professions) | Templates, certs, mods required for Pre-CU lines | Client must still load assets |
| **Jedi / Force** | Pre-CU powers / progression as targeted | Partial; Force pool may lag vigor mapping |
| **UI / client** | Must remain NGE-client compatible | No client edits unless explicitly approved |

### Explicitly out of scope for now

| Area | Policy |
|------|--------|
| **Creatures / spawns / lairs** | **Leave NGE** until further notice |
| **Loot tables** | **Leave NGE** until further notice |
| **World / planet content** | **Leave NGE** until further notice |
| **Crafting / resources / schematics** | **Leave NGE**; no issues found yet — revisit only if Pre-CU professions require it |

**Combat is one subsystem among several in-scope systems** (skills, commands, abilities). Do not treat the combat hybrid as the whole project. Do not expand into loot/world/crafting “while you’re there” without an explicit decision to put them in scope.

---

## 2. Standing rules (non-negotiable)

### 2.1 Design principles

1. **Reconnect before inventing.** Prefer dormant Pre-CU tables, scripts, and NGE columns/buffs over new frameworks.
2. **Client compatibility.** NGE client must load and play. Use NGE-safe animations, effects, and datatable schemas.
3. **Phased delivery.** Make systems *usable* first (grants fire, abilities execute, skills train), then deepen fidelity (states, tighter simulation). Exact Pre-CU combat curves are optional while NGE math can simulate the intended feel.
4. **Data-driven where possible.** Datatables and command tables first; Java only for gates, hooks, or missing engine support.
5. **No silent scope creep.** If a change touches professions + combat + loot, split into clear commits/PRs.
6. **Full paths only in docs and instructions.** Never write truncated paths such as `serverdata/.../datatables/combat/combat_data.iff`. Always give the complete path from the server root (e.g. `~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.iff`).

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
# Java (under dsrc submodule)
~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/script/systems/combat/combat_actions.java
~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/script/systems/combat/combat_base.java

# Datatable source (edit .tab under dsrc)
~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.tab

# Compiled IFF output (DataTableTool writes under data/, NOT next to the .tab)
~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.iff

# Other runtime copies that must be kept in sync after compile
~/repos/swg-main/data/sku.0/sys.server/compiled/game/datatables/combat/combat_data.iff
~/repos/swg-main/serverdata/datatables/combat/combat_data.iff

# DataTableTool
~/repos/swg-main/build/bin/DataTableTool
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

### 4.5 Items (limited)

- Touch weapon/armor/item data **only when required** for Pre-CU profession certs or ability use.
- Keep client asset paths valid.
- Do not run a general Pre-CU item conversion pass unless scoped.

### 4.6 Crafting, resources, creatures, loot, world — OUT OF SCOPE (for now)

- **Crafting / resources:** leave NGE; no known blockers yet.
- **Creatures / spawns / lairs, loot tables, world content:** leave NGE until explicitly brought in scope.
- Agents must **not** “fix” or Pre-CU-ify these while working on skills/combat unless the project lead expands scope.

### 4.7 C++ engine (`src`)

- Only when Java/data cannot express the rule (rare).
- Files: `.cpp` / `.h` under the **`src` submodule** (engine + game).
- On the server machine, rebuild with **narrow Make targets** from the CMake dir (usually `x/`):  
  `make -j$(nproc) serverGame && make -j$(nproc) SwgGameServer` (see §6.3).  
  Do **not** default to `ant compile_src` / full rebuilds.
- Restart only the processes whose binaries you relinked.
- Treat C++ as last resort; PRs should list which targets were rebuilt.

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
| **Later** | Pool-specific damage, true Force pool, posture API fidelity | Not done; only if NGE simulation is insufficient |

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
- **Engine (`src`):** only with explicit justification; rebuild with narrow `make` targets in `x/` (§6.3).

### 6.3 Build on the server machine

Always build from the **runnable** tree: `~/repos/swg-main/` (full paths only; do not invent alternate roots in instructions).

**Rule: rebuild only what you touched.** Prefer the narrowest command. Do **not** run full-tree Ant compiles (`ant compile`, `ant compile_src`) for routine one-file or one-library edits.

#### Java — one `.java` file at a time

```bash
cd ~/repos/swg-main
./utils/build_java_single.sh dsrc/sku.0/sys.server/compiled/game/script/systems/combat/combat_actions.java
```

- Pass the **full path under `dsrc`** to the single changed file.
- Repeat the command per file if several scripts changed.
- Avoid `ant compile_java` unless you intentionally want a full Java rebuild.

#### Datatables — one `.tab` (or the set you edited)

**Do not use truncated paths** (`serverdata/...`). Always write the **full path** from the server root (`~/repos/swg-main/...`).

**Required sequence after editing a `.tab`:**

1. Compile `.tab` → `.iff` with DataTableTool.
   - **Important:** the tool does **not** write next to the `.tab` under `dsrc/`.
   - It prints `SUCCESS creating data table: …` — that path is the real output, almost always under:
     `~/repos/swg-main/data/sku.0/sys.<server|shared>/compiled/game/datatables/<category>/<file>.iff`
2. Set `SRC` to **that SUCCESS path** (or the matching `data/…` path), then **copy** the new `.iff` to every other existing copy under `~/repos/swg-main` (`data/…/sys.server/…`, `serverdata/…`, etc.).
3. Restart GameServer.

**Preferred compile pattern (project standard):**

```bash
# Template — server root is always ~/repos/swg-main
cd ~/repos/swg-main/dsrc/sku.0/sys.<server|shared>/compiled/game/datatables/<category>/
~/repos/swg-main/build/bin/DataTableTool -i <file>.tab
# Read the SUCCESS line — that is SRC. Typical form:
# ~/repos/swg-main/data/sku.0/sys.<server|shared>/compiled/game/datatables/<category>/<file>.iff
```

**Concrete example — combat_data (compile + distribute .iff):**

```bash
cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/combat/
~/repos/swg-main/build/bin/DataTableTool -i combat_data.tab
# SUCCESS creating data table: /home/swg/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.iff

SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/combat/combat_data.iff

# List every existing copy
find ~/repos/swg-main -name 'combat_data.iff' -print

# Overwrite every other copy with the newly built one
find ~/repos/swg-main -name 'combat_data.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;

# Confirm timestamps match
find ~/repos/swg-main -name 'combat_data.iff' -printf '%T+ %p\n'
```

**Concrete example — command_table (shared + server sources):**

```bash
# Shared source .tab
cd ~/repos/swg-main/dsrc/sku.0/sys.shared/compiled/game/datatables/command/
~/repos/swg-main/build/bin/DataTableTool -i command_table.tab
# SUCCESS → ~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/command/command_table.iff

SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/command/command_table.iff
find ~/repos/swg-main -name 'command_table.iff' -print
find ~/repos/swg-main -name 'command_table.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;

# If you also edited the server copy of the .tab, compile it too:
cd ~/repos/swg-main/dsrc/sku.0/sys.server/compiled/game/datatables/command/
~/repos/swg-main/build/bin/DataTableTool -i command_table.tab
# SUCCESS → ~/repos/swg-main/data/sku.0/sys.server/compiled/game/datatables/command/command_table.iff
# Prefer the shared output as the single source of truth for distribution unless server-only rows differ.
SRC=~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/command/command_table.iff
find ~/repos/swg-main -name 'command_table.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;
```

Same pattern for any other table: build with `DataTableTool -i <file>.tab`, set `SRC` from the **SUCCESS** line (under `data/`), then:

```bash
find ~/repos/swg-main -name '<file>.iff' ! -path "$SRC" -exec cp -f "$SRC" {} \;
```

- Tool path: `~/repos/swg-main/build/bin/DataTableTool` (full path; do not rely on `PATH`).
- Run from the directory that contains the `.tab` under `dsrc/`.
- **Never** set `SRC` to a path under `dsrc/…/*.iff` — that file is usually not created.
- Confirm: `ls -la ~/repos/swg-main/data/sku.0/sys.shared/compiled/game/datatables/<category>/<file>.iff`
- After the `find` + `cp` pass, restart GameServer.

Prefer this over `ant compile_tab` when only one table changed.

#### C++ — narrow `make` targets (`.cpp` / `.h` under `src`)

C++ is built from the **CMake build directory**. On this project that directory is commonly named **`x`** (some stock Ant setups use `build/` instead — use whichever exists on the machine).

**Standard narrow rebuild after game/combat engine edits:**

```bash
cd ~/repos/swg-main/x    # CMake build dir
make -j$(nproc) serverGame
make -j$(nproc) SwgGameServer
```

| Target | Role |
|--------|------|
| `serverGame` | Game library / objects affected by most `src/game` and shared engine edits |
| `SwgGameServer` | GameServer binary that must be relinked after `serverGame` |

- Rebuild **only these** when a few `.cpp`/`.h` files change and those targets are sufficient.
- If you changed a different binary (LoginServer, ConnectionServer, etc.), `make -j$(nproc) <ThatTarget>` instead of rebuilding everything.
- There is no single-TU helper equivalent to `build_java_single.sh`; Make still compiles dirty objects, but **do not** default to rebuilding every server target.
- Restart **GameServer** (and only other processes whose binaries you relinked) so the new binary is loaded.

**When the CMake tree is missing or stale** (first setup, clean, or generator change), configure once, then use narrow makes again:

```bash
cd ~/repos/swg-main
ant prepare_src_x86   # or prepare_src on non-x86; creates/updates the CMake build dir
cd x                  # or build/ if that is your cmake output dir
make -j$(nproc) serverGame
make -j$(nproc) SwgGameServer
```

**Avoid for routine work:** `ant compile_src` and `ant compile` (full C++ / full stack). Reserve them for intentional full rebuilds only.

#### Station/chat C++

Only if `stationapi` sources changed — use that project’s narrow build (or `ant compile_chat` only when necessary). Not part of normal Pre-CU skill/combat iteration.

### 6.4 Git publish

1. Commit in the correct repo (usually **`dsrc`**).
2. Push feature branch; open PR vs **`daquorm89/...` `master`**.
3. If needed, bump submodule pointer on **`swg-main`** in a second PR.
4. After merge: pull + submodule update on **server**, rebuild, restart, smoke-test.

### 6.5 Definition of done

- [ ] Feature branch + PR on correct fork/base  
- [ ] Merged to master (submodule then parent if both)  
- [ ] Server tree updated and **narrowly** rebuilt (Java single-file / DataTableTool / `make serverGame`+`SwgGameServer` as appropriate — not full-tree Ant)  
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
6. Forgetting **DataTableTool** after `.tab` edits, setting `SRC` to a non-existent `dsrc/…/*.iff` path (tool writes under `data/…`), or compiling but **not copying** the new `.iff` to every existing copy under `~/repos/swg-main`. Always use the SUCCESS path as `SRC`.  
7. Giving truncated paths (`serverdata/.../file.iff`) in docs or agent instructions — always full paths from the server root.  
8. Forgetting **`git submodule update`** on the server after merge.  
9. Inventing git author identities — always `daquorm89 <douweheuvel@gmail.com>`.  
10. Large C++ changes without a rollback plan.  
11. Editing `.cpp`/`.h` but only rebuilding Java — run `make … serverGame` and `SwgGameServer` in the CMake dir (`x/`), then restart GameServer.  
12. Using full `ant compile` / `ant compile_src` for a one-file change — wasteful and unnecessary when narrow targets exist.  
13. Breaking NGE client assumptions (missing anims, bad datatable schema).

---

## 9. Suggested roadmap (high level)

Order is guidance, not a rigid schedule. Items marked *deferred* stay NGE until scope expands:

1. **Profession/skill grant spine** — train Pre-CU lines and receive commands.  
2. **Combat hybrid** — abilities execute, weapons gated, basic DoTs/buffs (in progress).  
3. **Combat feel pass** — tune costs/damage/states so Pre-CU abilities feel right **without requiring pure Pre-CU math** if NGE math already works.  
4. **Jedi / Force** — powers and visibility rules as needed.  
5. **Items/certs only as required** by professions.  
6. *Deferred:* crafting, resources, creatures, loot, world content.  
7. *Last resort:* C++ engine changes for gaps data/Java cannot cover.

---

## 10. Document maintenance

- **Owner:** project lead (daquorm89).  
- **Agents:** update this file in the same PR when adding a permanent rule, phase completion, or path change.  
- **Do not** replace this with chat-only tribal knowledge.

---

*End of WORKFLOW.md*
