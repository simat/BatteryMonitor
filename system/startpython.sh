TZ='Australia/Perth'; export TZ
cd ~/BatteryMonitor
python3 -u batteries.py $1 1> /dev/null 2>batteries.log
echo "$!" > batpid
# python batteries.py
exit 0
