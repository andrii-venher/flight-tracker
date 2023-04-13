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
