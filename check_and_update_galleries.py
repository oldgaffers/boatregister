import json
import sys
import os
import yaml
import requests
from requests_oauthlib import OAuth1Session

cs = os.environ.get('SMUGMUG_CLIENT_SECRET', 'n/a')
sac = os.environ.get('SMUGMUG_SECRET_ACCESS_KEY', 'n/a')
ac = os.environ.get('SMUGMUG_ACCESS_KEY', 'n/a')
api_key = os.environ.get('SMUGMUG_API_KEY', 'n/a')
sm = 'https://api.smugmug.com'

def getRequestsHandler():
    session = OAuth1Session(api_key,
        client_secret=cs,
        resource_owner_key=ac,
        resource_owner_secret=sac
    )
    session.headers.update({'accept': 'application/json'})
    return session

smugmug = getRequestsHandler()

def get_album(oga_no):
    text = f'({oga_no})'
    r = smugmug.get(f'{sm}/api/v2/album!search',
        headers={'accept': 'application/json' },
        params={
            'APIKey': api_key,
            'Scope': '/api/v2/user/oga',
            'SortDirection': 'Descending',
            'SortMethod': 'Rank',
            'Text': text,
        }
    )
    if r.ok:
        js = r.json()
        r = js['Response']['Album']
        for a in r:
          if a['UrlName'] == f'OGA-{oga_no}':
             return a
    else:
        print(f'Error fetching gallery name for {oga_no}: {r.status_code}')
    return None

def boat_name(no):
    with open(f"boat/{no}/boat.yml", "r", encoding='utf-8') as stream:
      boat = yaml.safe_load(stream)
    return boat['name']

def update_gallery_name(no, album, new_name):
    print(album['Uri'])
    r = smugmug.patch(f'https://api.smugmug.com{album["Uri"]}',
        headers={'accept': 'application/json', 'Content-Type': 'application/json' },
        json={
            'Title': new_name,
        }
    )
    if not r.ok:
        print(f'Error updating gallery name for {no}: {r.status_code} {r.text}')
        return
    print(f'Gallery name for {no} updated to {new_name}')

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