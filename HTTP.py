import network
import time
from machine import Pin
import dht
import ujson
import urequests

sensor = dht.DHT22(Pin(15))

# HTTP Server Parameters
HTTP_SERVER = "http://localhost:8000"
HTTP_ENDPOINT = "/weather"

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

prev_weather = ""
while True:
    print("Measuring weather conditions... ", end="")
    start_time = time.ticks_ms()  # Record the start time
    sensor.measure()
    data = {
        "temp": sensor.temperature(),
        "humidity": sensor.humidity(),
    }
    message = ujson.dumps(data)
    
    if message != prev_weather:
        print("Updated!")
        
        # Manually format the JSON data and headers
        headers = {'Content-Type': 'application/json'}
        payload = message.encode()
        
        response = urequests.post(HTTP_SERVER + HTTP_ENDPOINT, data=payload, headers=headers)
        print("HTTP Response:", response.status_code)
        response.close()
        prev_weather = message
    else:
        print("No change")
    
    end_time = time.ticks_ms()  # Record the end time
    latency = end_time - start_time
    print("Latency: {} ms".format(latency))
    time.sleep(1)
