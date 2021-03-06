#!/bin/sh
if [ ! -z $LOG_PERIOD_SEC ] && [ ! -z $MESSAGE_LEN ] && [ ! -z $POD_NAME ]; then
    DIV=$(echo "scale=3; $LOG_PERIOD_SEC" | bc)
    while true; do 
        MESSAGE=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $MESSAGE_LEN | head -n 1)
        echo "$POD_NAME: $(date) $MESSAGE"
        sleep $DIV
    done
fi
