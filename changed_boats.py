from os import environ
import json

boats = []
files = environ['CHANGED_FILES']
for file in files.split(' '):
  if file.startswith('boat'):
    oga_no = int(file.split('/')[1])
    boats.append(oga_no)
print(f'CHANGED_BOATS={json.dumps(boats)}')
