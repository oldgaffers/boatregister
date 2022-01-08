#!/bin/sh
echo $1
mkdir -p page-data/boat/$1
./getboat.sh $1 > page-data/boat/$1/page-data.json
git add page-data/boat/$1/page-data.json
