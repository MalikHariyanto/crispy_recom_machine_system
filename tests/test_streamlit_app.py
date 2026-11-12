"""Search-only SISRE interactions against the real dataset."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

class StreamlitAppTests(unittest.TestCase):
    def setUp(self):
        self.app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()

    def submit(self,text):
        self.app.text_input(key='sisre_query').set_value(text)
        next(b for b in self.app.button if b.label=='Cari').click().run()
        self.assertFalse(self.app.exception)

    def test_search_filters_and_reset(self):
        app=self.app
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('file_uploader')),0)
        self.assertEqual(len(app.sidebar.radio),0)
        app.selectbox(key='sisre_weather').set_value('Penghujan')
        app.selectbox(key='sisre_category').set_value('pantai')
        self.submit('pantai')
        result=app.session_state['sisre_results'][2]
        self.assertGreater(len(result),0)
        self.assertTrue(result.wisata.eq('pantai').all())
        self.assertTrue(result.rekomendasi_cuaca.eq('Kemarau & Penghujan').all())
        next(b for b in app.button if b.label=='Reset').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_input(key='sisre_query').value,'')
        self.assertIn('Jelajahi Madura',[h.value for h in app.subheader])

    def test_empty_and_unmatched_query(self):
        self.submit('')
        self.assertTrue(self.app.warning)
        self.submit('qzxwvunomatch')
        self.assertTrue(self.app.session_state['sisre_results'][2].empty)
        self.assertTrue(self.app.info)

    def test_load_more_preserves_search(self):
        self.submit('pantai')
        app=self.app
        before=len(app.session_state['sisre_results'][2])
        if before>6:
            next(b for b in app.button if b.label=='Lihat lebih banyak').click().run()
            self.assertEqual(app.session_state['sisre_limit'],12)
            self.assertEqual(len(app.session_state['sisre_results'][2]),before)
        self.assertFalse(app.exception)
