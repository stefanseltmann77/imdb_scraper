import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def scraper():
    from imdb_scraper import IMDBScraper
    return IMDBScraper("")


class TestIMDBScraper:

    def test__parse_year_from_title(self, scraper):
        assert scraper._parse_year_from_title("Carlos (TV Mini-Series 2010– )") == 2010

    def test_parse_genre_from_soup(self, scraper):
        website = """<div class="subtext">12<span class="ghost">|</span><time datetime="PT152M">2h 32min
            </time>    <span class="ghost">|</span><a href="/genre/Action?ref_=tt_ov_inf">Action</a>, 
            <a href="/genre/Adventure?ref_=tt_ov_inf">Adventure</a>,<a href="/genre/Fantasy?ref_=tt_ov_inf">Fantasy</a>
            <a href="/genre/Sci-Fi?ref_=tt_stry_gnr"> Sci-Fi</a>
            <span class="ghost">|</span><a href="/title/tt2527336/releaseinfo?ref_=tt_ov_inf" title="See 
            more release dates" >14 December 2017 (Germany)</a></div>"""
        soup = BeautifulSoup(website, 'html.parser')
        result = scraper._parse_genre_from_soup(soup)
        assert result == {'Adventure', 'Fantasy', 'Action', 'Sci-Fi'}

    def test__parse_rating_from_soup(self, scraper):
        website = """<div class="imdbRating"><div class="ratingValue"><strong title="7,2 based on 413.699 user ratings">
            <span>7,2</span></strong><span class="grey">/</span><span class="grey">10</span></div>
            <a href="/title/tt2527336/ratings?ref_=tt_ov_rt"><span class="small">413.699</span></a>
            <div class="hiddenImportant"><span>5.564 user</span><span>648 critic</span></div></div>"""
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_rating_from_soup(soup) == {'rating_imdb': 7.2, 'rating_imdb_count': 413699}

    def test__parse_fsk_from_soup(self, scraper):
        website = """<li class="ipl-inline-list__item"> <a href="/search/title?certificates=DE:16">Germany:16</a> 
                     (bw) </li>"""
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_fsk_from_soup(soup) == 16
        website = """<li class="ipl-inline-list__item">
                                    <a href="/search/title?certificates=DE:16">Germany:16</a>
                                </li>"""
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_fsk_from_soup(soup) == 16
        website = """<li class="ipl-inline-list__item">
                                    <a href="/search/title?certificates=DE:12">Germany:12</a>
                                </li>"""
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_fsk_from_soup(soup) == 12
