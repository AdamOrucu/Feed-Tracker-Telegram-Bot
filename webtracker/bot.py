import pandas as pd
import csv, os
import threading
import feedparser
import requests
from bs4 import BeautifulSoup
import urllib
import re
import numpy as np
import time
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram import ParseMode

from webtracker.config import TOKEN


class Bot:
   def __init__(self, tracker, token):
      self.TOKEN = token
      self.tracker = tracker

      updater = Updater(self.TOKEN, use_context=True)
      dp = updater.dispatcher
      dp.add_handler(CommandHandler('start', self.start_conv))
      dp.add_handler(CommandHandler('list', self.list_urls))
      dp.add_handler(CommandHandler('add', self.add))
      dp.add_handler(CommandHandler('delete', self.delete))

      updater.start_polling()
      updater.idle()

   def start_conv(self, update, context):
      print('Start')
      print(update.message.chat_id)
      import csv
      self.tracker.start_new_chat(update.message.chat_id)
      update.message.reply_text('Welcome {} I\'m RSS Tracker Bot let me help you with changes on websites'.format(update.message.from_user.first_name))

   def list_urls(self, update, context):
      print('List')
      try:
         df = pd.read_csv('data/{}.csv'.format(update.message.chat_id))
         urls = []
         for index, row in df.iterrows():
            urls.append(f'{index+1}. [{row[1]}]({row[0]})')
         print('urls:', urls)
         update.message.reply_text(text='\n'.join(urls), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
      except Exception as e:
         update.message.reply_text(f'Error: {e}')

   def add(self, update, context):
      try:
         print(update.message.text)
         url = update.message.text[5:]
         print('Add:', url)
         res = self.tracker.add(update.message.chat_id, url)
         update.message.reply_text(res)
      except Exception as e:
         update.message.reply_text(f'Error: {e}')

   def delete(self, update, context):
      try:
         url = update.message.text[8:]
         print('Delete:', url)
         res = str(self.tracker.delete(update.message.chat_id, url))
         update.message.reply_text(res)
      except Exception as e:
         update.message.reply_text(f'Error: {e}')
