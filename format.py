ONE_FOOT = 0.3048

METRE_KEYS = [
    'beam', 'draft', 'draft_keel_down', 'air_draft',
    'perpendicular', 'luff', 'head', 'leech', 'foot',
    'length_on_deck', 'length_on_waterline', 'length_over_all',
    'length_over_spars', 'length_overall',
    'fore_triangle_height', 'fore_triangle_base',
]
SQUARE_METRE_KEYS = ['sailarea']
BOOLEAN_KEYS = ['year_is_approximate']

def format_designer_builder(b, k):
    data = b.get(k) if b else None
    if data and isinstance(data, dict) and 'name' in data:
        return data['name']
    if isinstance(data, list):
        return ' / '.join(d.get('name') for d in data if d and 'name' in d)
    return None

def price(n):
    if n == 0:
        return 'offers'
    return f"£{n:,.2f}"

def m2dfn(val):
    if val:
        return round(1000 * val / ONE_FOOT) / 1000

def m2df(val):
    if val:
        return f"{m2dfn(val):.2f}"

def feet(n):
    return f"{n:.2f} ft"

def squarefeet(n):
    return f"{n:.2f} ft²"

def kg(n):
    if n:
        return f"{int(n)} kg"

def m2f(val):
    if val:
        return feet(m2dfn(val))

def m2f2(val):
    if val:
        return squarefeet(val / ONE_FOOT / ONE_FOOT)

def m2dsqf(val):
    if val:
        return f"{val / ONE_FOOT / ONE_FOOT:.3f}"

def m2dsqfn(val):
    if val:
        return round(val / ONE_FOOT / ONE_FOOT, 3)

def f2m(val):
    if val:
        return round(1000 * ONE_FOOT * val) / 1000

def f2m2(val):
    if val:
        return round(1000 * ONE_FOOT * ONE_FOOT * val) / 1000

def boatm2f(obj):
    if obj is None:
        return None
    if isinstance(obj, list):
        return [boatm2f(n) for n in obj]
    elif isinstance(obj, dict):
        r = {}
        for k, v in obj.items():
            if k in METRE_KEYS:
                r[k] = m2dfn(v)
            elif k in SQUARE_METRE_KEYS:
                r[k] = m2dsqfn(v)
            elif k in BOOLEAN_KEYS:
                r[k] = bool(v)
            elif v:
                r[k] = boatm2f(v)
        return r
    else:
        return obj

def boatf2m(obj):
    if obj is None:
        return obj
    if isinstance(obj, list):
        return [boatm2f(n) for n in obj]
    elif isinstance(obj, dict):
        r = {}
        for k, v in obj.items():
            if k in METRE_KEYS:
                r[k] = f2m(v)
            elif k in SQUARE_METRE_KEYS:
                r[k] = f2m2(v)
            elif k in BOOLEAN_KEYS:
                r[k] = bool(v)
            else:
                r[k] = boatf2m(v) if v else v
        return r
    else:
        return obj

def boat_defined(value):
    if value is False:
        return False
    if not value:
        return None
    if isinstance(value, list):
        if len(value) == 0:
            return None
        return [item for item in (boat_defined(n) for n in value) if item]
    if isinstance(value, dict):
        if len(value) > 0:
            return {key: val for key, val in ((k, boat_defined(v)) for k, v in value.items()) if val is not None}
    return value

def m2fall(o):
    if o:
        return [m2dfn(o[k]) for k in o]

def newest_for_sale_record(boat):
    if not boat or not boat.get('for_sales'):
        return {'created_at': '1970-01-01T00:00:00Z'}
    return max(boat['for_sales'], key=lambda fs: fs.get('created_at', '1970-01-01T00:00:00Z'))
