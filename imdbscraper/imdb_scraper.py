# -*- coding: utf-8 -*-
__author__ = "Stefan Seltmann"
__interpreter__ = "3.6.3"
import logging
import re
from logging import NullHandler
from typing import Optional, Set
from urllib import request

from bs4 import BeautifulSoup


class IMDBScraper:
    url_base: str = 'http://www.imdb.com/title/tt{}'
    dir_cache: str

    def __init__(self, dir_cache: str):
        """:param dir_cache: local directory where the scraped objects will be stored."""
        self.dir_cache = dir_cache
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(NullHandler())

    def process_imdb_movie_id(self, imdb_movie_id: int, use_cache: bool = True) -> dict:
        """Get website for a given imdb_movie_id and return parsed asset

        :param imdb_movie_id:
        :param use_cache:
        :return: parsed asset data as dictionary
        """
        content = self.get_webcontent_4_imdb_movie(imdb_movie_id, use_cache=use_cache)
        asset = self.parse_webcontent_4_imdb_movie(imdb_movie_id, content)
        return asset

    def get_webcontent_4_imdb_movie(self, imdb_movie_id: int, use_cache: bool = True) -> str:
        """Provide the website for a given imdb_movie_id as a string to be parsed

        :param imdb_movie_id: unique ID used by imdb
        :param use_cache: if true, a already stored string will be used and no request to the website will be made
        :return: raw string of the website
        """
        website_string: str = None
        if use_cache:
            try:
                with open(self.dir_cache + '/movies/{}.imdb_movie'.format(imdb_movie_id), 'rb') as file_handle:
                    website_string = file_handle.read()
                    self.logger.info("Loading cached website for {}.".format(imdb_movie_id))
            except FileNotFoundError:
                self.logger.info("{} not found in cache.".format(imdb_movie_id))
        if not website_string or not use_cache:
            self.logger.info("Retrieving website for {}.".format(imdb_movie_id))
            url_movie: str = self.url_base.format(str(imdb_movie_id).zfill(7))
            website_string = request.urlopen(url_movie).read()
            for sub_site in ('parentalguide', 'fullcredits', 'awards', 'business', 'companycredits', 'technical',
                             'keywords', 'plotsummary'):
                website_sub = request.urlopen(f'{url_movie}/{sub_site}')
                website_string += website_sub.read()
            with open(self.dir_cache + '/movies/{}.imdb_movie'.format(imdb_movie_id), 'wb') as f:
                f.write(website_string)
        return website_string

    def parse_webcontent_4_imdb_movie(self, imdb_movie_id: int, website: str) -> dict:
        self.logger.info("Parsing webcontent for {}".format(imdb_movie_id))
        asset = {'imdb_movie_id': imdb_movie_id}
        soup = BeautifulSoup(website, 'html.parser')
        title_orig = soup.find('meta', {'property': 'og:title'})['content']
        asset['title_orig'] = ' '.join(title_orig.split(' ')[:-1])
        asset['year'] = self._parse_year_from_title(title_orig)
        asset['awards'] = self._parse_awards_from_soup(soup.find_all('table', {'class': 'awards'}))
        asset['genres'] = self._parse_genre_from_soup(soup)
        asset['budget'] = self._parse_budget_from_soup(soup)
        asset['duration'] = self._parse_runtime_from_soup(soup.find('time'))
        asset['fsk'] = self._parse_fsk_from_soup(soup)

        ratings = self._parse_rating_from_soup(soup)
        asset.update(ratings)
        print(asset)

        asset['storyline']: str = self._parse_story_line_from_soup(soup)

        asset['persons'] = self._parse_credits_from_soup(soup.find('div', {'id': 'fullcredits_content'}))
        directors_raw = soup.find('h4', text=re.compile('Directed by')).find_next('tbody').find_all('a')
        for director_raw in directors_raw:
            asset['persons'].setdefault('director', []).append(re.findall('name/nm.*/', director_raw['href'])[0][7:-1])
        return asset

    @staticmethod
    def _parse_rating_from_soup(soup: BeautifulSoup):
        search_tmp = soup.find('div', attrs={'class': 'imdbRating'})
        search_spans = search_tmp.find_all('span')
        rating_imdb = search_spans[0].contents[0]
        rating_imdb_count = search_spans[3].contents[0]
        return {'rating_imdb': float(rating_imdb.replace(',', '.')),
                'rating_imdb_count': int(rating_imdb_count.replace(',', '').replace('.', ''))}

    @staticmethod
    def _parse_genre_from_soup(soup: BeautifulSoup) -> Set[str]:
        search = soup.find('div', {'itemprop': 'genre'})
        if search:
            # first old-style parsing:
            genres_raw = search.find_all('a')
            genres = {genre.text.strip() for genre in genres_raw}
        else:
            genres_raw = soup.find_all('a', attrs={'href': re.compile("^/genre/")})
            genres = {element.contents[0].strip() for element in genres_raw}
        return genres

    @staticmethod
    def _parse_credits_from_soup(soup: BeautifulSoup) -> dict:
        res = soup.find_all("td", attrs={'itemprop': 'actor'})
        actor_ids = [int(html.find('a', attrs={'itemprop': 'url'}).attrs['href'].split("/")[2][2:]) for html in res]
        persons = {'actor': actor_ids}
        return persons

    def _parse_storyline_from_soup(self, soup: BeautifulSoup) -> str:
        try:
            storyline_raw: str = soup.find('div', {'class': 'inline canwrap'}).p.span.get_text()
        except AttributeError:
            storyline_raw = ""  # fixme
        if not storyline_raw:
            self.logger.error("No storyline found!")
        return storyline_raw.replace("\n", "").replace('"', "").strip()

    def _parse_synopsis_from_soup(self, soup: BeautifulSoup) -> str:
        try:
            synopsis: str = soup.find('ul', {'id': 'plot-synopsis-content'}).get_text()
        except AttributeError:
            synopsis = ""  # fixme
        if not synopsis:
            self.logger.error("No storyline found!")
        return synopsis.replace("\n", "").replace('"', "").strip()

    @staticmethod
    def _parse_budget_from_soup(soup: BeautifulSoup) -> Optional[int]:
        budget_raw = soup(text=re.compile('Budget'))
        if budget_raw:
            try:
                budget = budget_raw[0].next.replace('$', '').replace(',', '').strip()
            except TypeError:
                budget = None
        else:
            budget = None
        return budget

    @staticmethod
    def _parse_year_from_title(title_string: str) -> int:
        if 'TV Series' in title_string or "Mini-Series" in title_string:
            year_search = re.search(r'\(.+\)$', title_string).group(0)
            year = int(year_search.split(' ')[2][0:4])
        else:
            year = int(title_string.split(' ')[-1].replace('(', '').replace(')', ''))
        return year

    @staticmethod
    def _parse_fsk_from_soup(soup: BeautifulSoup) -> int:
        """fsk is the German required age to access an asset"""
        soup_search_result = \
            soup.find_all('a', {'href': re.compile(r'/search/title\?certificates=(de|imdb_wg|DE|Germany):[0-9]')})
        if not soup_search_result:
            fsk = 99
        else:
            fsk = int(soup_search_result[0].text.split(':')[1])
        return fsk

    @staticmethod
    def _parse_runtime_from_soup(soup: BeautifulSoup) -> int:
        if soup:
            try:
                runtime_str = soup.text.strip()
                if runtime_str.find('h') > 0:
                    runtime_hours, runtime_min = runtime_str.split(' ')
                    runtime = int(runtime_hours.strip('h')) * 60 + int(runtime_min.strip('min'))
                else:
                    runtime = int(soup.text.strip().replace(' min', ''))
            except ValueError:
                runtime = None
        else:
            runtime = None
        return runtime

    @staticmethod
    def _parse_awards_from_soup(soup: BeautifulSoup) -> dict:
        awards = {}
        for award_table in soup:
            cells = award_table.find_all('td')
            award_outcome_current = None
            award_category_current = None
            for cell in cells:
                cell_htmlclass = cell.get('class')[0]
                if cell_htmlclass == 'title_award_outcome':
                    award_outcome_current = cell.find('b').text
                    award_category_current = cell.find('span').text
                elif cell_htmlclass == 'award_description':
                    award_description = cell.text.split('\n')[1].strip()
                    awards.setdefault(award_category_current, []).append((award_description, award_outcome_current))
                else:
                    raise Exception
        return awards
