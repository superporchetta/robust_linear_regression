from winreg import ExpandEnvironmentStrings
import numpy as np
import matplotlib.pyplot as plt
import fixed_point_equations as fpe
from tqdm.auto import tqdm
from src.utils import check_saved, save_file, load_file

random_number = np.random.randint(0, 100)

names_cm = ["Greens", "Oranges", "Reds", "Purples", "YlGnBu", "RdPu", "Blues"]


def get_cmap(n, name="hsv"):
    return plt.cm.get_cmap(name, n)


alpha_min, alpha_max = 0.01, 100
alpha_points_theory = 31
d = 500
reps = 20
deltas = [[0.1, 1.0]]  # , [1.0, 5.0], [1.0, 10.0]
lambdas = [0.5, 1.0, 2.0]

alphas_theory = [None] * len(deltas) * len(lambdas)
errors_theory = [None] * len(deltas) * len(lambdas)

for idx, l in enumerate(tqdm(lambdas, desc="lambda", leave=False)):
    for jdx, [delta_small, _] in enumerate(tqdm(deltas, desc="delta", leave=False)):
        i = idx * len(deltas) + jdx

        experiment_dict = {
            "loss_name": "L2",
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "alpha_pts": alpha_points_theory,
            "reg_param": l,
            "delta_small": delta_small,
            "experiment_type": "theory",
        }

        file_exists, file_path = check_saved(**experiment_dict)

        if not file_exists:
            while True:
                m = 0.89 * np.random.random() + 0.1
                q = 0.89 * np.random.random() + 0.1
                sigma = 0.89 * np.random.random() + 0.1
                if np.square(m) < q + delta_small * q:
                    break

            initial = [m, q, sigma]

            (
                alphas_theory[i],
                errors_theory[i],
            ) = fpe.projection_ridge_different_alpha_theory(
                fpe.var_func_L2,
                fpe.var_hat_func_L2_num,
                alpha_1=alpha_min,
                alpha_2=alpha_max,
                n_alpha_points=alpha_points_theory,
                lambd=l,
                delta=delta_small,
                initial_cond=initial,
                verbose=True,
            )
            experiment_dict.update(
                {
                    "file_path": file_path,
                    "alphas": alphas_theory[i],
                    "errors": errors_theory[i],
                }
            )

            save_file(**experiment_dict)
        else:
            experiment_dict.update({"file_path": file_path})
            alphas_theory[i], errors_theory[i] = load_file(**experiment_dict)

alphas_BO = [None] * len(deltas)
errors_BO = [None] * len(deltas)

for jdx, [delta_small, _] in enumerate(tqdm(deltas, desc="delta", leave=False)):

    experiment_dict = {
        "alpha_min": alpha_min,
        "alpha_max": alpha_max,
        "alpha_pts": alpha_points_theory,
        "delta_small": delta_small,
        "experiment_type": "BO",
    }

    file_exists, file_path = check_saved(**experiment_dict)

    if not file_exists:
        while True:
            m = 0.89 * np.random.random() + 0.1
            q = 0.89 * np.random.random() + 0.1
            sigma = 0.89 * np.random.random() + 0.1
            if np.square(m) < q + delta_small * q:
                break

        initial = [m, q, sigma]

        alphas_BO[jdx], errors_BO[jdx] = fpe.projection_ridge_different_alpha_theory(
            fpe.var_func_BO,
            fpe.var_hat_func_BO,
            alpha_1=alpha_min,
            alpha_2=alpha_max,
            n_alpha_points=alpha_points_theory,
            lambd=l,
            delta=delta_small,
            initial_cond=initial,
            verbose=True,
        )

        experiment_dict.update(
            {"file_path": file_path, "alphas": alphas_BO[jdx], "errors": errors_BO[jdx],}
        )

        save_file(**experiment_dict)
    else:
        experiment_dict.update({"file_path": file_path})
        alphas_BO[jdx], errors_BO[jdx] = load_file(**experiment_dict)


fig, ax = plt.subplots(1, 1, figsize=(10, 8), tight_layout=True)

for idx, l in enumerate(lambdas):
    colormap = get_cmap(len(deltas) + 3, name=names_cm[idx])

    for jdx, delta in enumerate(deltas):
        i = idx * len(deltas) + jdx
        ax.plot(
            alphas_theory[i],
            errors_theory[i],
            # marker='.',
            label=r"$\lambda = {}$ $\Delta = {}$".format(l, delta[0]),
            color=colormap(jdx + 3),
        )

colormapBO = get_cmap(len(deltas) + 3, "Greys")

for jdx, delta in enumerate(deltas):
    ax.plot(
        alphas_BO[jdx],
        errors_BO[jdx],
        marker=".",
        linestyle="dashed",
        label=r"BO $\Delta$ = {}".format(delta[0]),
        color=colormapBO(jdx + 3),
    )

ax.set_title(r"L2 Loss - $\epsilon = {:.2f}$".format(epsil))
ax.set_ylabel(r"$\frac{1}{d} E[||\hat{w} - w^\star||^2]$")
ax.set_xlabel(r"$\alpha$")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim([0.009, 110])
ax.minorticks_on()
ax.grid(True, which="both")
ax.legend()

# fig.savefig(
#     "./imgs/together - double noise - code {}.png".format(random_number),
#     format="png",
#     dpi=150,
# )

plt.show()
