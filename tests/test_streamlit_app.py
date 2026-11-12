"""Exercise actual Streamlit reruns and the shipped bundle."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class StreamlitAppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()

    def test_navigation_and_live_search(self):
        app = self.app
        self.assertFalse(app.exception)
        app.text_input[0].set_value("pantai pasir putih")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertIn("Pilihan untuk perjalananmu", [s.value for s in app.subheader])
        self.assertGreater(len(app.session_state["search_result"][3]), 0)
        for page in ["Katalog destinasi", "Insight data", "Tentang", "Jelajahi"]:
            app.sidebar.radio[0].set_value(page).run()
            self.assertFalse(app.exception, page)
        self.assertIn("Pilihan untuk perjalananmu", [s.value for s in app.subheader])

    def test_empty_and_unmatched_query(self):
        app = self.app
        app.button[0].click().run()
        self.assertTrue(app.warning)
        app.text_input[0].set_value("qzxwvunomatch")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["search_result"][3].empty)
