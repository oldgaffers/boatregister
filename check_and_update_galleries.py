import json
import sys
import os
import yaml
import requests
from requests_oauthlib import OAuth1Session
from add_kw import get_album, update_gallery_name, add_to_all, get_images

def boat_name(no):
    with open(f"boat/{no}/boat.yml", "r", encoding='utf-8') as stream:
      boat = yaml.safe_load(stream)
    return boat['name']

def check_and_update(no):
    print(f'OGA No, {no}!')
    album = get_album(no)
    if album is None:
        print(f"OGA No {no} has no gallery")
        return
    gn = album['Title']
    bn = boat_name(no)
    newgn = f"{bn} ({no})"
    if gn != newgn:
        print(f'Gallery name is {gn}, should be {newgn}. Updating...')
        update_gallery_name(no, album, newgn)

if __name__ == '__main__':
  if len(sys.argv) == 2:
    boats = json.loads(sys.argv[1])
    for n in boats:
        check_and_update(n)