while true
do
	mosquitto_pub -m '1' -t "//esp8266\2\pir" -h mqtt.eclipse.org
	echo "Published : 1"
	sleep 1
done
