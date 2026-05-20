import sys
import json

boats = []
files = input()
print(f'CHANGED_BOATS_INPUT={files}', file=sys.stderr)
for file in files.split(' '):
  try:
    if '/boat/' in file:
      print(f'CHANGED_BOATS_FILE_{file}=wanted', file=sys.stderr)
      p = file.split('/')
      n = 1 if p[0] == 'boat' else 2
      n = 2 if p[1] == 'boat' else 1
      oga_no = int(p[n])
      boats.append(oga_no)
    else:
      print(f'CHANGED_BOATS_FILE_{file}=not wanted', file=sys.stderr)
  except:
    pass
print(f'BOATS={json.dumps(boats)}')
