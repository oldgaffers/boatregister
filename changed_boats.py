import fileinput
import json

boats = []
files = ' '.join(list(fileinput.input()))
print(f'CHANGED_BOATS_INPUT={files}')
for file in files.split(' '):
  try:
    if file.startswith('boat'):
      print(f'CHANGED_BOATS_FILE_{file}=wanted')
      oga_no = int(file.split('/')[1])
      boats.append(oga_no)
    else:
      print(f'CHANGED_BOATS_FILE_{file}=not wanted')
  except:
    pass
print(f'BOATS={json.dumps(boats)}')
