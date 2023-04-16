FROM ghcr.io/osgeo/gdal:ubuntu-small-latest
RUN apt-get update && apt-get -y install python3-pip --fix-missing
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./src .
CMD ["python3", "main.py"]
