import yaml
import sys

def get_boat(path):
  with open(path, "r") as stream:
    try: 
      boat = yaml.safe_load(stream)
    except Exception as e:
      print(e)
      print('OGA', path)
      boat = None
  if boat is None:
    return None
  else:
    return boat

if __name__ == '__main__':
  oga_no = sys.argv[1]
  field = sys.argv[2]
  boat = get_boat(f"boat/{oga_no}/boat.yml")
  print(f'{field}={boat[field]}')