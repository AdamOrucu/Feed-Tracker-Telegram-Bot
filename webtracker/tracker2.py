import csv
import os
import threading
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import telegram

from webtracker.components import *

class Tracker(threading.Thread):
    FIELDS = ['url', 'page', 'newest_post_title', 'newest_post_url', 'extra_info', 'is_rss']

    def __init__(self, token, refresh_time, check_window=(9,22)):
        threading.Thread.__init__(self)
        self.deamon = True
        self.WINDOW = check_window
        self.REF_TIME = refresh_time
        self.TO_NOTIFY = {}

        self.bot = telegram.Bot(token=token)

        if not os.path.exists('data'):
           os.makedirs('data')

    def run(self):
        while True:
            chat_ids = []
            for f in os.listdir('data'):
                chat_ids.append(f[:-4])
            print('Chats:', chat_ids)
            for chat in chat_ids:
                self.check_all_pages(chat)
            if self.WINDOW[0] < time.localtime().tm_hour < self.WINDOW[1]:
                self.notify()
            time.sleep(self.REF_TIME)

    def start_new_chat(self, chat_id):
        if not os.path.exists(f'data/{chat_id}.csv'):
            self.TO_NOTIFY[chat_id] = []
            with open(f'data/{chat_id}.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.FIELDS)

    def list_pages(self, chat_id):
        df = pd.read_csv(f'data/{chat_id}.csv')
        return list(zip(df['url'].to_list(), df['page'].to_list()))


    def add(self, chat_id, url_to_add):
        print(f'adding {url} to {chat_id}.csv')
        file_loc = f'data/{chat_id}.csv'
        urls = get_url_combo(url_to_add)
        for url in urls:
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            print(200)
            soup = BeautifulSoup(resp.content, 'html.parser')
            name = soup.find('title').string
            name = " ".join(re.sub(r'([^\s\w]|_)+', '', name).split()[:6])
            df = pd.read_csv(file_loc)
            if url not in df['url'].values:
                df.append({'url': url, 'page': name, 'is_rss': True}, ignore_index=True)
                return 'Success'
            else:
                return 'Given url already exists'

        print('No page found')
        return self.add_non_rss(url_to_add)

    def remove(self, chat_id, url):
        file_loc = f'data/{chat_id}.csv'
        try:
            df = pd.read_csv(file_loc, index_col=False)
            df = df[df.url != url]
            df.ro_csv(file_loc, index=False)
            return 'Success'
        except Exception as e:
            print(e)
            return 'Error'

    def check_all_pages(self, chat_id):
        file_loc = f'data/{chat_id}.csv'
        df = pd.read_csv(file_loc)
        pages = df.url.values
        is_rss = df.is_rss.values
        for i, isrs in enumerate(is_rss):
            if isrs:
                self.check_page(chat_id, url)
            else:
                raise NotImplementedError

    def check_page(self, chat_id, url):
        file_loc = f'data/{chat_id}.csv'
        last_entry = feedparser.parse(url).entries[0]
        df = pd.read_csv(file_loc)
        row = df.loc[df['url'] == url]
        print(row['newest_post_url'])
        if row['newest_post_url'] != last_entry.link:
            print('new post')
            df.loc[df['url'] == url] = [row['url'], row['page'], last_entry.title, last_entry.link, 'NULL']
            df.to_csv(file_loc, index=False)
            if chat_id not in self.TO_NOTIFY.key():
                self.TO_NOTIFY[chat_id] = []
            self.TO_NOTIFY[chat_id].append(row['url'], row['page'], last_entry.title,last_entry.published_parsed)

    def notify(self):
        remove = []
        print(self.TO_NOTIFY)
        for chat in self.TO_NOTIFY.keys():
            posts = []
            for ind, post in enumerate(self.TO_NOTIFY[chat]):
                posts.append(f'_{time.strftime("%e %b %H:%M", post[-1])}_\n+ [{post[2]}]({post[3]}) - {post[1]}')
            remove.append(chat)
            if len(posts) > 1:
                posts.insert(0, f'*{len(posts)} New Posts*')
                self.bot.sendMessage(chat_id=chat, text='\n'.join(posts), parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
            else:
                self.bot.sendMessage(chat_id=chat, text='\n'.join(posts), parse_mode=telegram.ParseMode.MARKDOWN)
        for rem in remove:
            del self.TO_NOTIFY[rem]
        print('done')
