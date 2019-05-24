# monitor_plugins

This directory is used to contain monitoring plugins used for rest api monitoring on various technologies.

It uses click to input variable options
Used in conjunction with nagios other tools to run these modules


Running straight from the CLI could be used as  
./storagegrid/check_grid_health_alarms.py -h 192.168.0.100 -w 1 -c 1 -u api-username -p api-password  
Which will then return a result of (CRIT|WARN|OK|UNKNOWN) plus an exit code  
  Exit code 2 = Crit  
  Exit code 1 = Warn  
  Exit code 0 = OK  
  Exit code 3 = Unknown  
