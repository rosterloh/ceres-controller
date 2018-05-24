import datetime
import logging
import ssl
import time

import jwt
import paho.mqtt.client as mqtt


class IotCoreClient(object):

    def __init__(self, key, loop):
        self._key = key
        self._loop = loop
        self.client = mqtt.Client(
            client_id='projects/project-ceres/locations/europe-west1/registries/ceres-registry/devices/ceres-controller')

        self.client.username_pw_set(username='unused', password=self._create_jwt())
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self._on_connect
        self.client.on_publish = self._on_publish
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.connected = False
        mqtt_topic = '/devices/ceres-controller/device-events'

    def _create_jwt(self):
        token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': 'project-ceres'
        }

        # Read the private key file.
        with open(self._key, 'r') as f:
            private_key = f.read()

        return jwt.encode(token, private_key, algorithm='RS256')

    def _on_connect(self, client, userdata, flags, rc):
        logging.info(mqtt.connack_string(rc))
        self.connected = True

    def _on_publish(self, client, userdata, mid):
        logging.debug('Published message \'{}\''.format(mid))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        logging.debug('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            logging.warning('Subscription failed.')

    def _on_disconnect(self, client, userdata, rc):
        logging.info(mqtt.error_string(rc))

    def _on_message(self, client, userdata, message):
        payload = str(message.payload)
        logging.debug('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        if not payload:
            return

    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def connect(self):
        self.client.connect('mqtt.googleapis.com', 8883)
        self.client.loop_start()

        self.wait_for_connection(5)

        self.client.subscribe('/devices/ceres-controller/config', qos=1)

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
