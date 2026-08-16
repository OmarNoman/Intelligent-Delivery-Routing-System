import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz

from app.fuzzy.controller import FuzzySpeedController
from app.fuzzy.explainability import WorkedExampleResult
from app.fuzzy.membership import (
    BUMPINESS_MFS,
    BUMPINESS_UNIVERSE,
    FRAGILITY_MFS,
    FRAGILITY_UNIVERSE,
    SPEED_MFS,
    SPEED_UNIVERSE,
)
from app.models.cargo import CargoProfile
from app.models.network import RoadNetwork


def path_label(network: RoadNetwork, path: list) -> str:
    if path is None:
        return "No path found"
    return " -> ".join(network.nodes[n].name for n in path)


def _draw_map_on_ax(ax, network: RoadNetwork, path: list, constrained_edges: set, title: str,
                     start_node: int, goal_node: int) -> None:
    drawn = set()
    for u, nbrs in network.graph.items():
        for v, _ in nbrs:
            ef = frozenset({u, v})
            if ef in drawn:
                continue
            drawn.add(ef)
            ux, uy = network.nodes[u].lon, network.nodes[u].lat
            vx, vy = network.nodes[v].lon, network.nodes[v].lat
            is_con = ef in constrained_edges
            col = "#E74C3C" if is_con else "#BDC3C7"
            ax.plot([ux, vx], [uy, vy], color=col, lw=2.0 if is_con else 1.2,
                    ls="--" if is_con else "-", zorder=1)

    if path:
        for i in range(len(path) - 1):
            ux, uy = network.nodes[path[i]].lon, network.nodes[path[i]].lat
            vx, vy = network.nodes[path[i + 1]].lon, network.nodes[path[i + 1]].lat
            ax.plot([ux, vx], [uy, vy], color="#F39C12", lw=5, alpha=0.85, zorder=2)

    for nid, node in network.nodes.items():
        c = "#27AE60" if nid in (start_node, goal_node) else "#3498DB"
        ax.scatter(node.lon, node.lat, s=90, c=c, zorder=3, edgecolors="white")
        ax.text(node.lon, node.lat + 0.005, node.name, fontsize=6.5, ha="center")

    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.set_aspect("equal", adjustable="datalim")

    legend = [
        mlines.Line2D([], [], color="#BDC3C7", lw=1.5, label="Normal road"),
        mlines.Line2D([], [], color="#E74C3C", lw=2, ls="--", label="Constrained (40 km/h)"),
        mlines.Line2D([], [], color="#F39C12", lw=5, label="Optimal route"),
    ]
    ax.legend(handles=legend, fontsize=7, loc="lower right")


def plot_baseline_route(network: RoadNetwork, path: list, time_h: float, start_node: int, goal_node: int) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.suptitle("Baseline A* Route (100 km/h constant speed)", fontsize=13, fontweight="bold")
    _draw_map_on_ax(ax, network, path, set(),
                     f"{network.nodes[start_node].name} -> {network.nodes[goal_node].name}  |  {time_h * 60:.1f} min",
                     start_node, goal_node)
    plt.tight_layout()
    plt.show()


def plot_route_map(network: RoadNetwork, results: list, fragility: int, constrained_edges: set,
                    start_node: int, goal_node: int) -> None:
    frag_lbl = CargoProfile.from_fragility(fragility).label
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle(f"Route Map  (Fragility = {fragility}, {frag_lbl})", fontsize=14, fontweight="bold")

    for ax, sc_prefix in zip(axes, ["A -", "B -"]):
        row = next((r for r in results if r["fragility"] == fragility and r["scenario"].startswith(sc_prefix)), None)
        path = row["path"] if row else []
        t_h = row["time_h"] if row else float("nan")
        sc_name = row["scenario"] if row else sc_prefix
        _draw_map_on_ax(ax, network, path, constrained_edges, f"Scenario {sc_name[:25]}...  |  {t_h * 60:.1f} min",
                         start_node, goal_node)

    plt.tight_layout(pad=2.0)
    plt.show()


def plot_scenario_comparison(results: list, fragility_levels: list) -> None:
    scenarios = ["A - No constraint", "B - Replan", "C - 60% constrained"]
    colors = ["#2ECC71", "#3498DB", "#E74C3C"]
    frag_label = {2: "Low (F=2)", 5: "Med (F=5)", 8: "High (F=8)"}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Algorithm Comparison Across Fragility Levels", fontsize=13, fontweight="bold")
    x = np.arange(len(fragility_levels))
    w = 0.25
    x_lbl = [frag_label[f] for f in fragility_levels]

    for ax_idx, key, title, ylabel in [(0, "time_h", "Travel Time by Scenario", "Travel Time (minutes)"),
                                        (1, "nodes_exp", "Search Effort by Scenario", "Nodes Expanded")]:
        for sc, col, offset in zip(scenarios, colors, [-w, 0, w]):
            vals = []
            for frag in fragility_levels:
                row = next((r for r in results if r["fragility"] == frag and r["scenario"].startswith(sc[:4])), None)
                val = row[key] if row else 0
                vals.append(val * 60 if key == "time_h" else val)
            bars = axes[ax_idx].bar(x + offset, vals, w, label=sc, color=col, alpha=0.85)
            for bar, v in zip(bars, vals):
                fmt = f"{v:.1f}" if key == "time_h" else str(int(v))
                axes[ax_idx].text(bar.get_x() + bar.get_width() / 2,
                                   bar.get_height() + (0.3 if key == "time_h" else 0.1),
                                   fmt, ha="center", va="bottom", fontsize=8, fontweight="bold")

        axes[ax_idx].set_xticks(x)
        axes[ax_idx].set_xticklabels(x_lbl)
        axes[ax_idx].set_ylabel(ylabel)
        axes[ax_idx].set_title(title)
        axes[ax_idx].legend(fontsize=8)
        axes[ax_idx].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_membership_functions() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Fuzzy Membership Functions", fontsize=14, fontweight="bold")

    # Fragility
    ax = axes[0]
    u = FRAGILITY_UNIVERSE
    ax.plot(u, fuzz.trimf(u, FRAGILITY_MFS["robust"]), "b-", lw=2, label="Robust")
    ax.plot(u, fuzz.trimf(u, FRAGILITY_MFS["moderate"]), "g-", lw=2, label="Moderate")
    ax.plot(u, fuzz.trimf(u, FRAGILITY_MFS["fragile"]), "r-", lw=2, label="Fragile")
    ax.axvspan(2, 4, alpha=0.13, color="purple", label="Robust–Mod overlap [2,4]")
    ax.axvspan(6, 8, alpha=0.13, color="orange", label="Mod–Fragile overlap [6,8]")
    ax.axvline(5, color="k", lw=1.5, ls="--", label="Example input: 5")
    ax.set_title("Fragility (cargo)", fontweight="bold")
    ax.set_xlabel("Fragility score (0 = robust, 10 = fragile)")
    ax.set_ylabel("Membership degree μ")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_ylim(-0.05, 1.1)
    ax.grid(True, alpha=0.3)

    # Bumpiness
    ax = axes[1]
    u = BUMPINESS_UNIVERSE
    ax.plot(u, fuzz.trimf(u, BUMPINESS_MFS["smooth"]), "b-", lw=2, label="Smooth")
    ax.plot(u, fuzz.trimf(u, BUMPINESS_MFS["moderate"]), "g-", lw=2, label="Moderate")
    ax.plot(u, fuzz.trimf(u, BUMPINESS_MFS["rough"]), "r-", lw=2, label="Rough")
    ax.axvspan(2, 4, alpha=0.13, color="purple", label="Smooth–Mod overlap [2,4]")
    ax.axvspan(6, 8, alpha=0.13, color="orange", label="Mod–Rough overlap [6,8]")
    ax.axvline(7, color="k", lw=1.5, ls="--", label="Example input: 7")
    ax.set_title("Bumpiness (road segment)", fontweight="bold")
    ax.set_xlabel("Bumpiness score (0 = smooth, 10 = rough)")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_ylim(-0.05, 1.1)
    ax.grid(True, alpha=0.3)

    # Max Safe Speed
    ax = axes[2]
    u = SPEED_UNIVERSE
    ax.plot(u, fuzz.trimf(u, SPEED_MFS["slow"]), "r-", lw=2, label="Slow")
    ax.plot(u, fuzz.trimf(u, SPEED_MFS["medium"]), "g-", lw=2, label="Medium")
    ax.plot(u, fuzz.trimf(u, SPEED_MFS["fast"]), "b-", lw=2, label="Fast")
    ax.axvspan(50, 65, alpha=0.13, color="orange", label="Slow–Med overlap [50,65]")
    ax.axvspan(75, 95, alpha=0.13, color="purple", label="Med–Fast overlap [75,95]")
    ax.set_title("Max Safe Speed (output)", fontweight="bold")
    ax.set_xlabel("Speed (km/h)")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_ylim(-0.05, 1.1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_control_surface(controller: FuzzySpeedController) -> None:
    res = 30
    f_vals = np.linspace(0.1, 9.9, res)
    b_vals = np.linspace(0.1, 9.9, res)
    Z = np.zeros((res, res))

    for i, f in enumerate(f_vals):
        for j, b in enumerate(b_vals):
            Z[i, j] = controller.get_safe_speed(f, b)

    F, B = np.meshgrid(f_vals, b_vals)

    fig = plt.figure(figsize=(8, 6))
    fig.suptitle("FIS Control Surface", fontsize=13, fontweight="bold")
    ax2 = fig.add_subplot(111)
    cp = ax2.contourf(F, B, Z.T, levels=20, cmap="RdYlGn")
    ax2.contour(F, B, Z.T, levels=10, colors="k", linewidths=0.4, alpha=0.4)
    fig.colorbar(cp, ax=ax2, label="Max Speed (km/h)")

    for fval, lbl, col in [(2, "Low (F=2)", "blue"),
                           (5, "Med (F=5)", "black"),
                           (8, "High (F=8)", "red")]:
        ax2.axvline(fval, color=col, lw=1.8, ls="--", label=lbl)

    ax2.legend(fontsize=8, loc="lower right", title="Fragility levels")
    ax2.set_xlabel("Fragility")
    ax2.set_ylabel("Bumpiness")
    ax2.set_title("2D Contour Map")
    plt.tight_layout()
    plt.show()


def plot_worked_example(result: WorkedExampleResult) -> None:
    u_spd = SPEED_UNIVERSE
    slow_mf = fuzz.trimf(u_spd, SPEED_MFS["slow"])
    medium_mf = fuzz.trimf(u_spd, SPEED_MFS["medium"])

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(u_spd, slow_mf, "r--", lw=1.5, alpha=0.6, label="Slow MF")
    ax.plot(u_spd, medium_mf, "g--", lw=1.5, alpha=0.6, label="Medium MF")
    ax.fill_between(u_spd, result.aggregated_curve, alpha=0.35, color="steelblue", label="Aggregated region")
    ax.axvline(result.crisp_speed, color="k", lw=2, ls="--", label=f"Centroid = {result.crisp_speed:.1f} km/h")
    ax.set_title(f"Worked Example - Fragility={result.fragility_val}, Bumpiness={result.bumpiness_val}",
                 fontweight="bold")
    ax.set_xlabel("Max Safe Speed (km/h)")
    ax.set_ylabel("Membership degree μ")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
