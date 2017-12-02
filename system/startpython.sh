TZ='Australia/Perth'; export TZ
cd ~/BatteryMonitor
python -u batteries.py $1 1> /dev/null 2>batteries.log
# python batteries.py
exit 0
