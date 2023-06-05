#!/usr/bin/ksh

current_date=$(date +"%Y-%m-%d")

year=$(date -d "$current_date" +"%Y")
month=$(date -d "$current_date" +"%m")

log_file=$TRADE_HOME_DIR/production/logs/$year$month.log

if [ ! -f "$log_file" ]; then
    touch "$log_file"
fi
