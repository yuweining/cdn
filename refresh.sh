#!/usr/bin/env bash

prefix='https://purge.jsdelivr.net/npm/logicdn/logi.im/api'
apis=(
    "$prefix/sentence/data.json"
    "$prefix/links/data.json"
)

refresh() {
    for i in {1..6}; do
        curl -s "$1"
        sleep 30
    done
}

for api in "${apis[@]}"; do
    refresh "$api" &
done

sleep 180
