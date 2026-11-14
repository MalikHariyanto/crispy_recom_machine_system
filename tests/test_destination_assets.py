"""Covers must be explicitly matched, local, and safe when metadata is missing."""
import json
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch
import tempfile
import pandas as pd
from PIL import Image

from wisata_madura.web.assets import enrich_catalog,cover_markup,DIRECTORY,MANIFEST
from wisata_madura.web.runtime import load_data

class DestinationAssetTests(unittest.TestCase):
    def test_known_covers_regions_and_unknown_destinations(self):
        catalog,_=load_data()
        bangkalan=catalog.loc[catalog.id_destinasi.eq('21')].iloc[0]
        self.assertEqual(bangkalan.daerah,'Bangkalan')
        self.assertTrue(Path(bangkalan.cover_path).is_file())
        html=cover_markup(bangkalan)
        self.assertIn('data:image/webp;base64,',html)
        self.assertIn('Alun Alun Bangkalan',html)
        self.assertIn('object-position:',html)
        manifest=json.loads(MANIFEST.read_text())
        self.assertEqual(len(manifest['photos']),25)
        self.assertEqual(catalog.cover_path.ne('').sum(),22)
        self.assertEqual(catalog.loc[catalog.id_destinasi.eq('73'),'daerah'].item(),'Sampang')
        self.assertTrue(catalog.loc[catalog.id_destinasi.eq('24'),'cover_path'].item())
        jaddih=manifest['destinations']['29']
        self.assertEqual(jaddih['source_filename'],'Bukit Jaddih.png')
        self.assertEqual(
            [photo['source_filename'] for photo in manifest['photos'] if photo['assignment']=='pending'],
            ['Fishing boats under a coastal tree.png'],
        )
        self.assertEqual(
            {photo['destination_name'] for photo in manifest['photos'] if photo['assignment']=='not_in_catalog'},
            {'Pantai Sembilan','Pantai Watu Leter'},
        )
        self.assertNotIn('Pantai Sembilan',set(catalog.destinasi))
        for photo in manifest['photos']:
            self.assertEqual(hashlib.sha256((DIRECTORY/photo['file']).read_bytes()).hexdigest(),photo['sha256'])
            if photo['assignment'].isdigit():
                self.assertEqual(manifest['destinations'][photo['assignment']]['cover'],photo['file'])
        for row in catalog.itertuples():
            if row.cover_path:
                with Image.open(row.cover_path) as image:
                    self.assertEqual(image.format,'WEBP')
                    self.assertLessEqual(image.width,1280)

    def test_id_name_mismatch_and_missing_file_do_not_assign_wrong_cover(self):
        incoming=pd.DataFrame([dict(id_destinasi='21',destinasi='Other place'),dict(id_destinasi='unknown',destinasi='Unknown')])
        result=enrich_catalog(incoming)
        self.assertTrue(result.cover_path.eq('').all())
        self.assertTrue(result.daerah.eq('').all())
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'manifest.json'
            path.write_text(json.dumps({'destinations':{'21':{'name':'Other place','cover':'../../private.webp','area':'Bangkalan'}}}))
            with patch('wisata_madura.web.assets.MANIFEST',path):
                result=enrich_catalog(incoming)
                self.assertTrue(result.cover_path.eq('').all())
