# P9 — Atmospheric Starship Flight

Status: PROPOSED (not started). For review before any code changes.
Repos touched: `swg-main` (`src`, `dsrc`, `serverdata` submodules) + `client-tools`.

---

## 1. Why this is possible at all

The entire reason ships can't be flown/boarded/exited on a ground planet today is a
single gate, duplicated identically on server and client:

```cpp
// client-tools: clientGame/Game.cpp
ms_isSpace = isSpaceSceneName(ms_sceneId);      // true only if sceneId starts with "space_"
ClientCommandTable::load();                      // loads *_ground.iff OR *_space.iff

// swg-main: serverGame/ServerCommandTable.cpp
if (!strncmp(ConfigServerGame::getSceneID(), "space_", 6))
    load command_tables_shared_space.iff + command_tables_server_space.iff
else
    load command_tables_shared_ground.iff + command_tables_server_ground.iff
```

`pilotShip`, `unpilotShip`, `leaveStation` (and the rest of ship flight/combat
commands) are defined **only** in `command_table_space.tab`. On a ground planet
process, those commands are never registered — the radial menu option can't exist
because the command itself doesn't exist server-side.

Everything underneath that gate is already scene-agnostic:

- `CreatureObject::pilotShip()` / `unpilotShip()` (`CreatureObject_Ships.cpp`) only
  check `ConfigServerGame::getShipsEnabled()` and `isInWorldCell()` — no scene check.
- `space_transition.unpackShipForPlayer()` (the datapad "call ship" flow) places the
  ship at the player's current position and pilots them — no scene check.
- Ship movement is **client-authoritative**: `PlayerShipController::receiveTransform()`
  on the server just accepts the transform the client sends
  (`ShipUpdateTransformMessage`). This is exactly the same trust model space flight
  uses today — flying on a planet doesn't change the movement architecture, it just
  means terrain now exists where before there was none.
- POB ship interiors (`ship_interior.java`, `ship_cell_manager.java`,
  `shipcontrol_falcon.java`) and pilot/gunner/operations slots are already generic,
  not written to assume a space scene.
- `TerrainObject::getHeight()` / `getWaterHeight()` (`sharedTerrain`) give us
  everything needed for ground-contact detection, landing, and an altitude-based
  space transition.

So this is a genuine "some of it is already there" situation, as you suspected —
it's a config/datatable + missing-collision problem, not a rewrite of the flight
model.

## 2. What actually has to be built

1. **Command availability on the ground.** Add `pilotShip`, `unpilotShip`,
   `leaveStation`, and related ship commands to the ground command tables (server +
   client, shared), so the commands exist as valid script/radial targets outside
   space scenes.
2. **A per-planet allow-list.** Nothing like this exists today — every "is this
   scene space" check is the `space_` prefix. We need a new, explicit
   `atmospheric_flight_planets.tab` (or a flag column on the existing planet table)
   so Kashyyyk etc. can be excluded cleanly, checked once at ship-call/board time.
3. **Ship-vs-terrain collision & landing.** Never needed in space, doesn't exist.
   Minimum viable version: each flight tick, sample `TerrainObject::getHeight()`
   under the ship; if the ship's belly is at/below ground and vertical speed is
   at/below a small threshold, snap to "landed" state (zero out engine thrust,
   allow exit). If speed is high or angle is steep, treat as a collision (existing
   `ShipController::respondToCollision()` path) rather than a landing.
4. **Boarding/exit state machine on the ground.** Radial menu additions:
   - On a landed, stationary ship → "Board / Pilot" (and "Enter Interior" for POB
     hulls) for players nearby.
   - On a ship you're piloting, landed and stationary → "Exit Ship" (mirrors the
     existing space `leaveStation` flow, just callable from ground).
   - Passenger seats inside a POB ship interior on the ground → same exit rules as
     the ship's own interior cells already use.
   Piloting while airborne must not offer "Exit Ship" — reuse/extend the existing
   speed/state check `leaveStation` already does in space (need to confirm it checks
   velocity — if not, add the check).
5. **Radial menu for "call ship" on ground.** `ship_control_device.java`'s
   `OnObjectMenuRequest` already offers "Retrieve"/store on the ground (it's not
   scene-gated); we mainly need to confirm `unpackShipForPlayer()` respects the new
   planet allow-list before placing a live, pilotable ship on an excluded planet.
6. **Bonus: altitude → space transition.** New logic: while piloting on a ground
   scene, if altitude above terrain exceeds a per-planet threshold, trigger the
   existing scene-transfer plumbing (`space_transition`'s scene-change path) into
   that planet's `space_<planet>` scene, preserving the ship's velocity vector and
   the pilot/gunner/passenger manifest. This is new trigger logic wrapped around an
   existing transition mechanism, not a new transition mechanism.
7. **Client visuals/UX.** Confirm ship appearances render correctly outside the
   space skybox/lighting rig (`ShadowManager::setAllowed(!ms_isSpace)` currently
   disables shadows in space — on the ground we want shadows ON for a landed/flying
   ship, which happens automatically since `ms_isSpace` will correctly be `false`
   there; just needs a smoke test). Flight HUD/reticle (`SwgCuiShipReticle`) needs
   to still function when `Game::isSpace() == false`, since several UI paths key off
   that flag — needs an audit, not necessarily a rewrite.

## 2a. Major discovery: ship-vs-terrain collision already exists, just disabled

While tracing the collision path, found that SOE already built a full ship-vs-terrain
collision system — it's just never turned on:

```cpp
// swg-main/src/.../CollisionCallbacks.cpp, CollisionCallbacks::install()
//CollisionCallbackManager::registerDoCollisionWithTerrainFunction(CollisionCallbacksNamespace::onDoCollisionWithTerrain);
```

That single commented-out line is the entire gate. Once registered:
- `CollisionWorld::spatialSweepAndResolve()` — the same generic per-object collision
  loop already used for ship-vs-ship/asteroid collision — calls
  `doCollisionWithTerrain(object)` **every physics frame for every collidable
  object**, no extra wiring needed.
- `CollisionCallbackManager::intersectAndReflectWithTerrain()` does a real capsule-
  vs-terrain sweep against `TerrainObject`, returning point of impact and surface
  normal — genuinely implemented, not a stub.
- It calls into `ShipController::respondToCollision()`, which moves the ship back to
  the point of impact and reflects its velocity off the surface normal — again fully
  implemented.

**Why it's still not usable as-is:** `respondToCollision()` unconditionally bounces —
there's no concept of "landing." Turning this on with zero other changes would make a
ship bounce off the ground like a rubber ball instead of settling. That's almost
certainly why it was left disabled/unfinished — this is very likely SOE's own
abandoned prototype of this exact feature. `PlayerShipController::experiencedCollision()`
also does no damage — it just resyncs the client after a bounce.

**Revised design given your decisions (multi-point landing check, real damage above a
speed threshold):**

1. Register the terrain collision callback (uncomment the one line) — gated behind
   `ConfigServerGame::getAllowAtmosphericFlight()` so it stays off entirely if the
   feature is disabled.
2. Add a new `ShipController::checkLanding()` step, run once per tick when a ship's
   vertical speed is below a small threshold and it's near the ground (cheap early-out
   otherwise). It samples `TerrainObject::getHeight()` at several points around the
   hull footprint (not just the single movement-sweep capsule used for the bounce
   check) — this is the "multi-point, steeper/slower" check you asked for:
   - If all sample points are within a small height tolerance of each other (flat
     enough) **and** ship speed is below the landing-speed threshold **and** descent
     angle is close to vertical → snap to "landed" state: zero velocity, mark
     `isLanded = true`, allow `unpilotShip`/exit.
   - If the multi-point check fails (too steep, moving sideways too fast, or an
     obstruction under one of the sample points) → do **not** land; fall through to
     the existing `respondToCollision()` bounce path instead, so the pilot has to
     find a clearer/flatter spot.
3. In `onDoCollisionWithTerrain` (server), add a speed check before calling
   `respondToCollision()`: below the damage threshold, bounce with no damage (soft
   landing-attempt-failed feel); above it, apply the same armor/hp damage pathway
   used for ship-to-ship ramming (exact function to confirm while implementing —
   `PlayerShipController::experiencedCollision()` is the natural hook point since
   it already fires on every terrain/ship collision and already has the `ShipObject`
   handle).
4. Both thresholds (landing speed, damage speed) become `ConfigServerGame` values
   rather than hardcoded, so they're tunable without a rebuild.

## 3. Decisions (confirmed)

- **Landing precision:** multi-point terrain check (steeper/faster approaches are
  rejected; slow, flat-enough contact lands). ✅
- **Collision severity:** real collision response, but hull/armor damage only applies
  above a speed threshold — low-speed terrain contact that fails the landing check
  just bounces/stops with no damage. ✅
- **Excluded planets:** Kashyyyk (all instance variants) + other instance/POI-only
  scenes (Mustafar, adventure/dungeon instances, the tutorial). Open-world planets
  (Corellia, Dantooine, Dathomir, Endor, Lok, Naboo, Rori, Talus, Tatooine, Yavin4)
  allowed. ✅ — encoded in `atmospheric_flight_planets.tab` (already committed, see
  §7).
- **Space-transition altitude:** per-planet column in the same datatable, all
  currently defaulted to a flat 3000m so it's easy to tune per planet later without
  a schema change.

## 4. Rollout / revert strategy

- Everything lands in a single feature branch per repo:
  `feature/atmospheric-flight` in both `swg-main` and `client-tools`.
- The entire feature is additive at the datatable level (new rows/tables, not edits
  to existing space-only rows) and gated by the new planet allow-list, so:
  - Reverting = revert the branch merge (or just don't merge it) — nothing about
    existing space flight, ground movement, or vehicle mechanics is touched.
  - As an extra safety net I'll add a single `ConfigServerGame` bool
    (`allowAtmosphericFlight`, default `true` once merged, settable to `false` in
    server config with no code change) so you can kill it live without a rebuild if
    something's wrong in production, before deciding whether to revert outright.
- Server and client changes are committed separately (separate repos/PRs) but under
  matching branch names, per your existing shared-file convention in
  `client-tools/WORKFLOW.md` §2.

## 5. File-level change list (for the PR, once approved)

**swg-main / dsrc (datatables + scripts):**
- `dsrc/.../datatables/command/command_table_ground.tab` — add flight command rows.
- new: `dsrc/.../datatables/space/atmospheric_flight_planets.tab` — planet allow-list
  + altitude threshold column.
- `dsrc/.../script/space/ship_control_device/ship_control_device.java` — check
  allow-list before offering "Retrieve" on an excluded planet.
- `dsrc/.../script/library/space_transition.java` — new altitude-trigger entry point
  that calls the existing scene-change function.
- `dsrc/.../script/space/combat/combat_ship_player.java` — extend boarding/leaving
  checks to run on ground scenes too (currently implicitly space-only because the
  commands didn't exist there).

**swg-main / src (engine):**
- `serverGame/ConfigServerGame.h/.cpp` — add `allowAtmosphericFlight` bool.
- `serverGame/controller/ShipController.cpp` / `PlayerShipController.cpp` — add
  terrain-height sampling, landed-state detection, soft-stop-on-collision path.
- `serverGame/command/ServerCommandTable.cpp` — no change needed if step above
  (datatable) is sufficient; will confirm during implementation.

**client-tools / src (engine):**
- `clientGame/command/ClientCommandTable.cpp` — no change needed (already table-
  driven); ground command table additions are enough.
- `clientGame/core/Game.cpp` — audit only, likely no change (`ms_isSpace` logic
  stays correct as-is).
- `swgClientUserInterface/.../SwgCuiShipReticle.cpp` — audit/adjust HUD activation
  to not assume `Game::isSpace()`.

**serverdata submodule:**
- compiled `.iff` outputs regenerated from the `dsrc` `.tab` edits above (build step,
  not hand-edited).

## 6. Suggested implementation order (so each commit is independently testable)

1. Ground command table entries + `ConfigServerGame::allowAtmosphericFlight` flag
   (server can now board/pilot/exit on the ground; test near a starport with a ship
   already sitting there).
2. Terrain landing/collision handling (fly around, land, confirm no clipping-through-
   mountain issues at low speed).
3. Planet allow-list + ship_control_device gating (confirm Kashyyyk refuses).
4. Client HUD/reticle audit + any needed fixes.
5. Bonus: altitude → space transition trigger.

Each step above = one commit on the feature branch, so you can bisect/revert to any
point if something regresses.

---

## 7. Progress log

Branch `feature/atmospheric-flight` created in `dsrc`, `src`, and `swg-main`.

- **Commit 1 (dsrc + src, done):**
  - `ConfigServerGame::allowAtmosphericFlight` bool flag (default `true`), the kill
    switch from §4.
  - Ground command table (`command_table_ground.tab`, shared by server + client
    builds) gained `pilotShip`, `unpilotShip`, `leaveStation`, `openWings`,
    `closeWings`, `boosterOn`, `boosterOff`, `escapePod`, `kickFromShip`, copied
    verbatim from the space command table so their behavior flags match exactly.
    (Space-combat-only commands — weapons, shields, hyperspace, etc. — deliberately
    left out; not in scope for atmospheric flight.)
  - New `atmospheric_flight_planets.tab` (planet allow-list + per-planet space-
    transition altitude), per the confirmed decisions in §3.
- **Not yet committed — next up (commit 2, `src` only):**
  - Register `CollisionCallbacks::onDoCollisionWithTerrain` (currently commented
    out), gated behind `ConfigServerGame::getAllowAtmosphericFlight()`.
  - `ShipController::checkLanding()` multi-point terrain sampling + landed-state
    flag.
  - Speed-gated damage in the terrain collision path.
  - New tunables: landing-speed threshold, damage-speed threshold.
- **Commit 3 (dsrc):** `ship_control_device.java` planet allow-list check before
  "Retrieve" on the ground; `combat_ship_player.java` board/exit checks extended to
  ground scenes (exit only offered when `isLanded` is true).
- **Commit 4 (client-tools):** HUD/reticle audit for `Game::isSpace() == false`
  flight; smoke-test shadows/lighting on a landed/flying ship.
- **Commit 5 (dsrc):** altitude → space-scene transition trigger, reusing the
  existing `TRIG_ABOUT_TO_LAUNCH_TO_SPACE`-style transition plumbing.

I'll do commit 2 next — it's the biggest, most technical piece (real C++ physics/
collision code I can't compile-test in this environment), so I'll post the exact
diff for your review before pushing, rather than pushing silently.
