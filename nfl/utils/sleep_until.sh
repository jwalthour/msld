#!/bin/bash
# Method courtesy https://stackoverflow.com/a/646008/415551
target=$1
current_epoch=$(date +%s)
target_epoch=$(date -d "$target" +%s)

sleep_seconds=$(( $target_epoch - $current_epoch ))

sleep $sleep_seconds
