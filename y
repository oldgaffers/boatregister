#!/bin/sh
for i in `cat x`
do
  echo $i
  ./getboat.sh $i > page-data/boat/$i/page-data.json
done
