import yaml
import json
from os import listdir
from pathlib import Path

boats = listdir('boat')
data = {}
for b in boats:
  boat = None
  try:
    with open(f"boat/{b}/boat.yml", "r") as stream:
      boat = yaml.safe_load(stream)
  except:
    print(b)
  if boat is not None:
    outdir = f"page-data/boat/{b}"
    Path(outdir).mkdir(parents=True, exist_ok=True)
    with open(f'{outdir}/page-data.json', 'w') as outfile:
      json.dump(boat, outfile)

