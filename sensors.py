import RPi.GPIO as GPIO
import time, threading
import os
import logging

logging.basicConfig(level=logging.INFO)

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE")
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH")
pnconfig.uuid = '3fa7edb4-3d6e-11ec-8bbf-0242ac130003'
pubnub = PubNub(pnconfig)

my_channel = 'johns-pi-channel-sd3a'
sensor_list = ['buzzer']
data = {}


PIR_pin = 16
Buzzer_pin = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)


def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.02)


def motion_detection():
    global data
    data["alarm"] = False
    trigger = False
    while True:
        if GPIO.input(PIR_pin):
            print("Motion detected")
            beep(4)
            publish(my_channel, {"motion" : "Yes"})
            trigger = True
            time.sleep(1)

        elif trigger:
            publish(my_channel, {"motion" : "No"})
            trigger = False
            print("No motion detected")
        if data["alarm"]:
            beep(2)
        time.sleep(1)


def publish(channel, msg):
    pubnub.publish().channel(my_channel).message(msg).pn_async(my_publish_callback)


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        print("Message successfully published")
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            print("Successfully connected to Pubnub")
            pubnub.publish().channel(my_channel).message('Hello world!').pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        try:
            print(message.message, ": ", type(message.message))
            msg = message.message
            key = list(msg.keys())
            if key[0] == "event":
                self.handle_event(msg)
        except Exception as e:
            print(message.message)
            print(e)
            pass


    def handle_event(self, msg):
        global data
        event_data = msg["event"]
        key = list(event_data.keys())
        print(key)
        print(key[0])
        if key[0] in sensor_list:
            print(event_data[key[0]])
            if event_data[key[0]] == "ON":
                print("Setting alarm")
                data["alarm"] = True
            elif event_data[key[0]] == "OFF":
                print("Turning alarm off")
                data["alarm"] = False


if __name__ == '__main__':
    sensors_thread = threading.Thread(target = motion_detection)
    sensors_thread.start()
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(my_channel).execute()






