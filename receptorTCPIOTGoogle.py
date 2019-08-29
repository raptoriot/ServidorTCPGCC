# Programa Servidor
# www.pythondiario.com

import socket
import sys


import os

import argparse
import datetime
import json
import ssl
import time

import jwt
import paho.mqtt.client as mqtt


# Variables de conexion de GCC

registry_id = 'bsa-lb-presionlinea1'
device_id = 'arduino23gprs'
project_id = 'asistente-180018'
private_key_file = 'private-key.pem'
algorithm = 'RS256'
ca_certs = 'roots.pem'
cloud_region = 'us-central1'

mqtt_bridge_hostname = 'mqtt.googleapis.com'
mqtt_bridge_port = 8883
message_type = 'event'
num_messages = 100



def create_jwt(project_id, private_key_file, algorithm):
    """Create a JWT (https://jwt.io) to establish an MQTT connection."""
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1000),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
    """Represents the state of a single device."""

    def __init__(self):
        #  print "entro aca1"
        self.temperature = 0
        self.fan_on = False
        self.connected = False

    #   print "entro aca2"

    def update_sensor_data(self):
        # print "entro aca3"
        """Pretend to read the device's sensor data.
        If the fan is on, assume the temperature decreased one degree,
        otherwise assume that it increased one degree.
        """
        if self.fan_on:
            self.temperature -= 1
        else:
            self.temperature += 1

    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.connected = False

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        # The config is passed in the payload of the message. In this example,
        # the server sends a serialized JSON string.
        data = json.loads(payload)
        if data['fan_on'] != self.fan_on:
            # If changing the state of the fan, print a message and
            # update the internal state.
            self.fan_on = data['fan_on']
            if self.fan_on:
                print('Fan turned on.')
            else:
                print('Fan turned off.')




def enviarmensale(dato):
    # This is the topic that the device will publish telemetry events
    # (temperature data) to.
    mqtt_telemetry_topic = '/devices/{}/events'.format(device_id)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Wait up to 5 seconds for the device to connect.
    device.wait_for_connection(15)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)
    payload = json.dumps({'corriente': dato})
    print('Publishing payload', payload)
    client.publish(mqtt_telemetry_topic, payload, qos=1)
    # client.disconnect()


client = mqtt.Client(
    client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, cloud_region, registry_id,
                                                                         device_id))
client.username_pw_set(username='unused', password=create_jwt(project_id, private_key_file, algorithm))
client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

device = Device()

client.on_connect = device.on_connect
client.on_publish = device.on_publish
client.on_disconnect = device.on_disconnect
client.on_subscribe = device.on_subscribe
client.on_message = device.on_message
client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
client.loop_start()






# Creando el socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.1.102',60261)
print(sys.stderr, 'empezando a levantar %s puerto %s' % server_address)
sock.bind(server_address)

# Escuchando conexiones entrantes
sock.listen(1)

while True:
    # Esperando conexion
    print(sys.stderr, 'Esperando para conectarse')
    connection, client_address = sock.accept()

    try:
        print(sys.stderr, 'concexion desde', client_address)

        # Recibe los datos en trozos y reetransmite
        while True:
            data = connection.recv(50)
            print(type(data))
            print(sys.stderr, 'recibido "%s"' % data)
            print(str(data,'utf-8'))
            enviarmensale(str(data,'utf-8'))
            if data:
                print(sys.stderr, 'enviando mensaje de vuelta al cliente')
               # connection.sendall(data)
            else:
                print(sys.stderr, 'no hay mas datos', client_address)
                break

    finally:
        # Cerrando conexion
        connection.close()