
import os
import time
import uuid

import json
from datetime import datetime

import gpxpy
import gpxpy.gpx

from azure.iot.device import IoTHubDeviceClient, Message
# Parsing an existing file:
# -------------------------

gpx_file = open('fahrrad.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
device_name = os.getenv("DEVICE_NAME")

print(conn_str)
print(device_name)
# The client object is used to interact with your Azure IoT hub.
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

# Connect the client.
device_client.connect()

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
            print(datetime.now())
            data = {
                "long": point.longitude,
                "lat": point.latitude,
                "timestamp": str(datetime.now())
            }
            json_str = json.dumps(data)
            print(json_str)
            msg = Message(json_str)
            device_client.send_message(msg)
            time.sleep(1)


