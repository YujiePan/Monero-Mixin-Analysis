# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-30 23:16:52
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-31 00:08:22

import os
import sqlite3
import time
import sys
import random
sys.path.append("..")
from db_builder import db_block_time_stamp
import threading


def count_age_process(NUMBER):
    filename = "../../raw/txin{}.dat".format(NUMBER)
    filesize = os.path.getsize(filename)
    blocksize = 1024

    conn = sqlite3.connect('../../db/tx_2_block.sqlite')
    print("opened database successfully", filename)
    cur = conn.cursor()
    #cur.execute('''SELECT  txid, block FROM TXTOBLOCK;''')
    #for item in cur.fetchall():   print(type(item))
    block_time = db_block_time_stamp.init()
    print("========================")

    def tx2block(tx, id):
        cur.execute(
            'SELECT txid, block FROM TXTOBLOCK WHERE txid = "{}";'.format(tx))
        for item in cur.fetchall():
            return item[1]

    def count_age(txid_txno_prevtxid_prevtxno_id_sum):
        # print(txid_txno_prevtxid_prevtxno_id_sum,end="-------")
        tx = txid_txno_prevtxid_prevtxno_id_sum.strip().decode().split('\t')
        if len(tx) != 6:
            print("ERROR!")

        tx_from = int(tx[2])
        tx_to = int(tx[0])

        block_from = tx2block(tx_from, 1)
        block_to = tx2block(tx_to, 2)

        if block_from and block_to:
            age = block_time[block_to] - block_time[block_from]
        else:
            return -100
        if age < 0:
            print("ERROR", tx_from, tx_to)
            return -100
        return age

        #cnt[int((age - AGE_MIN) / AGE_INTERVAL)] += 1
        #print(tx_from, tx_to, block_from, block_to, age)

    with open(filename, 'rb') as dat_file, open("../../result/AGE_ALL{}.txt".format(NUMBER), "w") as f:
        n = 0
        t0 = time.time()

        for line in dat_file:
            n += 1
            age0 = count_age(line)
            if age0 >= 0:
                age0 = age0 + random.randint(1, 600)
            f.write(str(age0) + ",")
            now_point = dat_file.tell()

            if n > 2.5e6:
                break

            if n % 5e3 == 0:
                print("[" + str(n) + "]\tsamples:\t" + "\n")
                finished_pct = now_point * 1.0 / filesize
                print("Ready %:\t", finished_pct * 100)
                now_time = time.time() - t0
                need_time = now_time / (finished_pct + 0.0000000001) * \
                    (1 - finished_pct + 0.0000000001)
                print("Used time:\t",
                      now_time / 60, ' min\t= ', now_time)
                print("Esti. remaining:\t",
                      need_time / 60, ' min\t- ', need_time)


a = input("THREAD")
count_age_process(int(a))
