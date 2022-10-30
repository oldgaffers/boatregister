#!/bin/sh
for i in `ls boat`
do
  echo $i
  ./getboat.sh $i|base64|./make_boat_yaml
done
