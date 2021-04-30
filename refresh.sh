#!/usr/bin/env bash

prefix='https://purge.jsdelivr.net/npm/logicdn/logi.im/api/asset'
apis=(
    "$prefix/data/sentence.json"
    "$prefix/data/friend.json"
    "$prefix/img/"
)

refresh() {
    for i in {1..3}; do
        curl -s "$1"
        sleep 20
    done
}

for api in "${apis[@]}"; do
    refresh "$api" &
done

sleep 180
