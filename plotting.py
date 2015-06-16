from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt


class VerticalLineAdder(object):
    def __init__(self, fig, axs):
        self.fig = fig
        self.axs = axs
        self.xs = [0]
        self.cid = fig.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print('click', event)
        x = event.xdata
        if event.button == 3:
            for ax in axs:
                ax.vlines(x, -3, 3, color='k', lw=3)
        plt.draw()

if __name__ == '__main__':
    fig, axs = plt.subplots(3, 1, sharex=True, sharey=True)
    for ax in axs:
        ax.plot(np.random.normal(0, 1, 1000,))
        ax.set_ylim(-3, 3)

    VerticalLineAdder(fig, axs)

    plt.show()