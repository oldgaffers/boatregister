import json
import sys
from os import listdir, environ
from datetime import date, datetime
import requests
import random

def json_serial(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, datetime):
        return obj.isoformat(timespec='seconds')[:-6]+'Z'
    raise TypeError ("Type %s not serializable" % type(obj))

def shuffle(boats):
    with_pictures = []
    without_pictures = []
    r=requests.get('https://api.smugmug.com/api/v2/folder/user/oga/Boats!albums',
        headers={'accept':'application/json'},
        params={
            'APIKey': environ['api_key'],
            '_filter': 'NiceName,AlbumKey,ImageCount',
            '_filteruri': ''
        }
    )
    if not r.ok:
        print('bad response from smugmug')
        return
    albums = r.json()['Response']['Album']
    print('got', len(albums), 'album records from smugmug')
    for b in boats:
        oga_no = int(b)
        count = [a['ImageCount'] for a in albums if a['NiceName']==f'OGA-{oga_no}']
        if len(count) > 0 and count[0] > 0:
            with_pictures.append(oga_no)
        else:
            without_pictures.append(oga_no)
    random.shuffle(with_pictures)
    random.shuffle(without_pictures)
    return with_pictures + without_pictures

if __name__ == '__main__':
    f = open('fleets/editors choice')
    editors_choice = json.load(f)
    f.close()
    if len(sys.argv) > 1:
        featured_oga_no = int(sys.argv[1])
        boats = editors_choice['filters']['oga_nos']
        b = [boat for boat in boats if boat != featured_oga_no]
        editors_choice['filters']['oga_nos'] = [featured_oga_no] + b
    else:
        boats = listdir('boat/')
        editors_choice['filters']['oga_nos'] = shuffle(boats)
    with open('fleets/editors choice', "w") as stream:
        json.dump(editors_choice, stream, ensure_ascii=False, default=json_serial)
