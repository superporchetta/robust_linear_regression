import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import scipy.stats as stats
from tqdm.auto import tqdm

def state_equations(var_func, var_hat_func, delta = .001, lambd = .01, alpha = .5, init=(.5, .5, 0.5)):
    m, q, sigma = init[0], init[1], init[2]
    err = 1.0
    blend = .7
    while err > 1e-6:
        m_hat, q_hat, sigma_hat = var_hat_func(m, q, sigma, alpha, delta)

        temp_m, temp_q, temp_sigma = m, q, sigma

        m, q, sigma = var_func(m_hat, q_hat, sigma_hat, alpha, delta, lambd)

        err = np.min(np.abs([temp_m - m, temp_q - q, temp_sigma - sigma]))

        m = blend * m + (1 - blend)*temp_m
        q = blend * q + (1 - blend)*temp_q
        sigma = blend * sigma + (1 - blend) * temp_sigma

    return m, q, sigma

def state_equations_max_iters(var_func, var_hat_func, n_max = 1000, delta = .001, lambd = .01, alpha = .5, init=(.5, .5, 0.5)):
    m, q, sigma = init[0], init[1], init[2]
    err = 1.0
    blend = .7
    for _ in range(n_max):
        m_hat, q_hat, sigma_hat = var_hat_func(m, q, sigma, alpha, delta)

        temp_m, temp_q, temp_sigma = m, q, sigma

        m, q, sigma = var_func(m_hat, q_hat, sigma_hat, alpha, delta, lambd)

        err = np.min(np.abs([temp_m - m, temp_q - q, temp_sigma - sigma]))

        m = blend * m + (1 - blend)*temp_m
        q = blend * q + (1 - blend)*temp_q
        sigma = blend * sigma + (1 - blend) * temp_sigma

    return m, q, sigma

def projection_ridge_different_alpha_theory(
        var_func, 
        var_hat_func, 
        alpha_1 = 0.01, 
        alpha_2 = 100, 
        n_alpha_points = 16, 
        lambd = 0.01, 
        delta = 1.0, 
        initial_cond = [0.6, 0.00, 0.00]
    ):
    
    alphas = np.logspace(np.log(alpha_1)/np.log(10), np.log(alpha_2)/np.log(10), n_alpha_points)

    initial = initial_cond
    error_theory = np.zeros(n_alpha_points)

    for i, alpha in enumerate(alphas):
        m, q, _ = state_equations(var_func, var_hat_func, delta, lambd, alpha, init=initial)
        error_theory[i] = 1 + q - 2*m
    
    return alphas, error_theory

def var_func_L2(m_hat, q_hat, sigma_hat, alpha, delta, lambd):
    m = m_hat / (sigma_hat + lambd)
    q = (np.square(m_hat) + q_hat) / np.square(sigma_hat + lambd)
    sigma = 1.0 / (sigma_hat + lambd)
    return m, q, sigma

def var_hat_func_L2(m, q, sigma, alpha, delta):
    m_hat = alpha / (1 + sigma)
    q_hat = alpha * (1 + q + delta - 2 * np.abs(m)) / ((1 + sigma)**2)
    sigma_hat = alpha / (1 + sigma)
    return m_hat, q_hat, sigma_hat

def var_hat_func_L2_num(m, q, sigma, alpha, delta):
    
    return m_hat, q_hat, sigma_hat

def var_hat_func_L1(m, q, sigma, alpha, delta):
    
    return m_hat, q_hat, sigma_hat

def var_hat_func_Huber(m, q, sigma, alpha, delta):

    return m_hat, q_hat, sigma_hat

if __name__ == "__main__":
    alpha_min, alpha_max = 0.01, 100
    alpha_points = 300
    d = 400
    reps = 10
    deltas = [0.2]
    lambdas = [0.01, 0.1, 1.0, 10.0, 100.0]

    alphas = [None] * len(deltas) * len(lambdas)
    errors = [None] * len(deltas) * len(lambdas)

    # m = 0.05 * np.random.random() + 0.45
    # q = 0.02 * np.random.random() + 0.01
    # sigma = 0.1 * np.random.random() + 0.05

    for idx, l in enumerate(lambdas):
        for jdx, delta in enumerate(deltas):
            while True:
                m = np.random.random()
                q = np.random.random()
                sigma = np.random.random()
                if np.square(m) < q + delta * q:
                    break

            initial = [m, q, sigma]

            i = idx * len(deltas) + jdx

            alphas[i], errors[i] = projection_ridge_different_alpha_theory(
                var_func_L2, 
                var_hat_func_L2, 
                alpha_1 = alpha_min, 
                alpha_2 = alpha_max, 
                n_alpha_points = alpha_points, 
                lambd = l, 
                delta = delta,
                initial_cond = initial
            )
            # print(initial)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8), tight_layout=True)

    for idx, l in enumerate(lambdas):
        for jdx, delta in enumerate(deltas):
            i = idx * len(deltas) + jdx
            ax.plot(
                alphas[i], 
                errors[i],
                marker='.',
                label=r"$\lambda = {}$ $\Delta = {}$".format(l, delta)
            )
    
    ax.set_title("L2 Loss")
    ax.set_ylabel(r"$\frac{1}{d} E[||\hat{w} - w^\star||^2]$")
    ax.set_xlabel(r"$\alpha$")
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.minorticks_on()
    ax.grid(True, which='both')
    ax.legend()

    fig.savefig("./imgs/{}.png".format(initial), format='png')

    plt.show()