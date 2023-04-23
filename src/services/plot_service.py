import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import geopandas as gpd

plt.set_loglevel('WARNING')


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


def make_delayed_chart(flight_ids, diffs):
    fig, ax = plt.subplots()

    for i in range(len(flight_ids)):
        if diffs[i] > 0:
            ax.bar(flight_ids[i], diffs[i], color='red', label='Delayed')
        elif diffs[i] < 0:
            ax.bar(flight_ids[i], diffs[i], color='green', label='Earlier')
        else:
            ax.bar(flight_ids[i], 1, color='blue', label='On time')
            ax.bar(flight_ids[i], -1, color='blue', label='On time')

    ax.set_xticklabels(flight_ids, rotation=45)

    ax.set_axisbelow(True)
    ax.grid(axis='y')

    # Remove duplicates from legend labels
    handles, labels = ax.get_legend_handles_labels()
    handle_list, label_list = [], []
    for handle, label in zip(handles, labels):
        if label not in label_list:
            handle_list.append(handle)
            label_list.append(label)

    # Resize plot to include moved legend and rotated x labels
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 * 1.8, box.width * 0.8, box.height])
    ax.legend(handle_list, label_list, loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_xlabel('Flight ID')
    ax.set_ylabel("Earlier (minutes) / Delayed (minutes)")

    return fig
