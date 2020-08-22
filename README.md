# MQTTInfluxDBBridge_MySensors


#### *********  STILL WIP   ********* #####

Its a copy of the MQTTInfluxDBBridge found on : https://diyi0t.com/
All credits go to him.

My intentions; Since, at the time of writing, Im using Domoticz and everything gets stored in its database.
In the future I might want to move away from domoticz, but i dont want to lose the data I collected so far.
Thats why I want to log everything in InfluxDB, just so it is stored in a independed database.

**Rundown** 

Changes to the original setup from diyi0t
In contrary to the original file, I made it compatible to my home setup that uses Mysensors (NRF5 and NRF24) nodes with 2 NRF24 MQTT gateways.

To do so, pick up the MQTT message and cut it into pieces, just like the original setup form diyi0t, only for my setup some more cuts need te be made.

the message I receive now: looks like: domoticz/in/MyMQTT/218/0/1/0/1 b'68.55'

The structure of the mysensors message looks like: node-id / child-sensor-id / command / ack / type / payload \n

node-id | child-sensor-id | command | ack | type | payload
---| ---|---|---|---|---
218 | 0 | 1 | 0 | 1 | 68.55


To make this more readable, i creating some Json files with translate for example, type; which is 1, in this case to V_HUM or humidity. This makes reading the value a but easier for when you are browsing though the data.

For more information: https://www.mysensors.org/


So far:
- The type gets filterd out and then is then changed to a readable line. E.g. the Type 0, that comes from the




