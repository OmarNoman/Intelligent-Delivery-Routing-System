# Intelligent Delivery Routing System

A cargo delivery routing simulation that finds optimal paths across a Melbourne
suburb road network, reroutes when road conditions change, and adjusts vehicle
speed limits based on road segments and cargo fragility using a fuzzy inference
system.

Originally built as a university assignment (SIT215 Computational Intelligence);
this repo restructures it into a proper Python package.

---

## Prerequisites

### Python Version
- **Python 3.10 or higher** is required.

### Required Libraries

Install all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

| Library | Version (tested) | Purpose |
|---|---|---|
| `haversine` | ≥ 2.8.0 | Geodesic distance computation (Haversine formula) |
| `matplotlib` | ≥ 3.5.0 | Route maps, bar charts, MF plots, and control surfaces |
| `numpy` | ≥ 1.21.0 | Numeric array operations for FIS universe and plots |
| `scipy` | ≥ 1.7.0 | Required by scikit-fuzzy for mathematical operations |
| `networkx` | ≥ 2.6.0 | Required by scikit-fuzzy control system internals |
| `scikit-fuzzy` | ≥ 0.4.2 | Fuzzy membership functions, rule base, and defuzzification |
| `pydantic-settings` | ≥ 2.0.0 | Config layer (`app/config.py`), env/`.env`-overridable settings |
| `heapq` | stdlib | Priority queue for A* and UCS frontiers |
| `math` | stdlib | `ceil()` for replanning trigger calculation |
| `random` | stdlib | Reproducible constrained edge selection (seed = 42) |
| `time` | stdlib | Wall-clock timing for search performance |

---

## How to Run

Run from the repo root, either:

```bash
python Main.py
```

or:

```bash
python -m scripts.run_demo
```

Both are equivalent; `Main.py` is a thin compatibility shim around
`scripts/run_demo.py`. **Running `python scripts/run_demo.py` directly does
not work** (the repo root would not be on `sys.path`, so `app.*` imports fail),
so always run from the repo root using one of the two forms above.

Route, cargo fragility levels, constraint fraction, and replan trigger
fraction are configurable via environment variables (or a `.env` file) using
the `IDRS_` prefix, e.g. `IDRS_START_NODE=3 python Main.py`. See
`app/config.py` for the full list of settings and their defaults.

> **Note:** Each matplotlib window must be closed before the next one appears.
> On headless servers, set `MPLBACKEND=Agg` before running to save figures to
> files instead of displaying them interactively.

---

## Expected Output

Running the script produces the following outputs in order:

### 1. Task 1 – Baseline A* Planner (printed to console)

```
=================================================================
TASK 1 — BASELINE TIME-BASED A* PLANNER
=================================================================
  Route : Hoppers Crossing → Ferntree Gully
  Speed : 100 km/h (constant, no FIS)

  Admissibility check (h = Haversine / max_speed ≤ h*):
  -> Heuristic is ADMISSIBLE over all reachable nodes

  Algorithm            Path cost (h)    Nodes exp.   Time (ms)
  ------------------------------------------------------------
  UCS (baseline)       0.6011           ...          ...
  A* (Haversine)       0.6011           ...          ...

  Optimal path (36.1 min):
    Hoppers Crossing -> Truganina -> Sunshine -> ...-> Ferntree Gully
```

### 2. Task 1 – Visualisation Window (matplotlib pop-up)

- **Route map** showing the optimal A* baseline path overlaid on the Melbourne
  delivery environment (21 nodes, 36 road segments).

### 3. Task 2 – FIS Membership Function Plots (matplotlib pop-up)

- Three-panel figure showing triangular membership functions for:
  - **Fragility** (Robust / Moderate / Fragile) with overlap shading and worked-example input marker
  - **Bumpiness** (Smooth / Moderate / Rough) with overlap shading and worked-example input marker
  - **Max Safe Speed** (Slow / Medium / Fast) with overlap shading

### 4. Task 2 – Worked Example (printed to console + matplotlib pop-up)

```
=================================================================
TASK 2 — WORKED EXAMPLE
=================================================================
  Cargo fragility : 5.0  ->  μ_Moderate = 1.000
  Road bumpiness  : 7.0  ->  μ_Moderate = 0.333, μ_Rough = 0.250

  Active rules (partial activation = genuine ambiguity):
    Rule 5  Moderate & Moderate -> Medium : min(1.000, 0.333) = 0.333
    Rule 6  Moderate & Rough   -> Slow   : min(1.000, 0.250) = 0.250

  Defuzzification (centroid) -> Max Safe Speed = 67.20 km/h
=================================================================
```

- **Defuzzification plot** showing aggregated output MF region and centroid value.

### 5. Task 2 – FIS Control Surface (matplotlib pop-up)

- **3D surface plot** of Max Safe Speed across the full Fragility × Bumpiness input space.
- **2D contour map** with Task 3 fragility-level markers (F = 2, 5, 8) overlaid.

### 6. Task 3 – Integration Comparison Table (printed to console)

```
=================================================================
TASK 3 — INTEGRATION AND COMPARISON
=================================================================
  Route  : Hoppers Crossing → Ferntree Gully
  Constraint fraction : 60% of edges capped at 40 km/h  (seed=42)
  22 of 36 edges constrained

  Fragility   Level   Scenario               Time (h)    Time (min)   Nodes exp.
  ------------------------------------------------------------------------------
  2           Low     A — No constraint      ...         ...          ...
  2           Low     B — 60% constrained    ...         ...          ...
  2           Low     C — Replan @...        ...         ...          ...
  ...
```

### 7. Task 3 – Route Maps (matplotlib pop-ups, one per fragility level)

- **Side-by-side map** for each fragility level (Low / Medium / High):
  - Left panel: Scenario A (FIS speeds, no constraints)
  - Right panel: Scenario B (60 % edges capped at 40 km/h)
  - Constrained edges shown in red dashed; optimal path highlighted in orange.

### 8. Task 3 – Comparison Bar Chart (matplotlib pop-up)

- Two-panel bar chart comparing all three scenarios (A / B / C) across all three
  fragility levels on:
  - **Travel Time (minutes)** – route efficiency
  - **Nodes Expanded** – search effort

---

## Code Structure Summary

```
data/network.json                landmarks, edges, bumpiness, blocked pairs (was Python dict literals)

app/
  config.py                      pydantic-settings Settings: route, speeds, constraint/replan fractions
  models/
    network.py                    Node, Edge, RoadNetwork (graph build/load/query, haversine)
    cargo.py                       CargoProfile (fragility value + label)
  fuzzy/
    membership.py                  MF universes + triangular MF params, single source of truth
    rules.py                        the 9-rule table as data, plus a builder for skfuzzy Rules
    controller.py                   FuzzySpeedController: builds the skfuzzy ControlSystem, get_safe_speed()
    explainability.py               pure worked-example trace computation (no print/plot side effects)
  routing/
    heuristics.py                   haversine_time_heuristic (admissible A* heuristic)
    search.py                        astar_time, ucs_time
    planning.py                       apply_constraints, path_time
    replanning.py                     simulate_replanning (deterministic checkpoint replan)
  services/
    routing_service.py             RoutingService facade composing network + FIS + routing + config

scripts/
  plotting.py                     all matplotlib functions (route maps, MF plots, control surface, ...)
  run_demo.py                       orchestrates Task 1 (baseline A*/UCS), Task 2 (FIS demo),
                                     Task 3 (integration: constraint scenarios + replanning), see main()

Main.py                          thin compatibility shim: `python Main.py` calls scripts.run_demo.main()
requirements.txt                 pinned dependency manifest
```

**Entry point** (`scripts/run_demo.py`):
```python
settings = get_settings()
network  = RoadNetwork.from_json(settings.network_data_path)
fis      = FuzzySpeedController()
service  = RoutingService(network, fis, settings)
# Task 1: service.astar_time(), service.ucs_time(), plot_task1_route()
# Task 2: plot_membership_functions(), explain_worked_example(), plot_worked_example(), plot_control_surface()
# Task 3: service.compute_segment_speeds(), service.simulate_replanning(), plot_task3_comparison()
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'skfuzzy'`**
```bash
pip install scikit-fuzzy
```

**`ModuleNotFoundError: No module named 'scipy'`**
```bash
pip install scipy
```

**`ModuleNotFoundError: No module named 'networkx'`**
```bash
pip install networkx
```

**`ModuleNotFoundError: No module named 'haversine'`**
```bash
pip install haversine
```

**`ModuleNotFoundError: No module named 'pydantic_settings'`**
```bash
pip install pydantic-settings
```

**Matplotlib windows do not appear:**
Ensure a display environment is available. On headless servers, add the following
before running:
```python
import matplotlib
matplotlib.use('Agg')  # Save to file instead of displaying
```

**`FIS compute() raises an exception for certain input values:`**
Ensure all fragility and bumpiness values lie within [0, 10]. `get_safe_speed()`
automatically clips inputs to [0.01, 9.99] to avoid boundary singularities in
scikit-fuzzy; it has no other error handling, so values outside [0, 10] are not
validated before clipping.

**Python version errors:**
Confirm Python 3.10+:
```bash
python --version
```

---

## Notes on Implementation

### Environment
- The road network reuses the 21-node, 36-edge Melbourne graph from Assignment 1.
- **Static constraint** (weight-restricted bridges on edges 19↔11 and 3↔9) is always
  active and removes those edges from the search entirely.
- Bumpiness values are fixed by road type and geography (inner-city: 2.0–3.0,
  middle-ring: 4.0–5.5, outer suburban: 6.0–7.5) and do not change at runtime.

### FIS Design
- Inputs: **Fragility** [0–10] and **Bumpiness** [0–10], each with three triangular MFs.
- Output: **Max Safe Speed** [40–100] km/h, three triangular MFs.
- Rule base: 9 rules covering all 3 × 3 input combinations; the Moderate fragility row
  deliberately produces distinct outputs from both the Robust and Fragile rows.
- Defuzzification method: centroid.

### Task 3 Constraints
- **60 % of edges** are capped at 40 km/h using `random.seed(42)` for reproducibility.
- This seed is fixed and reused consistently across all three fragility levels.
- **Replanning** is triggered after `ceil(0.20 × path_length)` nodes are visited; the
  agent replans from the current node (not from the start) using the constrained speed map.
