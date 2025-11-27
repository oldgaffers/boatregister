#!/usr/bin/env python3
import sys
import yaml
from os import listdir
from datetime import datetime
from helpers import dump

def get_boat(path):
  try:
    with open(path, "r", encoding='utf-8') as stream:
      return yaml.safe_load(stream)
  except Exception as e:
    print(e)
    print('OGA', path)
  return None

def update_owner(boat, status, firstname, lastname, id, member):
  dirty = False
  ownerships = boat.get('ownerships', [])
  name = f"{firstname} {lastname}".title()
  if status == 'Member':
    a = []
    b = []
    for ownership in ownerships:
      if ownership.get('name', None) == name and ownership.get('current', False):
        a.append(ownership)
        dirty = True
      else:
        b.append(ownership)
    for ownership in a:
      print(boat['oga_no'], ownership)
      del ownership['name']
      ownership['id'] = id
      ownership['member'] = member
    ownerships = [*a, *b]
  else:
    a = []
    b = []
    for ownership in ownerships:
      if ownership.get('id', None) == id:
        a.append(ownership)
        dirty = True
      else:
        b.append(ownership)
    for ownership in a:
      ownership['name'] = name
      del ownership['id']
      del ownership['member']
      if status == 'Non-member':
        pass
      elif status == 'Deceased':
        if ownership.get('current', False):
          del ownership['current']
        if 'end' not in ownership:
          ownership['end'] = datetime.now().year
      else:
        print('unknown status', status, firstname, lastname, id, member)
    ownerships = [*a, *b]
  if dirty:
    print('updated', boat['name'], boat['oga_no'])
    return { **boat, 'ownerships': ownerships }
  return None

def usage():
  print('usage: update_member_ownerships Member|Non-member|Deceased firstname lastname gold_id membership_number')

if __name__ == '__main__':
  if len(sys.argv) != 6:
    usage()
    exit()
  status = sys.argv[1]
  firstname = sys.argv[2]
  lastname = sys.argv[3]
  id = int(sys.argv[4])
  member = int(sys.argv[5])
  if status not in ['Member', 'Non-member', 'Deceased']:
    usage()
    exit()
  mypath='boat'
  boats = listdir(mypath)
  for b in boats:
    path = f"{mypath}/{b}/boat.yml"
    boat = get_boat(path)
    if boat is not None:
      updated = update_owner(boat, status, firstname, lastname, id, member)
      if updated is not None:
        with open(path, "w") as stream:
          dump(updated, stream)
