# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-27 18:30:23
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-28 19:38:31
# Database for txid - block mapping

import random
import time
import os
import sqlite3
import threading

PATH_INPUT_DAT = "../../raw/tx.dat"
PATH_OUTPUT_DB = '../../db/new_tx_block.sqlite'
PATH_LOG = "../../result/db_tx_block.log"
DAT_POINT_11AUG2017 = 5055916032
DAT_POINT_01JAN2017 = 3687744512
FREQ_DB_COMMIT = 1e6  # int
FREQ_DISPLAY = 1e5


def main():
    conn = sqlite3.connect(PATH_OUTPUT_DB)
    with open(PATH_LOG, "a") as log:
        write(log, "")
        write(log, "New db building.")
        if os.path.getsize(PATH_OUTPUT_DB) > 100:
            confirm_delete = input("Already exist. Delete & continue? (y/n): ")
            if confirm_delete != 'y':
                return
            else:
                try:
                    conn.execute("drop table TXTOBLOCK")
                except:
                    pass
                create_table(conn)
        else:
            create_table(conn)

        build_db(conn, log)
        conn.close()


def create_table(conn):
    conn.execute('''
                    CREATE TABLE TXTOBLOCK (
                    TXID            INT     NOT NULL UNIQUE,
                    BLOCK           INT     NOT NULL,
                    MINITX_STARTING INT    NOT NULL);
            ''')
    print("Table (re)created successfully.")


def build_db(conn, log):
    file_size = os.path.getsize(PATH_INPUT_DAT)  # Bytes
    dat_file = open(PATH_INPUT_DAT, 'rb')
    dat_file.seek(DAT_POINT_11AUG2017)  # this is where block48000 (AUG2017)
    dat_file.seek(DAT_POINT_01JAN2017)  # about 2017.1.1
    lines = dat_file.readline()
    lines = dat_file.readline()
    print("Start after: ", lines)
    write(log, "Start after" + lines.decode())

    cnt = 0
    t0 = time.time()
    start_p = dat_file.tell()

    tx_id = 0
    block_id = 0
    next_mini_tx_starting = 0
    for line in dat_file:
        cnt += 1
        tx_block_nin_nout = line.strip().decode().split('\t')
        # print(tx_block_nin_nout)

        tx_id = tx_block_nin_nout[0]
        block_id = tx_block_nin_nout[1]

        conn.execute(" INSERT INTO TXTOBLOCK (TXID, BLOCK, MINITX_STARTING) " +
                     " VALUES ({}, {}, {})".format(
                         tx_id,
                         block_id,
                         next_mini_tx_starting))
        next_mini_tx_starting += int(tx_block_nin_nout[3])

        if cnt % FREQ_DB_COMMIT == 0:
            conn.commit()
        if cnt % FREQ_DISPLAY == 0:
            disp_progress(t0, start_p, dat_file.tell(), file_size,
                          "No. " + str(cnt // FREQ_DISPLAY))
    dat_file.close()
    write(log, "TOTAL_MINI_TX_ID: [0, " + str(next_mini_tx_starting) + ")")
    conn.commit()


def disp_progress(start_time, start_p, now_p, end_p, comment):
    try:
        print("=" * 20, "\nREADY:\t", comment)
        pct = (now_p - start_p) / (end_p - start_p)
        used_time = time.time() - start_time
        print("COST TIME:\t", used_time // 60, ' min\t= ', used_time, " s")
        print("REMAINING:\t", used_time / (pct + 1e-10) * (1 - pct + 1e-10) //
              60, ' min\t= ', used_time / (pct + 1e-10) * (1 - pct + 1e-10), " s")
    except:
        pass


def write(f, notes):
    now_time_str = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    try:
        f.write(now_time_str + " " + str(notes))
        if len(notes) <= 1:
            f.write("\n")
        elif str(notes)[-1] != "\n":
            f.write("\n")
    except:
        print("Write error.")

main()
