"""
Helper file for generating an environment rollout
"""

import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
import numpy as np
from matplotlib import animation, rc
from matplotlib.animation import PillowWriter
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def generate_env_rollout_animation(
    env,
    i_start=1,
    fps=60,
    tagger_color="#C843C3",
    runner_color="#245EB6",
    runner_not_in_game_color="#666666",
    fig_width=4,
    fig_height=4,
):
    fig, ax = plt.subplots(
        1, 1, figsize=(fig_width, fig_height)  # , constrained_layout=True
    )
    ax.remove()
    ax = fig.add_subplot(1, 1, 1, projection="3d")

    # Bounds
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(-0.01, 0.01)

    # Surface
    corner_points = [
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
    ]

    poly = Polygon(corner_points, color=(0.1, 0.2, 0.5, 0.15))
    ax.add_patch(poly)
    art3d.pathpatch_2d_to_3d(poly, z=0, zdir="z")

    # "Hide" side panes
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # Hide axes
    ax.set_axis_off()

    # Set camera
    ax.elev = 40
    ax.azim = -55
    ax.dist = 10

    # Try to reduce whitespace
    fig.subplots_adjust(left=0, right=1, bottom=-0.2, top=1)

    # Plot init data
    lines = [None for _ in range(env.num_agents)]

    for idx in range(len(lines)):
        if idx in env.taggers:
            lines[idx] = ax.plot3D(
                env.global_state["loc_x"][:1, idx] / env.grid_length,
                env.global_state["loc_y"][:1, idx] / env.grid_length,
                0,
                color=tagger_color,
                marker="o",
                markersize=10,
            )[0]
        else:  # runners
            lines[idx] = ax.plot3D(
                env.global_state["loc_x"][:1, idx] / env.grid_length,
                env.global_state["loc_y"][:1, idx] / env.grid_length,
                [0],
                color=runner_color,
                marker="o",
                markersize=5,
            )[0]

    init_num_runners = env.num_agents - env.num_taggers

    def _get_label(timestep, n_runners_alive, init_n_runners):
        return (
            "Continuous Tag\n"
            + "Time Step:".ljust(14)
            + f"{timestep:4.0f}\n"
            + "Runners Left:".ljust(14)
            + f"{n_runners_alive:4} ({n_runners_alive / init_n_runners * 100:.0f}%)"
        )

    label = ax.text(
        0,
        0,
        0.02,
        _get_label(0, init_num_runners, init_num_runners).lower(),
    )

    label.set_fontsize(14)
    label.set_fontweight("normal")
    label.set_color("#666666")

    def animate(i):
        start = max(i - i_start, 0)
        for idx, line in enumerate(lines):
            line.set_data_3d(
                env.global_state["loc_x"][start:i, idx] / env.grid_length,
                env.global_state["loc_y"][start:i, idx] / env.grid_length,
                np.zeros((i - start,)),
            )

            still_in_game = env.global_state["still_in_the_game"][i, idx]

            if not still_in_game:
                line.set_color(runner_not_in_game_color)
                line.set_marker("")

        n_runners_alive = (
            env.global_state["still_in_the_game"][i].sum() - env.num_taggers
        )
        label.set_text(_get_label(i, n_runners_alive, init_num_runners).lower())

    ani = animation.FuncAnimation(
        fig, animate, np.arange(1, env.episode_length), interval=1000.0 / fps
    )

    return ani
