import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def scraper():
    from imdb_assetscraper.imdb_assetscraper import IMDBAssetScraper
    return IMDBAssetScraper("")


class TestIMDBScraper:

    def test__parse_year_from_soup(self, scraper):
        website = '<h1 class="">Total Recall&nbsp;<span id="titleYear">' \
                  '(<a href="/year/2012/?ref_=tt_ov_inf">2012</a>)</span></h1>'
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_year_from_soup(soup) == 2012

    def test_parse_genre_from_soup(self, scraper):
        website = """<div class="subtext">12<span class="ghost">|</span><time datetime="PT135M">2h 15min</time>
        <span class="ghost">|</span><a href="/search/title?genres=action&explore=title_type,genres&ref_=tt_ov_inf">Action</a>, 
        <a href="/search/title?genres=adventure&explore=title_type,genres&ref_=tt_ov_inf">Adventure</a>,
        <a href="/search/title?genres=sci-fi&explore=title_type,genres&ref_=tt_ov_inf">Sci-Fi</a><span class="ghost">|</span>
        <a href="/title/tt3778644/releaseinfo?ref_=tt_ov_inf"
            title="See more release dates" >24 May 2018 (Germany)</a></div>"""
        soup = BeautifulSoup(website, 'html.parser')
        result = scraper._parse_genre_from_soup(soup)
        assert result == {'Adventure', 'Action', 'Sci-Fi'}

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

    def test__storyline_from_soup(self, scraper):
        website = """<h2>Storyline</h2>
        <div class="inline canwrap">
            <p>
                <span>    In the aftermath of <a href="/title/tt3498820?ref_=tt_stry_pl">The First Avenger: 
                Civil War</a> (2016), Scott Lang grapples with the consequences of his choices as both a superhero 
                and a father. As he struggles to rebalance his home life with his responsibilities as Ant-Man, 
                he's confronted by Hope van Dyne and Dr. Hank Pym with an urgent new mission. 
                Scott must once again put on the suit and learn to fight alongside The 
                Wasp as the team works together to uncover secrets from their past.</span>
                <em class="nobr">Written by
                <a href="/search/title?plot_author=Walt%20Disney%20Studios&view=simple&sort=alpha&ref_=tt_stry_pl"
                >Walt Disney Studios</a></em>            </p>
        </div>"""
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_storyline_from_soup(soup).startswith('In the aftermath')

    def test__parse_credits_from_soup(self, scraper):
        website = """
                <table class="cast_list">
  <tr><td colspan="4" class="castlist_label"></td></tr>
      <tr class="odd">
          <td class="primary_photo">
<a href="/name/nm0185819/?ref_=ttfc_fc_cl_i1"
><img height="44" width="32" alt="Daniel Craig" title="Daniel Craig" src="https://m.media-amazon.com/images/G/01/imdb/images/nopicture/32x44/name-2138558783._CB470041625_.png" class="loadlate hidden " loadlate="https://m.media-amazon.com/images/M/MV5BMjEzMjk4NDU4MF5BMl5BanBnXkFtZTcwMDMyNjQzMg@@._V1_UX32_CR0,0,32,44_AL_.jpg" /></a>          </td>
          <td>
<a href="/name/nm0185819/?ref_=ttfc_fc_cl_t1"
> Daniel Craig
</a>          </td>
          <td class="ellipsis">
              ...
          </td>
          <td class="character">
            <a href="/title/tt0830515/characters/nm0185819?ref_=ttfc_fc_cl_t1" >James Bond</a> 
                  
          </td>
      </tr>
      <tr class="even">
          <td class="primary_photo">
<a href="/name/nm1385871/?ref_=ttfc_fc_cl_i2"
><img height="44" width="32" alt="Olga Kurylenko" title="Olga Kurylenko" src="https://m.media-amazon.com/images/G/01/imdb/images/nopicture/32x44/name-2138558783._CB470041625_.png" class="loadlate hidden " loadlate="https://m.media-amazon.com/images/M/MV5BMTkyMzIwMjY1OF5BMl5BanBnXkFtZTcwNzA3MDkwOQ@@._V1_UX32_CR0,0,32,44_AL_.jpg" /></a>          </td>
          <td>
<a href="/name/nm1385871/?ref_=ttfc_fc_cl_t2"
> Olga Kurylenko
</a>          </td>
          <td class="ellipsis">
              ...
          </td>
          <td class="character">
            <a href="/title/tt0830515/characters/nm1385871?ref_=ttfc_fc_cl_t2" >Camille</a> 
                  
          </td>
      </tr>
        """
        soup = BeautifulSoup(website, 'html.parser')
        assert scraper._parse_credits_from_soup(soup) == {'actor': [185819, 1385871]}
