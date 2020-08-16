# MQTTInfluxDBBridge_MySensors
Its a copy of the MQTTInfluxDBBridge found on : https://diyi0t.com/
All credits go to him.

My intentions; Since, at the time of writing, Im using Domoticz and everything gets stored in its database.
In the future I might want to move away from domoticz, but i dont want to lose the data I collected so far.
Thats why I want to log everything in InfluxDB, just so it is stored in a independed database.


Changes to the original setup from diyi0t
In contrary to the original file, I made is compatible to my home setup that uses Mysensors NRF24 MQTT gateways.

So far:
- The type gets filterd out and then is then changed to a readable line. E.g. the Type 0, that comes from the




Example:
-- Input from the MQTT: 
