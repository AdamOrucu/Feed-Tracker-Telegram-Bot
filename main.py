import os, sys
import pandas
import threading

from config import TOKEN
from Tracker import Tracker
from Bot import Bot


def main():
   try:
      tr = Tracker(TOKEN, refresh_time=60)
      tr.start()

      bot = Bot(tr, TOKEN)
   except KeyboardInterrupt:
      try:
         sys.exit(0)
      except:
         os._exit(0)

if __name__ == '__main__':
   main()