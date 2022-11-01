#!/bin/sh
curl 'https://api-oga.herokuapp.com/v1/graphql' \
--silent \
-X 'POST' \
-H 'Content-Type: application/json' \
-H 'Pragma: no-cache' \
-H 'Accept: application/json' \
-H 'Accept-Language: en-gb' \
-H 'Cache-Control: no-cache' \
-H 'Connection: keep-alive' \
--data '{"query": "query MyQuery { boat { oga_no } }"}' | jq '.data.boat[].oga_no'
