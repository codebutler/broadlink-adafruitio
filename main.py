import sys
import time

import broadlink
import ConfigParser
from Adafruit_IO import MQTTClient

IR_PACKET_AIRCON_POWER = '26005000000128941214121213121213133712131312131212371437133613131212143712371139131211' \
                         '3913371337101513111412101513361115121214111139143613371139130005440001274b12000d050000' \
                         '000000000000'


class BroadlinkAdafruit:
    config = None
    device = None

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('settings.ini')

    def connect(self):
        self.__connect_broadlink()
        while True:
            self.__connect_adafruit()
            time.sleep(15)

    def __connect_broadlink(self):
        print('Searching for Broadlink devices...')
        devices = broadlink.discover(5)
        if len(devices) == 0:
            print('No broadlink devices found')
            sys.exit(1)

        self.device = devices[0]
        self.device.auth()

    def __connect_adafruit(self):
        username = self.config.get('adafruit_io', 'username')
        key = self.config.get('adafruit_io', 'key')

        print('Connecting to Adafruit.IO...')
        client = MQTTClient(username, key)
        client.on_connect = self.__on_connected
        client.on_disconnect = self.__on_disconnected
        client.on_message = self.__on_message

        try:
            client.connect()
            client.loop_blocking()
        except Exception as err:
            print('Error with Adafruit client: %s' % err)
            client.disconnect()

    def __on_connected(self, client):
        feed_id = self.config.get('adafruit_io', 'feed_id')

        print('Connected to Adafruit IO!  Listening for {0} changes...'.format(feed_id))
        client.subscribe(feed_id)

    def __on_disconnected(self):
        print('Disconnected from Adafruit IO!')
        time.sleep(30)
        self.__connect_adafruit()

    def __on_message(self, client, feed_id, payload):
        print("got msg!!!", feed_id, payload)
        if payload == 'aircon_power':
            self.device.send_data(IR_PACKET_AIRCON_POWER.decode('hex'))


BroadlinkAdafruit().connect()
