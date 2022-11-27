import json
from os import listdir
from datetime import date, datetime
import requests
import random

def json_serial(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, datetime):
        return obj.isoformat(timespec='seconds')[:-6]+'Z'
    raise TypeError ("Type %s not serializable" % type(obj))

if __name__ == '__main__':
    f = open('fleets/editors choice')
    editors_choice = json.load(f)
    f.close()
    mypath='boat/'
    boats = listdir(mypath)
    with_pictures = []
    without_pictures = []
    for b in boats:
        oga_no = int(b)
        try:
            r = requests.head(f'https://oga.smugmug.com/Boats/OGA-{oga_no}/')
            if r.ok:
                with_pictures.append(oga_no)
            else:
                without_pictures.append(oga_no)
        except:
            without_pictures.append(oga_no)
    random.shuffle(with_pictures)
    random.shuffle(without_pictures)
    editors_choice['filters']['oga_nos'] = with_pictures + without_pictures
    with open('fleets/editors choice', "w") as stream:
        json.dump(editors_choice, stream, ensure_ascii=False, default=json_serial)
