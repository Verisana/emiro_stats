import requests
import pickle
import time

from bs4 import BeautifulSoup
from datetime import datetime


class EMiroDataCollector:
    def __init__(self, posts_filename='emiro_posts',
                 activity_filename='emiro_activity'):
        self.posts_url = "https://lena-miro.ru/?skip="
        self.stop_date = datetime.now().replace(month=1)
        self.posts_filename = posts_filename
        self.activity_filename = activity_filename

    def update_posts_file(self):
        posts = self._get_posts()
        with open(self.posts_filename, 'wb') as file:
            pickle.dump(posts, file)

    def update_activity_file(self):
        activity = self._get_activity()
        with open(self.activity_filename, 'wb') as file:
            pickle.dump(activity, file)

    def get_posts_file(self):
        with open(self.posts_filename, 'rb') as file:
            return pickle.load(file)

    def get_activity_file(self):
        with open(self.activity_filename, 'rb') as file:
            return pickle.load(file)

    def _get_soup_html(self, url):
        response = requests.get(url)
        time.sleep(1)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            raise Exception(f'Error fetching data. URL = {url}')

    @staticmethod
    def _parse_article_soup(soup):
        articles = soup.body.find('div', 'j-l-alpha-content-inner') \
            .findAll('article')
        parsed_posts = []
        for article in articles:
            datetime_str = article.time['datetime'] + ' ' \
                           + article.time.find('span', 'j-e-date-time').text
            new_parsed = {
                'title': article.h3.text,
                'date_added': datetime.strptime(datetime_str,
                                                "%Y-%m-%d %I:%M %p"),
                'link': article.h3.a['href'],
            }
            parsed_posts.append(new_parsed)
        return parsed_posts

    def _parse_comments_soup(self, post_soup):
        all_activity = []
        comment_section = post_soup.body.find('div', 'j-l-comments-inner')
        try:
            forward = comment_section.find('div',
                                           'j-comments-pages-next').a['href']
        except AttributeError or TypeError:
            forward = None
        all_comments = comment_section.findAll('article')

        for i, comment in enumerate(all_comments):
            try:
                user_name = comment.find('span', 'ljuser')['data-ljuser']
            except TypeError:
                user_name = ''
            if user_name == 'lena-miro.ru':
                if 'j-c-partial' in comment['class']:
                    soup_response = self._get_soup_html(
                        comment.a['href'])
                    full_comment = soup_response.select(
                        f'article[id={comment["id"]}]')[0]
                else:
                    full_comment = comment

                datetime_str = full_comment.time[
                                   'datetime'] + ' ' + full_comment.time.find(
                    'span',
                    'j-c-date-time').text
                all_activity.append({
                    'date_added': datetime.strptime(
                        datetime_str,
                        "%Y-%m-%d %I:%M %p"),
                    'type': 'comment'
                })
                print(f'    Processeded {i} of {len(all_comments)} comments')
        return all_activity

    def _get_activity(self):
        posts = self.get_posts_file()
        all_activity = [{'date_added': post['date_added'], 'type': 'post'}
                        for post in posts]
        for i, post in enumerate(posts):
            post_soup = self._get_soup_html(post['link'])
            all_activity.extend(self._parse_comments_soup(post_soup))
            print(f'Processed {i} of {len(posts)} posts activity')
        return all_activity

    def _get_posts(self):
        skip = 0
        last_date = datetime.now()
        all_posts = []
        while last_date > self.stop_date:
            soup_response = self._get_soup_html(self.posts_url + str(skip))
            all_posts.extend(self._parse_article_soup(soup_response))
            skip += 10
            last_date = all_posts[-1]['date_added']
            print(f'Processed {len(all_posts)} posts article')
        return all_posts


dc = EMiroDataCollector()
dc.update_posts_file()
print('all_done')