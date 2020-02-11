import requests
import pickle
import time

from bs4 import BeautifulSoup
from datetime import datetime


class EMiroDataCollector:
    def __init__(self, posts_filename='emiro_posts',
                 activity_filename='emiro_activity'):
        self.URL = "https://lena-miro.ru/?skip="
        self.skip = 0
        self.stop_date = datetime.now().replace(month=1)
        self.posts_filename = posts_filename
        self.activity_filename = activity_filename

    def update_posts_file(self):
        posts = self._get_posts()
        with open(self.activity_filename, 'w') as file:
            pickle.dump(posts, file)

    def get_posts_file(self, filename):
        with open(self.activity_filename, 'r') as file:
            return pickle.load(file)

    def _get_soup_html(self, skip):
        response = requests.get(self.URL+str(skip))
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            raise Exception(f'Error fetching data. Skip = {skip}')

    def _parse_soup(self, soup):
        articles = soup.body.find('div', 'j-l-alpha-content-inner')\
            .findAll('article')
        for article in articles:
            new_parsed = {}
            new_parsed['title'] = article.h3.text

            year, month, day = article.time['datetime'].split('-')

            new_parsed['date_publ'] = None
            new_parsed['link'] = article.h3.a['href']


    def _get_posts(self):
        skip = 0
        last_date = datetime.now()
        while last_date > self.stop_date:
            soup_response = self._get_soup_html(skip)
            parsed_posts = self._parse_soup(soup_response)
            skip += 10
            last_date = parsed_posts[-1]['publ_date']

dc = EMiroDataCollector()
dc.update_posts_file()