import json
import re

import datetime


from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '127.0.0.1'
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'my_sensors'

MQTT_ADDRESS = '127.0.0.1' 
MQTT_USER = ''
MQTT_PASSWORD = ''
MQTT_TOPIC = 'domoticz/in/MyMQTT/+/+/+/+/+'
MQTT_REGEX = 'domoticz/in/MyMQTT/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086 , INFLUXDB_USER, INFLUXDB_PASSWORD, None)


class SensorData(NamedTuple):
    Measurement: str
    Node_ID: str
    Child_ID: str
    Command: str
    Ack : str
    SensorType : str
    value: float

##### Mysensors

class MySensorClass:
        value = int
        type = str
        Comment  = str

MysensorsProp = MySensorClass()

def getTypeData(mysensorsValue_json,x):
        print("start get TypeData")
        for typenr in mysensorsValue_json:
                if typenr["value"]:
                        MysensorsProp.type=typenr["type"]
                        MysensorsProp.Comment=typenr["Comment"]
                        return


mysensorsValue_json = [
    
        {
        "value":0,
        "type" : "V_TEMP",
        "Comment" : "Temperature"
        },
        {
        "value":1,
        "type" : "V_HUM",
        "Comment" : "Humidity"
        },
        {
        "value":2,
        "type" : "V_STATUS",
        "Comment" : "Binary status. 0=off 1=on"
        },
        {
        "value":3,
        "type" : "V_PERCENTAGE",
        "Comment" : "Percentage value. 0-100 (%)"
        },
        {
        "value":4,
        "type" : "V_PRESSURE",
        "Comment" : "Atmospheric Pressure",
        },
        {
        "value":5,
        "type" : "V_FORECAST",
        "Comment" : "Whether forecast",
        },
        {
        "value":6,
        "type" : "V_RAIN",
        "Comment" : "Amount of rain"
        },
        {
        "value":7,
        "type" : "V_RAINRATE",
        "Comment" : "Rate of rain"
        },
        {
        "value":8,
        "type" : "V_WIND",
        "Comment" : "Windspeed"
        },
                {
        "value":9,
        "type" : "V_GUST",
        "Comment" : "Gust"
        },
                {
        "value":10,
        "type" : "V_DIRECTION",
        "Comment" : "Wind direction 0-360 (degrees)"
        },
                {
        "value":11,
        "type" : "V_UV",
        "Comment" : "UV light level	"
        },
                {
        "value":12,
        "type" : "V_WEIGHT",
        "Comment" : "Weight (for scales etc)	"
        },
                {
        "value":13,
        "type" : "V_DISTANCE",
        "Comment" : "Distance"
        },
################# SKIPPED A LOT #########
                {
        "value":38,
        "type" : "V_VOLTAGE",
        "Comment" : "Voltage level"
        },
                {
        "value":39,
        "type" : "V_CURRENT",
        "Comment" : "Current level"
        },
                {
        "value":47,
        "type" : "V_TEXT",
        "Comment" : "Text message to display on LCD or controller device"
        },           
        
    
]


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    if sensor_data is not None:
        _send_sensor_data_to_influxdb(sensor_data)


def _parse_mqtt_message(topic, payload):
    print('parse loop')
    match = re.match(MQTT_REGEX, topic)
    print('after match')
    if match:
        
        #print('inside match')
        t = 42  
        #print('t =', t)
        x = 0
        #print('x =', x)
        print(match.group(5))
        value = match.group(1)
        
        SensorTypeInt = match.group(5)
        SensorTypeInt = int(SensorTypeInt)
        print('SensorTypeInt =>', type(SensorTypeInt))

        print('value =>', type(value))
        if SensorTypeInt == 0:
            SensorType = 'V_TEMP'
            print ('It was 0/Temp')
            print(x)
        if SensorTypeInt == 1:
            SensorType = 'V_HUM'
            print ('It was 1/hum')
        if SensorTypeInt == 2:
            SensorType = 'V_STATUS'
            print ('It was 2/V_STATUS')
        if SensorTypeInt == 16:
            SensorType = 'V_TRIPPED'
            print ('It was 16/V_TRIPPED')
        if SensorTypeInt == 22:
            SensorType = 'MQTT-GATEWAY-HEARTBEAT'
            print ('It was 22/Heartbeat')
                
        else:
            print ('Broke out of the loop')
         
        
        measurement =  SensorType
        print(type(measurement))
        print('measurement 0 : ', measurement)
        ##1
        Node_ID =  match.group(1)
        print('Node_ID : ', Node_ID, type(Node_ID))
        ## 2
        Child_ID =  match.group(2)
        print('Child_ID : ', Child_ID, type(Child_ID))
        ## 3
        Command =  match.group(3)
        print('Command : ', Command, type(Command))
        ## 4
        Ack =  match.group(4)
        print('Ack : ', Ack,type(Ack))
        ##5
        # measurement =  match.group(5)
        # print('measurement 5 : ', measurement,type(measurement))
        
        value = payload
        print('value : ',value, type(value))
        print('meas incomming')    
        print(datetime.datetime.now()) 
        time = datetime.datetime.now()
        print(time)
        print('DATA_STORED: measurement: ',measurement, " Node_ID: ", Node_ID," : ", Child_ID," - ", Command," - ", Ack," - ", SensorType," - ", float(value))

        if measurement == 'status':
            return None
        print('1')
        return SensorData(measurement, Node_ID, Child_ID, Command, Ack, SensorType, float(value))
    else:   
        print('3')
        return None
    print('end')

def _send_sensor_data_to_influxdb(sensor_data):
    print("sensor_data.Node_ID",sensor_data.Node_ID)
    print("sensor_data.Child_ID",sensor_data.Child_ID)
    json_body = [
        {
            "measurement": sensor_data.Measurement,
            "time": datetime.datetime.now(),
            "tags": {
                "Node_ID": sensor_data.Node_ID,
                "Child_ID": sensor_data.Child_ID,
                'Child_ID': sensor_data.Child_ID,
                'Command': sensor_data.Command,
                'Ack': sensor_data.Ack,
                'SensorType' : sensor_data.SensorType
            },
            "fields": {
                'value': sensor_data.value,
            }
        }
    ]

    print('Send JSON')
    '''json_body = [
        {
        'Measurement': sensor_data.Node_ID,
        'tags': {
            'Node_ID': sensor_data.Node_ID,
            'Child_ID': sensor_data.Child_ID,
            'Command': sensor_data.Command,
            'Ack': sensor_data.Ack,
            'SensorType' : sensor_data.SensorType
        },
        'fields': {
            'value': sensor_data.value,
            }
        }
    ]'''
    
    print('Trying to Send')
    influxdb_client.write_points(json_body)
    print('JSON Send')


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
        print("created a database")
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main():
    _init_influxdb_database()
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()
    print("main() completed")
    


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()
