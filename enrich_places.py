import json
import re
import requests
import time
import sys

# Basic lookup for UK ceremonial counties (expand as needed)
COUNTY_LOOKUP = {
    "Maldon": "Essex",
    "Falmouth": "Cornwall",
    "Ashurst": "Hampshire",
    "St Columb": "Cornwall",
    "Southend on Sea": "Essex",
    "Littlehampton": "West Sussex",
    "Mylor Bridge": "Cornwall",
    "Boston": "Lincolnshire",
    "Heybridge": "Essex",
    "Wadebridge": "Cornwall",
    "Totnes": "Devon",
    "Ipswich": "Suffolk",
    "Woodbridge": "Suffolk",
    "Lymington": "Hampshire",
    "Dartmouth": "Devon",
    "Burnham-on-Crouch": "Essex",
    "Brightlingsea": "Essex",
    "Truro": "Cornwall",
    "Mevagissey": "Cornwall",
    "Great Yarmouth": "Norfolk",
    "Liverpool": "Merseyside",
    "Scarborough": "North Yorkshire",
    "Whitstable": "Kent",
    "Ramsgate": "Kent",
    "Poole": "Dorset",
    "Southampton": "Hampshire",
    "Bosham": "West Sussex",
    "Bembridge": "Isle of Wight",
    "Cowes": "Isle of Wight",
    "Leigh on Sea": "Essex",
    "Plymouth": "Devon",
    "Bristol": "Bristol",
    "Cardiff": "Cardiff",
    "London": "London",
    # ... add more as needed ...
}

OS_API_KEY = "WVR4YmhGPIkjdukzjehGWp9A6HSsbDJQ"

# Helper to infer country from place name
NON_UK_COUNTRIES = [
    (r"France|Brittany|Cherbourg|Granville|Benodet|Camaret|Cancale|Bordeaux|Marennes|Pont L'Abbe Bretagne|Carantec|Sables d'Olones|Paimpol", "France"),
    (r"Sweden|Goteborg|Landskrona|Simrishamn|Koping|Listerby|Lofhomsvarfet|Raa|Kristinehamn|Stockholm|Faro|Kungsor", "Sweden"),
    (r"Norway|Vestnes|Ulvik|Risor|Larvik|Grimstad|Rana Fjord|Innvik|Hagavik|Rosendal", "Norway"),
    (r"USA|Patchogue, NY|Cape Cod|Maine|Rhode Island|Connecticut|Florida|California|Astoria Oregon|Woonsocket RI|Pensacola Florida|Quincy MA|Neponset, S Boston, MA|South Dartmouth MA|Westport Mass|Marshfield USA|Clearwater, Florida", "USA"),
    (r"Netherlands|Holland|Amsterdam|Alphen|Gaastmeer|Jirnsum|Leeuwarden|Papendrecht|Gorinchem|Warga|Den Helder|Edam|Boom, NL|Sneek, Friesland|Groningen|Zwyndrecht|Reeuwijk|Lekkekerk", "Netherlands"),
    (r"Belgium|Antwerp|Ostende|Walsoorden|Brussels", "Belgium"),
    (r"Germany|Bremen|Elbe|Hamburg|Warnemunde|Stade|Neuhaus an der Oste|Gluckstadt|Mittelburg", "Germany"),
    (r"Ireland|Dublin|Galway|Cork|Connemara|Wexford|Donegal|Malahide|Carna|Ross Muck Eire|Portavogie|Bangor Co Down|Groomsport Co Down|Arklow|Carrickfergus|Dunlaoghaire|Dun Laoghaire|Dún Laoghaire|Maguineshridge, Fermanagh", "Ireland"),
    (r"Canada|Nova Scotia|Victoria BC|Burnaby B.C.|Dundas Ontario|Parry Sound, Ontario|Comox BC", "Canada"),
    (r"Australia|Sydney Australia|Fremantle,WA|Western Australia|W Australia|Hornsby, N.S.W. Australia|La Perouse New S Wales", "Australia"),
    (r"Denmark|Troense|Nykobing Mors|Gilleleje|Horne, Faaborg|Lynaes|Marstal|Vejle|Odense|Hardinxveld", "Denmark"),
    (r"Spain|Valencia|Almeira|Spain/Maldon|Livorno IT", "Spain"),
    (r"Sri Lanka|Shri Lanka|Sri Lanka/Yarmouth", "Sri Lanka"),
    (r"New Zealand|Whangerei|Gisbourne New Zealand", "New Zealand"),
    (r"Finland|Abo Finland|Sipu,Finland", "Finland"),
    (r"Cyprus|Kyrenia, Cyprus", "Cyprus"),
    (r"Greece|Syros, Greece", "Greece"),
    (r"Brazil|Cajaiba, Bahia, Brazil", "Brazil"),
    (r"Oman|Wudam, Sultanate of Oman", "Oman"),
    (r"Thailand", "Thailand"),
    (r"Poland", "Poland"),
    (r"Malta", "Malta"),
    (r"Bermuda", "Bermuda"),
    # ... add more as needed ...
]

def infer_country(place):
    # Direct country/province/city match
    place_lower = place.lower().strip()
    # List of known countries and regions
    known_countries = [
        "france", "sweden", "norway", "usa", "united states", "netherlands", "holland", "belgium", "germany", "ireland", "canada", "australia", "denmark", "spain", "sri lanka", "new zealand", "finland", "cyprus", "greece", "brazil", "oman", "thailand", "poland", "malta", "bermuda", "isle of man", "scotland", "wales", "england"
    ]
    for country in known_countries:
        if place_lower == country or country in place_lower:
            # Normalize some country names
            if country == "usa" or country == "united states":
                return "USA"
            if country == "holland":
                return "Netherlands"
            if country == "isle of man":
                return "Isle of Man"
            if country == "england" or country == "scotland" or country == "wales":
                return "United Kingdom"
            return country.title()
    # Regex pattern match fallback
    for pattern, country in NON_UK_COUNTRIES:
        if re.search(pattern, place, re.IGNORECASE):
            return country
    return "United Kingdom"

def os_lookup_county(place):
    url = f"https://api.os.uk/search/names/v1/find?query={place}&key={OS_API_KEY}"
    # Allowed LOCAL_TYPEs
    ALLOWED_LOCAL_TYPES = {
        "Hamlet",
        "Other Settlement",
        "Suburban Area",
        "Island",
        "City",
        "Port Consisting of Docks and Nautical Berthing",
        "Harbour",
        "Village",
        "Town"
    }
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            # Collect LOCAL_TYPEs for this lookup
            local_types = set(r.get('GAZETTEER_ENTRY', {}).get('LOCAL_TYPE', '') for r in results)
            os_lookup_county.local_types_seen.update(local_types)
            # Filter results by allowed LOCAL_TYPEs
            filtered = [r for r in results if r.get('GAZETTEER_ENTRY', {}).get('LOCAL_TYPE', '') in ALLOWED_LOCAL_TYPES]
            best = filtered[0] if filtered else None
            if best:
                entry = best.get('GAZETTEER_ENTRY', {})
                county = entry.get('COUNTY_UNITARY', '')
                geometry_x = entry.get('GEOMETRY_X', None)
                geometry_y = entry.get('GEOMETRY_Y', None)
                return county, geometry_x, geometry_y
            with open("places.log", "a", encoding="utf-8") as log:
                log.write(f"[OS API] No suitable result for place: '{place}' (API response: {results})\n")
            return '', None, None
        else:
            with open("places.log", "a", encoding="utf-8") as log:
                log.write(f"[OS API] Error for place: '{place}' (HTTP {resp.status_code})\n")
            return '', None, None
    except Exception as e:
        with open("places.log", "a", encoding="utf-8") as log:
            log.write(f"[OS API] Exception for place: '{place}' - {e}\n")
        return '', None, None

# Set to collect all LOCAL_TYPEs seen
os_lookup_county.local_types_seen = set()

def infer_county(place):
    # First try local lookup
    county = COUNTY_LOOKUP.get(place, "")
    if county:
        return county, None, None
    # If not found, try OS API for UK places
    # Only call API if likely UK place (not mapped to other country)
    return os_lookup_county(place)

def main():
    with open("places.json", "r", encoding="utf-8") as f:
        places = json.load(f)
    enriched = []
    # Support both dict-of-counts and dict-of-objects input
    if isinstance(places, dict):
        items = places.items()
    elif isinstance(places, list):
        items = [(obj.get("place", ""), obj) for obj in places]
    else:
        print("Unsupported input format for places.json")
        return

    for place, obj in items:
        if isinstance(obj, int):
            obj = {"place": place, "count": obj}
        country = infer_country(place)
        ceremonial_county = ""
        geometry_x = None
        geometry_y = None
        if country == "United Kingdom":
            ceremonial_county, geometry_x, geometry_y = infer_county(place)
            time.sleep(0.2)
        obj["country"] = country
        obj["ceremonial_county"] = ceremonial_county
        if geometry_x is not None:
            obj["geometry_x"] = geometry_x
        if geometry_y is not None:
            obj["geometry_y"] = geometry_y
        enriched.append(obj)
    with open("places_enriched.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    # Log the set of all LOCAL_TYPEs seen
    with open("places.log", "a", encoding="utf-8") as log:
        log.write(f"[OS API] All LOCAL_TYPEs seen: {os_lookup_county.local_types_seen}\n")

if __name__ == "__main__":
    main()
