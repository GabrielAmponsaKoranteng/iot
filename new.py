#importing needed modules
import time
import random
import socket
import paho.mqtt.client as mqtt
import pika
import asyncio
import aiocoap

# Generate a client ID based on the hostname
def generate_client_id():
    hostname = socket.gethostname()
    return f"{hostname}_iot_client"

# MQTT settings
mqtt_broker_address = "xxxxxxxx" #enter broker address here
mqtt_port = 0000 #enter port
mqtt_topic = "iot/temperature"

# AMQP settings
amqp_broker_address = "xxxxxxxxxx" #enter broker address here
amqp_port = 0000 #enter port here
amqp_exchange = "iot_exchange"
amqp_routing_key = "iot.temperature"

# CoAP settings
coap_server_address = "xxxxxxx" #enter coap  server address

# Function to calculate latency
def calculate_latency(start_time):
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert to milliseconds

# Function to simulate IoT temperature readings
def generate_temperature_reading():
    return random.uniform(20.0, 30.0)  # Simulate temperature between 20.0 and 30.0

# Function to publish MQTT message
def publish_mqtt_message(client, payload, qos):
    client.publish(mqtt_topic, payload, qos=qos)

# Function to publish AMQP message
def publish_amqp_message(connection, payload):
    channel = connection.channel()
    channel.basic_publish(exchange=amqp_exchange, routing_key=amqp_routing_key, body=payload)

# Function to send CoAP request
async def send_coap_request(payload):
    protocol = await aiocoap.Context.create_client_context()
    request = aiocoap.Message(code=aiocoap.POST, payload=payload)
    request.set_request_uri(coap_server_address)
    response = await protocol.request(request).response
    return response

# Main function
def main():
    protocol_choice = input("Select protocol (mqtt/amqp/coap): ").lower()
    num_devices = int(input("Enter number of devices: "))
    qos_level = int(input("Enter QoS level (0/1/2): "))

    payload = "Temperature: {:.2f} °C".format(generate_temperature_reading())

    if protocol_choice == "mqtt":
        client_id = generate_client_id()
        client = mqtt.Client(client_id=client_id)
        client.connect(mqtt_broker_address, mqtt_port)

        start_time = time.time()
        for _ in range(num_devices):
            temperature = generate_temperature_reading()
            payload = "Temperature: {:.2f} °C".format(temperature)
            publish_mqtt_message(client, payload, qos=qos_level)
            time.sleep(1)  # Simulate delay between readings
        latency = calculate_latency(start_time)
        print(f"MQTT Average Latency: {latency:.2f} ms")
        client.disconnect()

    elif protocol_choice == "amqp":
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=amqp_broker_address, port=amqp_port))

        start_time = time.time()
        for _ in range(num_devices):
            temperature = generate_temperature_reading()
            payload = "Temperature: {:.2f} °C".format(temperature)
            publish_amqp_message(connection, payload)
            time.sleep(1)  # Simulate delay between readings
        latency = calculate_latency(start_time)
        print(f"AMQP Average Latency: {latency:.2f} ms")
        connection.close()

    elif protocol_choice == "coap":
        start_time = time.time()
        for _ in range(num_devices):
            temperature = generate_temperature_reading()
            payload = "Temperature: {:.2f} °C".format(temperature)
            asyncio.get_event_loop().run_until_complete(send_coap_request(payload))
            time.sleep(1)  # Simulate delay between readings
        latency = calculate_latency(start_time)
        print(f"CoAP Average Latency: {latency:.2f} ms")

    else:
        print("Invalid protocol choice.")

if __name__ == "__main__":
    main()
