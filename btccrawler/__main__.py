import ccxt
from datetime import datetime
from threading import Timer,Thread,Event
from .db import DB

EXCHANGES = ['bitflyer', 'liquid', 'zaif', 'coincheck']
BOOK_DEPTH = 10

class LoopThread(Thread):
  def __init__(self, event):
    Thread.__init__(self)
    self.stopped = event
    # self.daemon = True
    self.exchanges = {}
    for name in EXCHANGES:
      self.exchanges[name] = getattr(ccxt, name)()
    self.db = None

  def run(self):
    while not self.stopped.wait(3):
      if self.db == None:
        self.db = DB(BOOK_DEPTH)
      for name in EXCHANGES:
        book = self.exchanges[name].fetch_order_book('BTC/JPY')
        asks = book['asks'][0:BOOK_DEPTH]
        bids = book['bids'][0:BOOK_DEPTH]
        unix = datetime.now().timestamp()
        self.db.save(name, unix, asks, bids)

if __name__ == "__main__":
  stopFlag = Event()
  thread = LoopThread(stopFlag)
  thread.start()
  while True:
    n = input()
    if n == "e":
      print("Terminate")
      stopFlag.set()
      break