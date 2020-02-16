import pandas
import csv
import threading
import os
import feedparser
import requests
from bs4 import BeautifulSoup
import urllib
import re
import numpy as np
import time
import telegram

from config import TOKEN
FIELDS = ['url', 'page', 'lp_title', 'lp_url', 'extra_info']
FROM_H = 9
TO_H = 23
REFRESH_TIME = 300 # seconds


def check():
   obj = Obj()
   obj.func()

class Obj():
   def __init__(self):
      self.TO_NOTIFY = {}
      self.bot = telegram.Bot(token=TOKEN)
      pandas.set_option('display.max_colwidth', -1)

   def func(self):
      while(True):
         chat_ids = []
         for (dirpath, dirnames, filenames) in os.walk('data'):
            for f in filenames:
               chat_ids.append(f[:-4])
         print('Chats:', chat_ids)
         for chat in chat_ids:
            self.check_all_pages(chat)
         if FROM_H < time.localtime().tm_hour < TO_H:
            self.notify()
            count = 0
         print(self.TO_NOTIFY)
         time.sleep(REFRESH_TIME) #TODO: adjust time
   
   def check_all_pages(self, chat_id):
      file_loc = 'data/{}.csv'.format(chat_id)
      if os.stat(file_loc).st_size != 0 and len(list(csv.reader(open(file_loc, 'r')))) > 1:
         df = pandas.read_csv(file_loc)
         pages = df.url.values
         print('pages', pages)
         for url in pages:
            self.check_page(chat_id, url)
   
   def check_page(self, chat_id, url):
      file_loc = 'data/{}.csv'.format(chat_id)
      print('checking', url)
      blog = self.feedify(url)
      last_entry = feedparser.parse(blog).entries[0]
      df = pandas.read_csv(file_loc)
      row = df.loc[df['url'] == url]
      if row['lp_url'].to_string(index=False)[1:] != last_entry.link:
         df.loc[df['url'] == url] = [row['url'], row['page'], last_entry.title, last_entry.link, 'NULL']
         df = df.replace(np.NaN, 'NULL')
         df.to_csv(file_loc, index=False)
         if chat_id not in  self.TO_NOTIFY.keys():
            self.TO_NOTIFY[chat_id] = []
         self.TO_NOTIFY[chat_id].append((row['url'].to_string(index=False)[1:], row['page'].to_string(index=False)[1:], last_entry.title, last_entry.link, last_entry.published_parsed))
   
   def feedify(self, url): # TODO: add https:// to the beginning ot http
      if 'feed' not in url and 'rss' not in url:
         if url[-1] == '/':
            url = url + 'feed/'
         else:
            url += '/feed/'
      if 'http' not in url:
         url = 'https://' + url
      return url
   
   def notify(self):
      print('notifiying')
      remove = []
      print(self.TO_NOTIFY)
      for chat in self.TO_NOTIFY.keys():
         posts = []
         for index, post in enumerate(self.TO_NOTIFY[chat]):
            posts.append(f'_{time.strftime("%e %b %H:%M", post[-1])}_\n+ [{post[2]}]({post[3]}) - {post[1]}')
         remove.append(chat)
         if len(posts) > 1:
            posts.insert(0, f'*{len(posts)} New Posts*')
            self.bot.sendMessage(chat_id=chat, text='\n'.join(posts), parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
         else:
            self.bot.sendMessage(chat_id=chat, text='\n'.join(posts), parse_mode=telegram.ParseMode.MARKDOWN)
      for rem in remove:
         del self.TO_NOTIFY[rem]
      print(self.TO_NOTIFY)
      print('done')


class Tracker(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True
      self.TO_NOTIFY = {}

      if not os.path.exists('data'):
         os.makedirs('data')
      
   
   def start(self, chat_id):
      if not os.path.exists('data/{}.csv'.format(chat_id)):
         self.TO_NOTIFY[chat_id] = []
         with open('data/{}.csv'.format(chat_id), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

   def feedify(self, url): # TODO: add https:// to the beginning ot http
      if 'feed' not in url and 'rss' not in url:
         if url[-1] == '/':
            url = url + 'feed/'
         else:
            url += '/feed/'
      if 'http' not in url:
         url = 'https://' + url
      return url

   def list_pages(self, chat_id):
      file_loc = 'data/{}.csv'.format(chat_id)
      df = pandas.read_csv(file_loc)
      print(df)
      pages = []
      for index, row in df.iterrows():
         pages.append((row[0],row[1]))
      return pages

   def add(self, chat_id, url):
      print(f'adding {url} to {chat_id}.csv')
      file_loc = 'data/{}.csv'.format(chat_id)
      try:
         print('try')
         r = requests.head(url)
         print('req')
         print(r.status_code)
         if r.status_code == 200:
            print('200')
            if requests.head(self.feedify(url)).status_code == 200:
               print('feed true')
               html = urllib.request.urlopen(url).read()
               soup = BeautifulSoup(html, 'html.parser')
               name = soup.find('title').string
               name = " ".join(re.sub(r'([^\s\w]|_)+', '', name).split()[:6])
               df = pandas.read_csv(file_loc)
               if url not in df['url'].values:
                  with open(file_loc, 'a', newline='\n') as file:
                     csv_writer = csv.writer(file, delimiter=',')
                     csv_writer.writerow([url, name, 'NULL', 'NULL', 'NULL'])
                  print('done')
                  return True
               return 'Given url already exists'
            else:
               return 'No RSS'
      except Exception as e:
         return e

   def delete(self, chat_id, url):
      print(f'deleting {url} from {chat_id}.csv')
      file_loc = 'data/{}.csv'.format(chat_id)
      try:
         df = pandas.read_csv(file_loc, index_col=False)
         df = df[df.url != url].replace(np.NaN, 'NULL')
         df.to_csv(file_loc, index=False)
         return True
      except Exception as e:
         return e