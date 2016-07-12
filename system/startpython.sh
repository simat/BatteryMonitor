TZ='Australia/Perth'; export TZ
cd ~/BatteryMonitor
until [ $? == 9 ]; do
  python -u batteries.py 1> /dev/null 2>~/batteries.log
done
exit 0
