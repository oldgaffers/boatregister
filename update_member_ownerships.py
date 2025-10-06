#!/usr/bin/env python3
import sys
import yaml
from os import listdir
from helpers import dump

def get_boat(path):
  try:
    with open(path, "r", encoding='utf-8') as stream:
      return yaml.safe_load(stream)
  except Exception as e:
    print(e)
    print('OGA', path)
  return None

def update_owner(boat, action, firstname, lastname, id, member):
  updated = {**boat}
  dirty = False
  if not dirty:
    return None
  return updated

if __name__ == '__main__':
  action = sys.argv[1]
  status = sys.argv[2]
  firstname = sys.argv[3]
  lastname = sys.argv[4]
  id = sys.argv[5]
  member = sys.argv[6]
  mypath='boat'
  boats = listdir(mypath)
  for b in boats:
    path = f"{mypath}/{b}/boat.yml"
    boat = get_boat(path)
    if boat is not None:
      updated = update_owner(boat, action, firstname, lastname, id, member)
      if updated is not None:
        with open(path, "w") as stream:
          dump(updated, stream)
