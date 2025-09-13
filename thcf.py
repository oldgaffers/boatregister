import math
from format import f2m

# Constants
baseLengthInFeetForTHCF = 25

# Helper Functions
def rig_allowance(r):
    r = r.lower()
    if r == 'cutter':
        return 0.96
    elif r == 'yawl':
        return 0.94
    elif r == 'schooner':
        return 0.92
    elif r == 'ketch':
        return 0.90
    return 1.0

def sails(r):
    r = r.lower()
    if r == 'cutter':
        return [
            'fore_triangle',
            'main',
            'topsail',
         ]
    elif r == 'yawl':
        return [
            'fore_triangle',
            'main',
            'topsail',
            'mizzen',
            'mizzen_topsail',
        ]
    elif r == 'schooner':
        return [
            'fore_triangle',
            'main',
            'topsail',
            'fore_sail',
            'fore_topsail',
        ]
    elif r == 'ketch':
        return [
            'fore_triangle',
            'main',
            'topsail',
            'mizzen',
            'mizzen_topsail',
        ]
    return []

def areas(boat):
    s = sails(boat.get('rig_type', ''))
    sail_areas = {}
    hd = boat.get('handicap_data', {})
    for sail in s:
        sail_areas[sail] = 0
        if sail == 'fore_triangle':
            sail_areas[sail] = fForeTriangle(hd)
        elif sail in ['main', 'fore_sail', 'mizzen']:
            sail_areas[sail] = fMainSA(hd.get(sail, {}))
        elif sail in ['topsail', 'fore_topsail', 'mizzen_topsail']:
            sail_areas[sail] = fTopSA(hd.get(sail, {}))
    return sail_areas

def fMainSA(sail):
    if not sail:
        return 0
    b = sail.get('foot', 0)
    h = sail.get('luff', 0)
    if b is None or h is None:
        return 0
    if 'head' not in sail:
        return 0.5 * b * h
    g = float(sail['head'])
    d = math.sqrt(b * b + h * h)
    return 0.5 * b * h + 0.5 * g * d

def fTopSA(sail):
    if sail:
        i = float(sail.get('perpendicular', 0))
        h = float(sail.get('luff', 0))
        return 0.5 * i * h
    return 0

def fForeTriangle(data):
    if data:
        i = float(data.get('fore_triangle_height', 0))
        j = float(data.get('fore_triangle_base', 0))
        return 0.425 * i * j
    return 0

def fL(data):
    if data and data.get('length_on_deck') and data.get('length_on_waterline'):
        return 0.5 * (data['length_on_deck'] + data['length_on_waterline'])
    return 0

def fBD(boat):
    if boat and boat.get('handicap_data') and boat['handicap_data'].get('beam'):
        return 0.67 * boat['handicap_data']['beam'] * boat['handicap_data']['beam']
    return 0

def fMSA(sail_area):
    return sum(sail_area.values())

def fSqrtS(rig_allowance, sailarea):
    return rig_allowance * math.sqrt(sailarea)

def fMR(boat):
    if 'rig_type' not in boat or 'handicap_data' not in boat:
        return 0
    handicap_data = boat['handicap_data']
    sails = areas(boat)
    if handicap_data:
        L = fL(handicap_data)
        sqrtS = fSqrtS(rig_allowance(boat['rig_type']), fMSA(sails))
        BD = fBD(boat)
        if BD > 0:
            x = 0.15 * L * sqrtS / math.sqrt(BD)
            y = 0.2 * (L + sqrtS)
            return x + y
    return 0

def fPropellorBonus(data):
    prop_type = data.get('propellor', {}).get('type', '')
    if prop_type == 'fixed':
        return 0.03
    elif prop_type == 'folding' or prop_type == 'feathering':
        return 0.015
    return 0

def fShoalBonus(R, boat):
    if boat and boat.get('handicap_data'):
        lwl = boat['handicap_data']['length_on_waterline']
        draft = boat['draft']
        nominal_draft = 0.16 * lwl - 0.04 * lwl
        bonus = 0
        if draft < 0.8 * nominal_draft:
            bonus = 0.02 * R
        if draft < 0.66 * nominal_draft:
            bonus = 0.02 * R
        if boat['hull_form'] in ['centre-boarder', 'centreboard dinghy', 'leeboarder']:
            bonus /= 2
        return bonus
    return 0

def fR(boat):
    if boat:
        MR = fMR(boat)
        return MR - MR * fPropellorBonus(boat['handicap_data'])
    return 0

def fThcf(boat):
    r = fR(boat)
    return 0.125 * (math.sqrt(r) + 3)

shapeFactorMap = {
    'Long keel - High volume': 0.25,
    'Long keel - Standard': 0.20,
    'Long keel - Low volume': 0.15,
    'Fin keel': 0.10,
}

def shapeFactors(sf):
    return shapeFactorMap.get(sf, 0.2)

def solentLength(data):
    LOD = data.get('length_on_deck', baseLengthInFeetForTHCF)
    LWL = data.get('length_on_waterline', baseLengthInFeetForTHCF)
    return f2m(0.5 * (LOD + LWL))

def solentEstimatedDisplacement(data):
    L = solentLength(data)
    B = f2m(data['beam'])
    D = f2m(data['draft'])
    SF = shapeFactors(data['solent']['hull_shape'])
    return round(1000 * L * B * D * SF)

def solentMR(boat):
    handicap_data = boat['handicap_data']
    L = solentLength(handicap_data)
    rS = f2m(boat['ddf'].get('root_s', 0.0))
    y = 0.67 * (L + rS)
    
    if handicap_data.get('displacement'):
        enteredDisplacement = handicap_data['displacement'] / 1000
        x = 0.2 * L * rS / math.sqrt(enteredDisplacement / L)
        return x + y
    else:
        B = f2m(handicap_data['beam'])
        D = f2m(handicap_data['draft'])
        SF = shapeFactors(handicap_data['solent']['hull_shape'])
        x = 0.2 * L * rS / math.sqrt(B * D * SF)
        return x + y

def solentRating(boat):
    data = boat['handicap_data']
    mmrf = data['solent']['measured_rating']
    thcf = fThcf(mmrf * (1 - boat['ddf']['prop_allowance']))
    pf = float(data['solent'].get('performance_factor', 0))
    sr = (1 + pf) * thcf
    return round(1000 * sr) / 1000
