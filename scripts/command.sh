#!/bin/bash

# Usage:
#
# 1, Edit schedule tasks 
#    crontab -e
#
# 2, Add lines as following,
#    # m h  dom mon dow   command
#    29  3   * * *   bash /xxx/.../update.sh
#
# 3, Restart cron and view status
#
#    sudo /sbin/service crond reload
#    sudo /sbin/service crond restart
#    sudo /sbin/service crond status
#    sudo cat /var/spool/cron/USERNAME

err_exit() {
	local log_file=$1
    local now=`TZ='Asia/Shanghai' date`
    echo "Failed to update at $now." >> $log_file
    exit 1
}

get_property() {

    local config_file=$1
    local prop_key=$2

    local prop_value=`cat ${config_file} | grep ${prop_key} | cut -d'=' -f2`

	echo $prop_value
}

run() {
	local app=$1
	local config_file=$2

	local num="${#app}"
	# Remove '.py'
	local pos=$(($num - 3))
	local name=`echo $APP | cut -c1-$pos`

	local code_path=$(get_property $config_file 'code-path')
	local output_path=$(get_property $config_file 'output-path')

	mkdir -p "$output_path/logs" -m 775

	local log_file="$output_path/logs/$name.log"

	# Begin
	local startDate=`TZ='Asia/Shanghai' date`
	echo "Updating at $startDate ..." >> $log_file

	# Running
	cd $code_path \
	&& source env/bin/activate \
	&& python $@ 1>> $log_file 2>> $log_file || err_exit $log_file

	# End
	endDate=`TZ='Asia/Shanghai' date`
	echo "Updated at $endDate" >> $log_file
}

# Sample:
#
# # Include command.sh
#
# DIR=$(dirname "$0")
# source "$DIR/command.sh"
#
# # APP is a relative path to code path
#
# APP=$(basename "$0")
# APP=${APP//\.sh/.py}
#
# # CONFIG_FILE should be an absolute path
# CONFIG_FILE="/.../config.ini"
#
# run $APP $CONFIG_FILE

