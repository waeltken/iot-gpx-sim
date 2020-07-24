import asyncio
import time
import json
from datetime import datetime

import gpxpy
import gpxpy.gpx

from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message


async def main():
    # In a production environment, don't store
    # connection information in the code.
    provisioning_host = 'global.azure-devices-provisioning.net'
    id_scope = '0ne001411B5'
    registration_id = 'Bike001'
    symmetric_key = 'HdKhiBIhJDTWiDkDnGiya2uy7/LqRnDknaWSaMkGCc4='

    delay = 5

    gpx_file = open('fahrrad.gpx', 'r')
    gpx = gpxpy.parse(gpx_file)

    async def register_device():
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=provisioning_host,
            registration_id=registration_id,
            id_scope=id_scope,
            symmetric_key=symmetric_key,
        )

        registration_result = await provisioning_device_client.register()

        print(f'Registration result: {registration_result.status}')

        return registration_result

    async def connect_device():
        device_client = None
        try:
            registration_result = await register_device()
            if registration_result.status == 'assigned':
                device_client = IoTHubDeviceClient.create_from_symmetric_key(
                    symmetric_key=symmetric_key,
                    hostname=registration_result.registration_state.assigned_hub,
                    device_id=registration_result.registration_state.device_id,
                )
                # Connect the client.
                await device_client.connect()
                print('Device connected successfully')
        finally:
            return device_client

    device_client = await connect_device()

    async def send_telemetry():
        print(
            f'Sending telemetry from the provisioned device every {delay} seconds')
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                    print(datetime.now())
                    payload = json.dumps({
                        "long": point.longitude,
                        "lat": point.latitude,
                        "timestamp": str(datetime.now())
                    })
                    msg = Message(payload)
                    await device_client.send_message(msg)
                    time.sleep(delay)

    await send_telemetry()


if __name__ == '__main__':
    asyncio.run(main())
