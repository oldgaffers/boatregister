#!/bin/sh
for i in `ls page-data/boat`
do
  echo $i
  ./getboat.sh $i > page-data/boat/$i/page-data.json
done
