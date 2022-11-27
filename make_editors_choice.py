import yaml
import json
from os import listdir
from datetime import date, datetime
import requests

def get_boat(path):
  with open(path, "r") as stream:
    try: 
      boat = yaml.safe_load(stream)
    except Exception as e:
      print(e)
      print('OGA', path)
      boat = None
  if boat is None:
    return None
  else:
    return boat

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
  chosen = editors_choice['filters']['oga_nos']
  mypath='boat/'
  boats = listdir(mypath)
  for b in boats:
    boat = get_boat(f"{mypath}/{b}/boat.yml")
    if boat is not None:
      oga_no = int(b)
      if oga_no not in chosen:
        r = requests.head(f'https://oga.smugmug.com/Boats/OGA-{oga_no}/')
        if r.ok:
            chosen.insert(0, oga_no)
        else:
            chosen.append(oga_no)
  editors_choice['filters']['oga_nos'] = chosen
  with open('fleets/editors choice', "w") as stream:
      json.dump(editors_choice, stream, ensure_ascii=False, default=json_serial)
