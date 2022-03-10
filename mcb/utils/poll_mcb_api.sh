#!/bin/bash
filename=mcb_api_log_`date +%F_%H-%m-%S`.tsv
printf "Time\tJSON\n" > $filename
URL="http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
interval=$1
count=$2

echo "Saving data to $filename every $interval seconds, $count times."

for i in `seq 1 $count`;
do
   TIME=`date -Is`;
   printf "$TIME\t" >> $filename;
   curl -s $URL >> $filename;
   printf "\n" >> $filename;
   sleep $interval;
done




