import json
import re

import datetime

from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = '127.0.0.1'
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'my_sensors_dev' # Chage to my_sensors when changing to live version
INFLUXDB_DATABASE_Nodes = 'my_sensors_Nodes_dev' #  data from nodes when the report to the server. Also internal

MQTT_ADDRESS = '127.0.0.1' 
MQTT_USER = ''
MQTT_PASSWORD = ''
MQTT_TOPIC = 'domoticz/in/MyMQTT/+/+/+/+/+'
MQTT_REGEX = 'domoticz/in/MyMQTT/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086 , INFLUXDB_USER, INFLUXDB_PASSWORD, None)

print("dev")
## Json
## Load JSon Presentation values
LoadPresJson = json.load(open("mysensorsPresValue.json"))
LoadIntJson = json.load(open("mysensorsIntValue.json"))
#print(LoadPresJson)
#print("#################################")
#print(LoadIntJson)

##Classes and objects
class SensorData(NamedTuple):
    Measurement: str
    Node_ID: str
    Child_ID: str
    Command: str
    Ack : str
    SensorType : str
    value: float
    Desctription: str

class MySensorClass:
        value = int
        type = str
        Desctription  = str

MysensorsProp = MySensorClass()

def getTypeData(mysensorsValue_json,inctype):
        #print("start get TypeData")
        for typenr in mysensorsValue_json:
                if typenr["value"] == inctype:
                        MysensorsProp.type=typenr["type"]
                        MysensorsProp.Desctription=typenr["Desctription"]
                        return


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    print('on_message')
    sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    if sensor_data is not None:
        _send_sensor_data_to_influxdb(sensor_data)



## parsing the message, and fill the "class SensorData(NamedTuple):" These variables have to be loaded to send fill the Json of "def _send_sensor_data_to_influxdb(sensor_data):"

def _parse_mqtt_message(topic, payload):
    print('parse loop')
    match = re.match(MQTT_REGEX, topic)
    print('after match')
    if match:
        
        ## Check Command, 0. presentation 1. Set (data) 2. request(data) 3. Internal 4. Stream 
        Command =  int(match.group(3))
        print(Command)
        

        ## if Command = 0
            #PresValue()
            #measurement = Pers
        if Command == 1:
            print("Parsing Set")
            getTypeData(LoadPresJson,int(match.group(5)))                
            measurement =  "Set" 
            SensorType = MysensorsProp.type
            Node_ID =  match.group(1)
            Child_ID =  match.group(2)
            Ack =  match.group(4)
            Desctription = str(MysensorsProp.Desctription)
            value = payload

        if Command == 2:
            print("Parsing Req")
            getTypeData(LoadPresJson,int(match.group(5)))                
            measurement =  "Req" 
            SensorType = MysensorsProp.type
            Node_ID =  match.group(1)
            Child_ID =  match.group(2)
            Ack =  match.group(4)
            Desctription = str(MysensorsProp.Desctription)
            value = payload

        if Command == 3:
            print("Parsing Int")
            getTypeData(LoadPresJson,int(match.group(5)))                
            measurement =  "Int" 
            SensorType = "INT FOR TESTING TYPE"
            Node_ID =  match.group(1)
            Child_ID =  match.group(2)
            Ack =  match.group(4)
            Desctription = str(payload)
            value = "1"
            print("Parsing Int OUT")
         
         ####################################################### Value is float so cant be parsed
       
        ## if Command = 4
            #StreamValue()
            #measurement = Stream      


        ##
        ##SensorTypeInt = match.group(5)
        ##SensorTypeInt = int(SensorTypeInt)
        
        
        
        time = datetime.datetime.now()
        print(time)
        time.strftime('%l:%M%p %Z on %b %d, %Y') # ' 1:36PM EDT on Oct 18, 2010'
        print('DATA_STORED: measurement: ',measurement, " Node_ID: ", Node_ID," : ", Child_ID," - ", Command," - ", Ack," - ", SensorType," - ", float(value) , " - ", Desctription )

        if measurement == 'status':
            return None
        return SensorData(measurement, Node_ID, Child_ID, Command, Ack, SensorType, float(value), Desctription)
    else:   
        return None
    print('end')

def _send_sensor_data_to_influxdb(sensor_data):
    print("_send_sensor_data_to_influxdb")
    if sensor_data.Command == 3:
        influxdb_client.switch_database(INFLUXDB_DATABASE_Nodes)
    else:
        influxdb_client.switch_database(INFLUXDB_DATABASE)

   
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
                'SensorType' : sensor_data.SensorType,
                'Desctription' : sensor_data.Desctription
            },
            "fields": {
                'value': sensor_data.value,
            }
        }
    ]

    
    print('Trying to Send')
    influxdb_client.write_points(json_body)
    print('JSON Send')


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
        print("created a database", INFLUXDB_DATABASE)
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE_Nodes, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE_Nodes)
        print("created a database", INFLUXDB_DATABASE_Nodes)
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