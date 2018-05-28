import threading
import time
import random
import sqlite3

exitFlag = 0
conn = sqlite3.connect('./play.sqlite')
print("opened database successfully")

#conn.execute("drop table TXTOBLOCK")
#conn.execute('''CREATE TABLE PLAY(        A           INT     NOT NULL UNIQUE,        B          INT     NOT NULL);''')
conn.commit()
conn.close()


class myThread (threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print_time(self.name, self.counter, 5)


def print_time(threadName, delay, counter):
    conn = sqlite3.connect('./play.sqlite')
    conn.execute('''INSERT INTO play (A, B) VALUES ({}, {});'''.format(
        random.uniform(1, 10),
        random.uniform(1, 10)
    ))
    conn.commit()
    conn.close()

# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启新线程
thread1.start()
thread2.start()
thread1.join()
thread2.join()

conn = sqlite3.connect('./play.sqlite')
cur = conn.cursor()
a = cur.execute('''SELECT * FROM play WHERE B<=2 ORDER BY B asc LIMIT 1;''')
for item in a.fetchall():
    print(dir(a))
    print(item)

print("退出主线程")
