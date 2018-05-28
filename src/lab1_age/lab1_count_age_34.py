# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-28 12:37:27
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-28 19:42:48
import os
import db_block_time_stamp
import sqlite3
import time
import threading

def count_age_process(NUMBER):
    filename = "../../raw/txin{}.dat".format(NUMBER)
    filesize = os.path.getsize(filename)
    blocksize = 1024

    conn = sqlite3.connect('../../db/tx_2_block-34.sqlite')
    print("opened database successfully", filename)
    cur = conn.cursor()
    #cur.execute('''SELECT  txid, block FROM TXTOBLOCK;''')
    #for item in cur.fetchall():   print(type(item))
    block_time = db_block_time_stamp.init()
    print("========================")

    AGE_MAX = 6e7
    AGE_MIN = 0
    AGE_INTERVAL = int(6e7*1.0 / 1e4)
    cnt = [0 for i in range(int((AGE_MAX - AGE_MIN)*1.0 / AGE_INTERVAL) + 1)]


    buf = {
    'buffer_tx_from' : 0,
    'buffer_tx_to' : 0,
    'buffer_bl_from' : 0,
    'buffer_bl_to' : 0,
    }

    def tx2block22(tx, id):
        print(tx,id)
        if buf['buffer_tx_from'] == tx:
            print('use buffer')
            cur.execute(
                'SELECT txid, block FROM TXTOBLOCK WHERE txid = "{}";'.format(tx))
            for item in cur.fetchall():
                if item[1] != buf['buffer_bl_from']:
                    print("BUFFER ERROR!")
            return buf['buffer_bl_from']
        if tx == buf['buffer_tx_to']:
            return buf['buffer_bl_to']
        if id == 1:
            buf['buffer_tx_from'] = tx
        if id == 2:
            buf['buffer_tx_to'] = tx
        cur.execute(
            'SELECT txid, block FROM TXTOBLOCK WHERE txid = "{}";'.format(tx))
        for item in cur.fetchall():
            if id == 1:
                buf['buffer_bl_from'] = item[1]
            if id == 2:
                buf['buffer_bl_to'] = item[1]
            return item[1]

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
            age = AGE_MAX
        if age < 0:
            print("ERROR", tx_from, tx_to)
            return
        if age > AGE_MAX:
            age = AGE_MAX

        cnt[int((age - AGE_MIN) / AGE_INTERVAL)] += 1
        #print(tx_from, tx_to, block_from, block_to, age)


    with open(filename, 'rb') as dat_file, open("../../result/age_distri{}.txt".format(NUMBER), "w") as f:
        '''
        if filesize > blocksize:
            maxseekpoint = (filesize // blocksize)
            ddd = (maxseekpoint - int(11.099993 * 1024 * 1024)) * blocksize
            ddd = (maxseekpoint - int(0.1099993 * 1024 * 1024)) * blocksize
            dat_file.seek(ddd)
        elif filesize:
            # maxseekpoint = blocksize % filesize
            dat_file.seek(0, 0)
        lines = dat_file.readline()
        lines = dat_file.readline()
        '''

        n = 0
        t0 = time.time()

        for line in dat_file:
            n += 1
            count_age(line)
            now_point = dat_file.tell()


            if n % 5e3 == 0:
                f.write("["+str(n)+"]\tsamples:\t"+ str(cnt)+"\n")
                finished_pct = now_point*1.0 / filesize
                print("Ready %:\t", finished_pct*100)
                now_time = time.time() - t0
                need_time = now_time / (finished_pct + 0.0000000001) * \
                    (1 - finished_pct + 0.0000000001)
                print("Used time:\t",
                      now_time / 60, ' min\t= ', now_time)
                print("Esti. remaining:\t",
                      need_time / 60, ' min\t- ', need_time)
        f.write("["+str(n)+"]\tsamples:\t"+ str(cnt)+"\n")

a = input("THREAD")
count_age_process(int(a))