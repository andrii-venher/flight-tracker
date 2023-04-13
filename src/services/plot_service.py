import matplotlib.pyplot as plt
import numpy as np


def make_airports_ranking_chart(airports_ranking, flights_axis_label):
    fig, ax = plt.subplots()

    bar_width = 0.75
    x = list(map(lambda t: t[0], airports_ranking))
    y = list(map(lambda t: t[1], airports_ranking))

    for i in range(len(x)):
        ax.bar(i * 2 * bar_width, y[i], bar_width)

    ax.set_xticks(np.arange(len(x)) * 2 * bar_width, x)

    ax.set_axisbelow(True)
    ax.grid(axis='y')

    ax.set_xlabel('Airport')
    ax.set_ylabel(flights_axis_label)

    return fig
