# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-28 19:20:44
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-28 19:23:12

import sqlite3



print("opened database successfully")

"""
conn.execute('''CREATE TABLE TXTOBLOCK
       (
        TXID           INT    NOT NULL UNIQUE,
        BLOCK          INT     NOT NULL);''')
#conn.execute('''CREATE TABLE TXTOBLOCK
#       (ID             INT    PRIMARY KEY     NOT NULL,
#        TXID           INT    NOT NULL UNIQUE,
#        BLOCK          INT     NOT NULL);''')

print("Table created successfully")

conn.execute("REPLACE INTO TXTOBLOCK (TXID, BLOCK) \
      VALUES (2213, 32)")
conn.execute("REPLACE INTO TXTOBLOCK (TXID, BLOCK) \
      VALUES (2213, 322)")
conn.execute("REPLACE INTO TXTOBLOCK (TXID, BLOCK) \
      VALUES (22, 32242)")
conn.execute("REPLACE INTO TXTOBLOCK (TXID, BLOCK) \
      VALUES (20, 32242)")

conn.commit()
conn.execute("REPLACE INTO TXTOBLOCK (TXID, BLOCK) \
      VALUES (324213, 32)")
conn.commit()
conn.close()

"""
conn = sqlite3.connect('playyy.sqlite')

print("opened database successfully")
cur = conn.cursor()

cur.execute('''SELECT txid, block FROM tb ;''')

for item in cur.fetchall():
    print(item)
    print(type(item))

conn.commit()
conn.close()