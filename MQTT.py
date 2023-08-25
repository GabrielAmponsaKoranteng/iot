import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = ""
MQTT_BROKER = ""
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "weather logging"

sensor = dht.DHT22(Pin(15))

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '') #Wokwi-GUEST is a free access point with no password required
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()
print("Connected!")

prev_weather = ""
while True:
    print("Measuring weather conditions... ", end="")
    start_time = time.ticks_ms()  # Record the start time
    sensor.measure()
    message = ujson.dumps({
        "temp": sensor.temperature(),
        "humidity": sensor.humidity(),
    })
    if message != prev_weather:
        print("Updated!")
        print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
        client.publish(MQTT_TOPIC, message)
        prev_weather = message
    else:
        print("No change")
    end_time = time.ticks_ms()  # Record the end time
    latency = end_time - start_time
    print("Latency: {} ms".format(latency))
    time.sleep(1)