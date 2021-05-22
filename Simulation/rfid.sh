rfid=$1

message=$(echo '{"uid":'"\"$rfid\""'}')

mosquitto_pub -m $(echo $message) -t "//esp8266\1\rfid" -h mqtt.eclipse.org
