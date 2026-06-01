import json
import sys
import os
from datetime import datetime
import yaml
import requests
from requests_oauthlib import OAuth1Session

cs = os.environ.get('SMUGMUG_CLIENT_SECRET', 'n/a')
sac = os.environ.get('SMUGMUG_SECRET_ACCESS_KEY', 'n/a')
ac = os.environ.get('SMUGMUG_ACCESS_KEY', 'n/a')
api_key = os.environ.get('SMUGMUG_API_KEY', 'n/a')

def getRequestsHandler():
    return OAuth1Session(api_key,
        client_secret=cs,
        resource_owner_key=ac,
        resource_owner_secret=sac
    )

def get_album(oga_no):
    text = f'({oga_no})'
    r = requests.get(f'https://api.smugmug.com/api/v2/album!search',
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
        rem = r.headers['x-ratelimit-remaining']
        print('calls in hand', rem)
        js = r.json()
        r = js['Response'].get('Album'], [])
        for a in r:
          if a['UrlName'] == f'OGA-{oga_no}':
             return a
    elif r.status_code == 404:
        return None
    elif r.status_code == 429:
        rem = r.headers['x-ratelimit-remaining']
        res = int(r.headers['x-ratelimit-reset'])
        ret = r.headers.get('retry-after', None)
        if ret is None:
            print(429, r.headers)
        else:
            print('rate limited', rem, res, ret)
            print(datetime.fromtimestamp(res))
        exit()
    else:
        print(r.status_code)
    return None

def boat(no):
    with open(f"boat/{no}/boat.yml", "r", encoding='utf-8') as stream:
      boat = yaml.safe_load(stream)
    return boat

def update_kw(url, kw):
    smugmug = getRequestsHandler()
    r = smugmug.patch(f'https://api.smugmug.com{url}',
        headers={'accept': 'application/json', 'Content-Type': 'application/json' },
        json={
            'KeywordArray': kw,
        }
    )
    if not r.ok:
        print(f'Error updating image keywords: {r.status_code} {r.text}')
        return

def update_all(images, kw):
    for image in images:
        ekw = image['KeywordArray']
        m = list(set(ekw + kw))
        if m != ekw:
            update_kw(image["Uri"], m)

def image_uri1(image):
    r = requests.get(f"https://api.smugmug.com{image['Uri']}",
        headers={'accept': 'application/json' },
        params={'APIKey': api_key}
    )
    if r.ok:
        js = r.json()
        res = js['Response']
        if 'AlbumImage' in res:
            return res['AlbumImage']['Uris']['Image']['Uri']
    return None

def image_uri(image):
    return f"/api/v2/image/{image['ImageKey']}"

def add_to_all(images, kw):
    urls = [image_uri(image) for image in images]
    smugmug = getRequestsHandler()
    r = smugmug.post(f'https://api.smugmug.com/api/v2/image!addkeywords',
        headers={'accept': 'application/json', 'Content-Type': 'application/json' },
        json={
            'Async': True,
            'ImageUris': urls,
            'Keywords': ';'.join(kw),
        }
    )
    if not r.ok:
        print(f'Error updating image keywords: {r.status_code} {r.text}')
        return

def get_keywords(no):
    b = boat(no)
    kw = [b['name']]
    gt = b.get('generic_type', [])
    if type(gt) == str:
       gt = [gt]
    dc = b.get('design_class', {}).get('name', None)
    if dc is not None:
       kw.append(dc)
    return kw + gt

def add_kw(no):
    print(f'OGA No, {no}!')
    album = get_album(no)
    if album is None:
        print(f"OGA No {no} has no gallery")
        return
    imagesUri = album['Uris']['AlbumImages']['Uri']
    url = f'https://api.smugmug.com{imagesUri}'
    r = requests.get(url,
        headers={'accept': 'application/json' },
        params={'APIKey': api_key}
    )
    if r.ok:
        js = r.json()
        images = js['Response']['AlbumImage']
    else:
        print(f'Error fetching gallery name for {no}: {r.status_code}')
        return
    kw = get_keywords(no)
    add_to_all(images, kw)

if __name__ == '__main__':
  if len(sys.argv) == 2:
    boats = json.loads(sys.argv[1])
    for n in boats:
        add_kw(n)