import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import geopandas as gpd


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

def make_airline_ranking_chart(airline_ranking, flights_axis_label):
    fig, ax = plt.subplots()

    bar_width = 0.75
    x = list(map(lambda t: t[0], airline_ranking))
    y = list(map(lambda t: t[1], airline_ranking))

    for i in range(len(x)):
        ax.bar(i * 2 * bar_width, y[i], bar_width)

    ax.set_xticks(np.arange(len(x)) * 2 * bar_width, x)

    ax.set_axisbelow(True)
    ax.grid(axis='y')

    ax.set_xlabel('Airline')
    ax.set_ylabel(flights_axis_label)

    return fig


def make_flight_map(flight_details):
    origin = flight_details['airport']['origin']['position']
    destination = flight_details['airport']['destination']['position']
    x = [origin['longitude'], destination['longitude']]
    y = [origin['latitude'], destination['latitude']]
    scale = 30

    countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    countries.plot(color="#0077b6")

    plt.plot(x, y, color="#ffb703", markersize="5", marker="o")

    plt.plot([destination['longitude']], [destination['latitude']], marker='*', markersize="8", color="red")
    plt.xlim([min(x) - scale, max(x) + scale])
    plt.ylim([min(y) - scale, max(y) + scale])

    origin_marker = mlines.Line2D([], [], color="#ffb703", marker='o', linestyle='None',
                                  markersize=10, label='Origin')
    destination_marker = mlines.Line2D([], [], color='red', marker='*', linestyle='None',
                                       markersize=10, label='Destination')

    plt.legend(handles=[origin_marker, destination_marker])

    return plt

