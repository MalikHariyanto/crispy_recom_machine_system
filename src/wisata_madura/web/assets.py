"""Curated covers/location metadata, bound to both destination ID and name."""
from functools import lru_cache
from pathlib import Path
from html import escape
import base64
import json

ROOT=Path(__file__).resolve().parents[3]
DIRECTORY=ROOT/'assets/destinations'
MANIFEST=DIRECTORY/'manifest.json'


def enrich_catalog(catalog):
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {'destinations':{}}
    metadata=manifest['destinations']
    result=catalog.copy()
    areas,covers,positions=[],[],[]
    for row in result.itertuples():
        entry=metadata.get(str(row.id_destinasi),{})
        if entry.get('name')!=row.destinasi:
            entry={}
        filename=entry.get('cover','')
        path=DIRECTORY/filename
        valid=filename and Path(filename).name==filename and path.suffix=='.webp' and path.is_file()
        areas.append(entry.get('area',''));covers.append(str(path) if valid else '')
        positions.append(entry.get('position','50% 50%'))
    return result.assign(daerah=areas,cover_path=covers,cover_position=positions)


@lru_cache(maxsize=96)
def _encoded_image(path,modified_ns):
    return base64.b64encode(Path(path).read_bytes()).decode('ascii')


def cover_markup(row):
    path=Path(row.cover_path)
    encoded=_encoded_image(str(path),path.stat().st_mtime_ns)
    # Positions are curated percentages, not arbitrary HTML or CSS.
    import re
    position=row.cover_position if re.fullmatch(r'\d{1,3}% \d{1,3}%',row.cover_position) else '50% 50%'
    return (f'<img class="destination-photo" src="data:image/webp;base64,{encoded}" '
            f'alt="{escape(str(row.destinasi),quote=True)}" '
            f'style="position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:cover;object-position:{position}" width="640" height="360">')
