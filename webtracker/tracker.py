import threading
import pandas as pd
import numpy as np
import os, csv, re
import requests, urllib
from bs4 import BeautifulSoup
import time
import telegram
import feedparser

from webtracker.components import *

class Tracker(threading.Thread):
   """The main part of the bot that runs in the background waits for commands from the user."""
   FIELDS = ['url', 'page', 'newest_post_title', 'newest_post_url', 'extra_info', 'is_rss']

   def __init__(self, token, refresh_time=300, window=(9,22)):
      """Initializes the tracker

      Keyword Arguments:
          token {str} -- telgram token
          refresh_time {int} -- the frequency to check websites (default: {300})
          window {tuple} -- Window in which the tracking should be conducted (default: {(8,22)})
      """
      threading.Thread.__init__(self)
      self.daemon = True
      self.WINDOW = window
      self.REF_TIME = refresh_time
      self.TO_NOTIFY = {}
      
      self.bot = telegram.Bot(token=token)
      pd.set_option('display.max_colwidth', -1)

      if not os.path.exists('data'):
         os.makedirs('data')
      
   def run(self):
      while True:
         chat_ids = []
         for (dirpath, dirnames, filenames) in os.walk('data'):
            for f in filenames:
               chat_ids.append(f[:-4])
         print('Chats:', chat_ids)
         for chat in chat_ids:
            self.check_all_pages(chat)
         if self.WINDOW[0] < time.localtime().tm_hour < self.WINDOW[1]:
            self.notify()
            count = 0
         print(self.TO_NOTIFY)
         time.sleep(self.REF_TIME)

   def start_new_chat(self, chat_id):
      """Creates a new file in which information of an individual user are stored.

      Arguments:
          chat_id {int} -- chat_id provided by telegram
      """
      if not os.path.exists('data/{}.csv'.format(chat_id)):
         self.TO_NOTIFY[chat_id] = []
         with open('data/{}.csv'.format(chat_id), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.FIELDS)

   def list_pages(self, chat_id):
      """Returns a list of subscribed websites for the given chat id

      Arguments:
          chat_id {int} -- chat id provided by telegram

      Returns:
          List -- List of page url and name
      """
      file_loc = 'data/{}.csv'.format(chat_id)
      df = pd.read_csv(file_loc)
      print(df)
      pages = []
      for index, row in df.iterrows():
         pages.append((strip(row[0]),row[1]))
      return pages

   def add(self, chat_id, url):
      """Adds a new webpage to the list of subsciptions.

      Arguments:
          chat_id {int} -- Chat id provided by telegram
          url {str} -- url of the page

      Returns:
          String -- Text that informs the user the result of the operation
      """
      print(f'adding {url} to {chat_id}.csv')
      file_loc = 'data/{}.csv'.format(chat_id)
      try:
         print('try')
         r = requests.get(url)
         print('req')
         print(r.status_code)
         if r.status_code == 200:
            print('200')
            ext = 'f' if requests.get(feedify(url)).status_code == 200 else \
               'r' if requests.get(rssify(url)).status_code == 200 else False
            if ext is not False:
               print('feed true')
               html = urllib.request.urlopen(url).read()
               soup = BeautifulSoup(html, 'html.parser')
               name = soup.find('title').string
               name = " ".join(re.sub(r'([^\s\w]|_)+', '', name).split()[:6])
               df = pd.read_csv(file_loc)
               if feedify(url) not in df['url'].values and rssify(url) not in df['url'].values:
                  with open(file_loc, 'a', newline='\n') as file:
                     csv_writer = csv.writer(file, delimiter=',')
                     csv_writer.writerow([feedify(url) if ext == 'f' else rssify(url), name, 'NULL', 'NULL', 'NULL'])
                  print('done')
                  return True
               return 'Given url already exists'
            else:
               return 'No RSS'
         else:
            return 'Could not find the web site'
      except Exception as e:
         return 'e: ', e

   def remove(self, chat_id, url):
      """Removes a page from subscriptions

      Arguments:
          chat_id {int} -- Chat id provided by telegram
          url {str} -- url of the site to be removed

      Returns:
          Exception  -- Returns an exception i there is one else returns True
      """
      print(f'deleting {url} from {chat_id}.csv')
      file_loc = 'data/{}.csv'.format(chat_id)
      try:
         df = pd.read_csv(file_loc, index_col=False)
         df = df[df.url != url].replace(np.NaN, 'NULL')
         df.to_csv(file_loc, index=False)
         return True
      except Exception as e:
         return e
      
   def check_all_pages(self, chat_id):
      file_loc = 'data/{}.csv'.format(chat_id)
      if os.stat(file_loc).st_size != 0 and len(list(csv.reader(open(file_loc, 'r')))) > 1:
         df = pd.read_csv(file_loc)
         pages = df.url.values
         print('pages', pages)
         for url in pages:
            self.check_page(chat_id, url)
   
   def check_page(self, chat_id, url):
      file_loc = 'data/{}.csv'.format(chat_id)
      print('checking', url)
      blog = url
      last_entry = feedparser.parse(blog).entries[0]
      df = pd.read_csv(file_loc)
      row = df.loc[df['url'] == url]
      if row['lp_url'].to_string(index=False)[1:] != last_entry.link:
         df.loc[df['url'] == url] = [row['url'], row['page'], last_entry.title, last_entry.link, 'NULL']
         df = df.replace(np.NaN, 'NULL')
         df.to_csv(file_loc, index=False)
         if chat_id not in  self.TO_NOTIFY.keys():
            self.TO_NOTIFY[chat_id] = []
         self.TO_NOTIFY[chat_id].append((row['url'].to_string(index=False)[1:], row['page'].to_string(index=False)[1:], last_entry.title, last_entry.link, last_entry.published_parsed))

   def notify(self):
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
      print('done')
