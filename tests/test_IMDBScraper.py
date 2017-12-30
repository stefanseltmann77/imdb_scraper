from unittest import TestCase
from imdb_scraper import IMDBScraper

class TestIMDBScraper(TestCase):

    def setUp(self):
        self.instance = IMDBScraper("")

    def test__parse_year_from_title(self):
        self.assertEqual(self.instance._parse_year_from_title("Carlos (TV Mini-Series 2010– )"), 2010)
