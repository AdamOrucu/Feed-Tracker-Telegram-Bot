#!/usr/bin/python3
import os, sys
import pandas
import threading

from webtracker.config import TOKEN
from webtracker.tracker2 import Tracker
from webtracker.bot import Bot


def main():
   try:
      tr = Tracker(TOKEN, refresh_time=10)
      tr.start()

      bot = Bot(tr, TOKEN)
   except KeyboardInterrupt:
      try:
         sys.exit(0)
      except:
         os._exit(0)

if __name__ == '__main__':
   main()
