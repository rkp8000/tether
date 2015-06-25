import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

N = 10000


for N_data in [50, 100, 1000, 5000]:
    print('{} data points'.format(N_data))
    fig, axs = plt.subplots(2, 2)

    p_vals = []
    for _ in range(N):
        x = np.random.uniform(0, 1, N_data)
        y = np.random.normal(0, 1, N_data)

        r, p_val = stats.pearsonr(x, y)
        p_vals += [p_val]

    axs[0, 0].scatter(x, y)
    axs[0, 1].hist(p_vals, 50)

    p_vals = []
    for _ in range(N):
        y = np.random.uniform(0, 1, N_data)
        x = np.concatenate([np.zeros(N_data/2), np.ones(N_data/2)])

        r, p_val = stats.pearsonr(x, y)
        p_vals += [p_val]

    axs[1, 0].scatter(x, y)
    axs[1, 1].hist(p_vals, 50)

plt.show()