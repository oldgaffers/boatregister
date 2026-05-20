import fileinput
import json

boats = []
files = ' '.join(list(fileinput.input()))
print(f'CHANGED_BOATS_INPUT={files}')
for file in files.split(' '):
  try:
    if '/boat/' in file:
      print(f'CHANGED_BOATS_FILE_{file}=wanted')
      p = file.split('/')
      n = 1 if p[0] == 'boat' else 2
      n = 2 if p[1] == 'boat' else 1
      oga_no = int(p[n])
      boats.append(oga_no)
    else:
      print(f'CHANGED_BOATS_FILE_{file}=not wanted')
  except:
    pass
print(f'BOATS={json.dumps(boats)}')
