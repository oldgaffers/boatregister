import math

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

def fGaffSA(sail):
    if sail:
        b = float(sail['foot'])
        h = float(sail['luff'])
        g = float(sail['head'])
        d = math.sqrt(b * b + h * h)
        return 0.5 * b * h + 0.5 * g * d
    return 0

def fTopSA(sail):
    if sail:
        i = float(sail['perpendicular'])
        h = float(sail['luff'])
        return 0.5 * i * h
    return 0

def fForeTriangle(data):
    if data:
        i = float(data['fore_triangle_height'])
        j = float(data['fore_triangle_base'])
        return 0.425 * i * j
    return 0

def fL(data):
    if data and data.get('length_on_deck') and data.get('length_on_waterline'):
        return 0.5 * (data['length_on_deck'] + data['length_on_waterline'])
    return 0

def fBD(boat):
    return 0.67 * boat['handicap_data']['beam'] * boat['handicap_data']['beam']

def fMSA(sail_area):
    return sum(sail_area.values())

def fSqrtS(rig_allowance, sailarea):
    return rig_allowance * math.sqrt(sailarea)

def fMR(boat):
    ddf = boat['ddf']
    handicap_data = boat['handicap_data']
    if handicap_data:
        L = fL(handicap_data)
        sqrtS = ddf.get('root_s', 0.0)
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

def fThcf(r=baseLengthInFeetForTHCF):
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

# Example for f2m conversion function
def f2m(feet):
    return feet * 0.3048

