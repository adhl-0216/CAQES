#!/bin/bash
while true; do
  timestamp=$(date "+%b %d %H:%M:%S")
  hostname=$(hostname)
  snort_message="$timestamp $hostname snort[$(($RANDOM % 9000 + 1000))]: [1:$(($RANDOM % 1000000 + 1)):1] Potential Attack [Classification: Attempted Administrator Privilege Gain] [Priority: 1] {TCP} 192.168.$(($RANDOM % 255)).$(($RANDOM % 255)):$(($RANDOM % 65535)) -> 10.0.0.1:80"
  echo "$snort_message" >> /tmp/snort.log
  sleep 1 # Generate a log message every second
done