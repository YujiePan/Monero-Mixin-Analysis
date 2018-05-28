# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-28 01:27:51
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-28 19:40:24
# Database for eachtx's in_Id, out_id

import time
import random
import os
import sqlite3
import threading

PATH_INPUT_DAT = "../../raw/txin{}.dat"
PATH_OUTPUT_DB = '../../db/new_tx_in_out{}.sqlite'
PATH_LOG = "../../result/db_tx_in_out.log"
FREQ_DB_COMMIT = 2e5  # int
FREQ_DISPLAY = 2e4


def main():
    task = input("1: split_dat\n2: build db\nCHOOSE: ")
    with open(PATH_LOG, "a") as log:
        write(log, "")
        write(log, "New db_tx_in_out execute")
        if task == "2":
            create_db()
            build_db()
        if task == "1":
            build_db(True)


def create_db():
    for num in range(4):
        conn = sqlite3.connect(PATH_OUTPUT_DB.format(num + 1))
        try:
            conn.execute("drop table tx_in_out")
        except:
            pass
        conn.execute('''CREATE TABLE tx_in_out
               (
                txto           INT    NOT NULL,
                txfrom         INT    NOT NULL,
                txfrom_no      INT    NOT NULL
                );
                ''')
        print("Table {} created successfully".format(num + 1))
        conn.commit()
        conn.close()


def split_dat(num, start, end):
    with open(PATH_INPUT_DAT.format(""), "rb") as fin,\
            open(PATH_INPUT_DAT.format(num), "wb") as fout:
        fin.seek(start)
        total = end - start + 1
        interval = 1024 * 1024
        times = int(total // (1024 * 1024))
        remain = total - times * interval
        buf = fin.read(remain)
        fout.write(buf)
        for i in range(times):
            fout.write(fin.read(interval))
    return 0


def build_db(is_split_dat=False):
    file_size = os.path.getsize(PATH_INPUT_DAT.format(""))

    # dat_file.seek((maxseekpoint -int(1*1024*1024)) * blocksize)
    # NO!!!!! REDITING!!!!
    one_s = int(file_size - 5.2358005 * 1024 * 1024 * 1024 + 18 + 48)
    interval = int((file_size - one_s) // 4)
    one_e = one_s + interval + 16 - 1
    two_s = one_e + 1
    two_e = two_s + interval + 35 - 2
    three_s = two_e + 1
    three_e = three_s + interval - 2
    four_s = three_e + 1
    four_e = file_size - 1

    if is_split_dat:
        split_dat(1, one_s, one_e)
        split_dat(2, two_s, two_e)
        split_dat(3, three_s, three_e)
        split_dat(4, four_s, four_e)
        return

    thread1 = DatabaseWriter("TH-1", one_s, one_e, 1)
    thread2 = DatabaseWriter("TH-2", two_s, two_e, 2)
    thread3 = DatabaseWriter("TH-3", three_s, three_e, 3)
    thread4 = DatabaseWriter("TH-4", four_s, four_e, 4)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()


class DatabaseWriter(threading.Thread):

    def __init__(self, threadID, seek_start, seek_end, id_t):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.A = seek_start
        self.B = seek_end
        self.id = id_t

    def run(self):
        num = write_db(self.threadID, self.A, self.B, self.id)
        with open("../../result/"+self.threadID + "-db-tx-in-out.txt", "w") as ff:
            ff.write(str(num))


def write_db(threadID, seek_start, seek_end, id):
    db = sqlite3.connect(PATH_OUTPUT_DB.format(id))
    cnt = 0

    with open(PATH_INPUT_DAT.format(id), 'rb') as f:
        t0 = time.time()
        for line in f:
            cnt += 1
            txto_noto_txfrom_noto_other = line.strip().decode().split('\t')
            # print(tx_block_nin_nout)
            db.execute("INSERT INTO tx_in_out (txto, txfrom, txfrom_no) VALUES ({}, {},{})".format(
                txto_noto_txfrom_noto_other[0],
                txto_noto_txfrom_noto_other[2],
                txto_noto_txfrom_noto_other[3]
            ))
            if cnt % FREQ_DB_COMMIT == 0:
                db.commit()

            now_point = f.tell()
            if cnt % FREQ_DISPLAY == 0:
                disp_progress(t0, 0, now_point, seek_end -
                              seek_start + 1, str(cnt % FREQ_DISPLAY) + "BY THREAD {}".format(id))
            if now_point > (seek_end - seek_start):
                break
    db.commit()
    db.close()
    return cnt  # total write_tx_in_out_flow


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

main()
