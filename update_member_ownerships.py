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
    for os in ownerships:
      if os.get('name', None) == name:
        a.append(os)
        dirty = True
      else:
        b.append(os)
    for os in a:
      print(boat['oga_no'], os)
      del os['name']
      os['id'] = id
      os['member'] = member
    ownerships = [*a, *b]
  else:
    a = []
    b = []
    for os in ownerships:
      if os.get('id', None) == id:
        a.append(os)
        dirty = True
      else:
        b.append(os)
    for os in a:
      os['name'] = name
      del os['id']
      del os['member']
      if status == 'Non-member':
        pass
      elif status == 'Deceased':
        if boat.get('current', False):
          del boat['current']
        if 'end' not in boat:
          os['end'] = datetime.now().year
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
