import json
import sys
import os
from datetime import datetime
import yaml
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
    text = f' ({oga_no})'
    r = smugmug.get(f'{sm}/api/v2/album!search',
        headers={'accept': 'application/json' },
        params={
            'Scope': '/api/v2/user/oga',
            'count': 100,
            'Text': text,
        }
    )
    if r.ok:
        rem = r.headers['x-ratelimit-remaining']
        print('calls in hand', rem)
        js = r.json()
        # print(json.dumps(dict(r.headers)))
        # print(json.dumps(r.request.url))
        # print(json.dumps(dict(r.request.headers)))
        # print(json.dumps(js))
        for a in js['Response'].get('Album', []):
          print(text, a['UrlName'], a['Title'])
          if a['UrlName'] == f'OGA-{oga_no}':
             return a
    elif r.status_code == 404:
        return None
    elif r.status_code == 429:
        rem = r.headers['x-ratelimit-remaining']
        res = int(r.headers['x-ratelimit-reset'])
        ret = r.headers.get('retry-after', None)
        if ret is None:
            print(429, r.reason, r.headers)
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
    r = smugmug.patch(f'{sm}{url}',
        headers={'Content-Type': 'application/json'},
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
    r = smugmug.get(f"{sm}{image['Uri']}")
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
    r = smugmug.post(f'{sm}/api/v2/image!addkeywords',
        headers={'Content-Type': 'application/json' },
        json={
            'Async': False,
            'ImageUris': urls,
            'Keywords': ';'.join(kw),
        }
    )
    if not r.ok:
        print(f'Error updating image keywords: {r.status_code} {r.text}')
        return
    print(json.dumps(r.json()))

def get_keywords(no):
    b = boat(no)
    kw = [b['name']]
    gt = b.get('generic_type', [])
    if type(gt) == str:
       gt = [gt]
    dc = b.get('design_class', {}).get('name', None)
    if dc is not None:
       kw.append(dc)
    pn = b.get('previous_names', [])
    return list(set(kw + gt + pn))

def add_kw(no):
    # print(f'OGA No, {no}!')
    album = get_album(no)
    if album is None:
        # print(f"OGA No {no} has no gallery")
        return
    add_kw_to_album(album)

def add_kw_to_album(album):
    print(album['UrlName'], album['Name'])
    no = album['UrlName'].split('-')[1]
    images = get_images(album)
    add_kw_to_images(images, no)

def get_images(album):
    imagesUri = album['Uris']['AlbumImages']['Uri']
    r = smugmug.get(f'{sm}{imagesUri}')
    if r.ok:
        js = r.json()
        return js['Response'].get('AlbumImage', [])
    else:
        print(f'Error fetching gallery name for {album ["Name"]}: {r.status_code}')
        return []

def add_kw_to_images(images, no):
    if len(images) == 0:
        return
    print(f'adding keywords to {len(images)} images for boat {no}')
    kw = get_keywords(no)
    print(json.dumps(kw))
    add_to_all(images, kw)

if __name__ == '__main__':
  if len(sys.argv) == 2:
      boats = json.loads(sys.argv[1])
      for b in boats:
          add_kw(b)
  if len(sys.argv) == 3:
    # boats = json.loads(sys.argv[1])
    start = int(sys.argv[1])
    count = int(sys.argv[2])
    r = smugmug.get('https://api.smugmug.com/api/v2/node/h4738Q!children',
        params = {'count': count, 'start': start},
    )
    if not r.ok:
        print(r.status_code, r.text)
        exit ()
    j = r.json()
    n = j['Response']['Node']
    for i in n :
        album = i ['Uris']['Album']['Uri']
        r = smugmug.get(f'{sm}{album}')
        if not r.ok:
            print(r.status_code)
            exit()
        j = r.json()
        a = j['Response']['Album']
        add_kw_to_album(a)