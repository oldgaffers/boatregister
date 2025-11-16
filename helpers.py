from typing import OrderedDict
import json
from ruamel.yaml import YAML
from datetime import date, datetime
from markdownify import MarkdownConverter
from markdown import Markdown
from bs4 import Comment, Doctype, NavigableString, Tag

yaml = YAML()
yaml.default_flow_style=False
yaml.sort_keys=False
yaml.allow_unicode=True

class MD(str):
  @classmethod
  def to_yaml(cls, representer, node):
    return representer.represent_scalar('tag:yaml.org,2002:str', node, style='|')
  
yaml.register_class(MD)

MARKDOWN_EXTENSIONS = [
    "markdown_text_decorator",
    "sane_lists",
]

MARKDOWN_EXTENSION_CONFS={
    "markdown_text_decorator": { "priority": 90 }
}

md2html = Markdown(extensions=MARKDOWN_EXTENSIONS,
                   extension_configs=MARKDOWN_EXTENSION_CONFS)

omitFields = ['price','update_id', 'thumb', 'updated_at']

htmlFields = ['short_description', 'full_description', 'sales_text']

topLevelFields = [
  'name',
  'oga_no',
  'generic_type',
  'rig_type',
  'mainsail_type',
  'short_description',
  'full_description',
  'year',
  'year_is_approximate',
  'designer',
  'design_class',
  'builder',
  'place_built',
  'construction_material',
  'spar_material',
  'construction_method',
  'construction_details',
  'previous_names',
  'engine_installations',
  'selling_status',
  'for_sales',
  'dimensions',
  'home_country',
  'home_port',
  'hull_form',
  'reference',
  'sail_number',
  'fishing_number',
  'mssi',
  'ssr',
  'callsign',
  'uk_part1',
  'nhsr',
  'nsbr',
  'ownerships',
  'website',
  'image_key',
  'draft',
  'handicap_data',
  'created_at',
]


def json_serialise(obj):
  if isinstance(obj, date):
    return obj.isoformat()
  if isinstance(obj, datetime):
    return obj.isoformat(timespec='seconds')[:-6]+'Z'
  raise TypeError ("Type %s not serializable" % type(obj))

def ownerSortOrder(o):
  if 'start' in o:
    try:
      return int(o['start'])
    except:
      pass
  return 1800

def owner(o):
  fields = ['name', 'member', 'id', 'start', 'end', 'share', 'current', 'note', 'text']
  r = {}
  for field in fields:
    if field in o:
      r[field] = o[field]
  return r

def ownerships(os):
  if type(os) is list:
    owners = os
  else:
    if 'owners' in os:
      nonmembers = [o for o in os['owners'] if 'member' not in o]
      members = [o for o in os['owners'] if 'member' in o]
    else:
      nonmembers = []
      members = []
    if 'current' in os:
      m = []
      for c in os['current']:
        if 'id' in c:
          n = [{**n, **c, 'current': True} for n in members if 'id' in n and n['id'] == c['id']]
        else:
          n = [{**n, **c, 'current': True} for n in members if n['member'] == c['member']]
        if (len(n) > 0):
          m.append(n[0])
      members = m
    owners = members+nonmembers
  return sorted([owner(o) for o in owners], key=ownerSortOrder)

handicapFields = [
  'thcf',
  'calculated_thcf',
  'beam',
  'draft',
  'fore_triangle_height',
  'fore_triangle_base',  
  'length_overall',
  'length_on_deck',
  'length_on_waterline',
  'length_over_spars',
  'propellor',
  'sailarea',
  'main'
  'mizzen',
  'topsail',  
]

def map_handicap_data(b):
  boat = {**b}
  if 'handicap_data' in boat:
    h = boat['handicap_data']
  else:
    h = {}
  for f in ['beam','draft','length_on_deck']:
    if f in boat:
      h[f] = boat[f]
      del boat[f]
  r = {}
  for f in handicapFields:
    if f in h:
      if h[f]:
        r[f] = h[f]
      del h[f]
  boat['handicap_data'] = {**r, **h}
  return boat

def falsy(v):
  if v is None:
    return True
  if v == '':
    return True
  if v == 'null':
    return True
  if v == 'true':
    return True
  return False

def _is_block_content_element(el):
    """
    In a block context, returns:

    - True for content elements (tags and non-whitespace text)
    - False for non-content elements (whitespace text, comments, doctypes)
    """
    if isinstance(el, Tag):
        return True
    elif isinstance(el, (Comment, Doctype)):
        return False  # (subclasses of NavigableString, must test first)
    elif isinstance(el, NavigableString):
        return el.strip() != ''
    else:
        return False

def _next_block_content_sibling(el):
    """Returns the first next sibling that is a content element, else None."""
    while el is not None:
        el = el.next_sibling
        if _is_block_content_element(el):
            return el
    return None

class MyMarkdownConverter(MarkdownConverter):
  def __init__(self, **options):
    super().__init__(**options)

  def convert_list(self, el, text, parent_tags):
    next_sibling = _next_block_content_sibling(el)
    if 'li' in parent_tags:
      # remove trailing newline if we're in a nested list
      return '\n' + text.rstrip()
    return '\n\n\n' + text

def markdownify(html, **options):
  return MyMarkdownConverter(**options).convert(html)

def toMarkdown(html):
  return MD(markdownify(html, wrap=True, escape_asterisks=False, sub_symbol='^', sup_symbol='^^').strip())

def map_for_sale(fs):
  r = {k: v for k, v in fs.items() if not falsy(v)}
  if 'sales_text' in r:
    r['sales_text'] = toMarkdown(r['sales_text'])
  return r

def augment_from_pickers(boat, pickers):
  n = {}
  for field in ['builder','designer','design_class']:
    if field in boat:
      value = boat[field]
      if type(value) is dict:
        id = value['id']
      else:
        id = value
      values = [p for p in pickers[field] if p['id'] == id]
      if (len(values) > 0):
        n[field] = values[0]
  return {**boat, **n}

def map_boat(item, pickers):
  boat = {k: v for k, v in item.items() if not falsy(v) and k not in omitFields}
  if 'ownerships' in boat:
    boat['ownerships'] = ownerships(boat['ownerships'])
  if 'short_description' in boat:
    boat['short_description'] = toMarkdown(boat['short_description'])
  if 'full_description' in boat:
    html = boat['full_description']
    md = toMarkdown(html)
    boat['full_description'] = md
  if 'for_sales' in boat:
    boat['for_sales'] = [map_for_sale(fs) for fs in boat['for_sales']]
  if 'design_class' in boat:
    if 'examples' in boat['design_class']:
      del boat['design_class']['examples']
  boat['updated_at'] = date.today().strftime('%Y-%m-%d')
  boat = augment_from_pickers(boat, pickers)
  return map_handicap_data(boat)

def known_fields_first(data):
  boat = {}
  for field in topLevelFields:
    if field in data and data[field] is not None:
      f = data[field]
      boat[field] = f
      del data[field]
  for field in data.keys():
    if field not in boat:
      boat[field] = data[field]
  return boat

def unique(l):
  # assume all items similar
  if type(l[0]) == str:
    return list(set(l))
  else:
    return [json.loads(x) for x in list(set([json.dumps(x, default=json_serialise) for x in l]))]

def merge_object(existing, changes):
  if isinstance(existing, dict):
    merged = OrderedDict(**existing)
  else:
    merged = OrderedDict()
  for key in changes.keys():
    t = type(changes[key])
    if t == dict:
      if key in merged:
        merged[key] = merge_object(existing[key], changes[key])
      else:
        merged[key] = changes[key]
    elif t == list:
      if key in merged:
        merged[key] = unique(existing[key] + changes[key])
      else:
        merged[key] = changes[key]
    else:
      merged[key] = changes[key]
  return known_fields_first(merged)

def dump(dict, outfile):
  yaml.dump(dict, outfile)

def nullif(o, k):
  if k in o:
    return o[k]
  return None

def emptyif(o, k):
  if o is None:
    return {}
  if k in o:
    return o[k]
  return {}

def isHtml(s):
  if '<a href' in s:
    return True
  if '<div>' in s:
    return True
  if '<blockquote>' in s:
    return True
  if '<p>' in s:
    return True
  if '<span style' in s:
    return True
  if '<p style' in s:
    return True
  if '<br' in s:
    return True
  if '<li>' in s:
    return True
  return False

def mapHtmlField(k, v):
  if k in htmlFields and not isHtml(v):
    return md2html.convert(v)
  return v

def mapHtmlFields(d):
  return {k:mapHtmlField(k,v) for (k,v) in d.items()}

def process_html(boat):
  r = mapHtmlFields(boat)
  if 'for_sales' in boat:
    r['for_sales'] = [mapHtmlFields(fs) for fs in boat['for_sales']]
  return r