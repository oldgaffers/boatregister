from os import environ
import json

boats = []
files = environ['CHANGED_FILES']
print(f'CHANGED_BOATS_INPUT={files}')
for file in files.split(' '):
  if file.startswith('boat'):
    print(f'CHANGED_BOATS_FILE_{file}=wanted')
    oga_no = int(file.split('/')[1])
    boats.append(oga_no)
  else:
    print(f'CHANGED_BOATS_FILE_{file}=not wanted')
print(f'CHANGED_BOATS={json.dumps(boats)}')
