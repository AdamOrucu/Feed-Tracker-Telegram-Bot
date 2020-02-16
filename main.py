import os, sys
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram import ParseMode
import pandas
import threading

from config import TOKEN
from tracker import Tracker, check

def start(update, context):
   print('Start')
   print(update.message.chat_id)
   tracker.start(update.message.chat_id)
   update.message.reply_text('Welcome {} I\'m RSS Tracker Bot let me help you with changes on websites'.format(update.message.from_user.first_name))

def list_urls(update, context):
   print('List')
   try:
      df = pandas.read_csv('data/{}.csv'.format(update.message.chat_id))
      urls = []
      for index, row in df.iterrows():
         urls.append(f'{index+1}. [{row[1]}]({row[0]})')
      print('urls:', urls)
      update.message.reply_text(text='\n'.join(urls), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
   except Exception as e:
      update.message.reply_text(f'Error: {e}')

def add(update, context):
   try:
      url = update.message.text[5:]
      print('Add:', url)
      res = tracker.add(update.message.chat_id, url)
      update.message.reply_text(res)
   except Exception as e:
      update.message.reply_text(f'Error: {e}')

def delete(update, context):
   try:
      url = update.message.text[8:]
      print('Delete:', url)
      res = str(tracker.delete(update.message.chat_id, url))
      update.message.reply_text(res)
   except Exception as e:
      update.message.reply_text(f'Error: {e}')

def main():
   updater = Updater(TOKEN, use_context=True)
   dp = updater.dispatcher
   dp.add_handler(CommandHandler('start', start))
   dp.add_handler(CommandHandler('list', list_urls))
   dp.add_handler(CommandHandler('add', add))
   dp.add_handler(CommandHandler('delete', delete))

   updater.start_polling()
   updater.idle()

if __name__ == '__main__':
   try:
      print('Beginning')
      tracker = Tracker()
      thread = threading.Thread(target=check)
      thread.daemon = True
      print('thread')
      thread.start()
      print('main')
      main()

   except KeyboardInterrupt:
      try:
         sys.exit(0)
      except:
         os._exit(0)