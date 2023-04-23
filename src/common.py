import io
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')


def text_from_airport(airport):
    text = f'{airport["name"]}\n'
    text += f'Country: {airport["country"]}\n'
    text += f'IATA: {airport["iata"]}\n'
    text += f'ICAO: {airport["icao"]}\n'
    text += f'Latitude: {airport["lat"]}\n'
    text += f'Longitude: {airport["lon"]}\n'
    text += f'Alt: {airport["alt"]}'
    return text


def plot_to_bytes(fig) -> bytes:
    memory_stream = io.BytesIO()
    fig.savefig(memory_stream, format='png')
    plt.close(fig)

    plot_bytes = memory_stream.getvalue()
    return plot_bytes


def map_plot_to_bytes(plot) -> bytes:
    memory_stream = io.BytesIO()
    plot.savefig(memory_stream, format='png')
    plot_bytes = memory_stream.getvalue()
    return plot_bytes


def text_from_seconds(time):
    time = abs(time)
    if time == 0:
        return None
    if time < 60:
        return f"{time} seconds"
    if 60 <= time < 3600:
        minutes, seconds = divmod(time, 60)
        result = f"{minutes} minutes"
        if seconds > 0:
            return result + f" and {seconds} seconds"
    if time >= 3600:
        hours, r = divmod(time, 60)
        minutes, seconds = divmod(r, 60)
        result = f"{hours} hours"
        if minutes > 0:
            result += f", {minutes} minutes"
        if seconds > 0:
            result += f" and {seconds} seconds"
        return result
