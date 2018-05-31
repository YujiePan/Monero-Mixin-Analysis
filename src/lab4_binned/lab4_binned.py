# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-30 11:37:19
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-31 05:04:01

import sqlite3
import os
import math
import sys
import time
import random
import datetime
from scipy.stats import gamma
sys.path.append("..")
from db_builder import db_block_time_stamp
BLOCK_TIME = db_block_time_stamp.init()


SIZE_DB = [0, 32929106, 33036408, 32872161, 32784690]
MIX_SIZE = 0
SIMU_TIMES = 250
ALPHA = 13.19
BETA = 0.86
D = gamma(ALPHA, scale=1 / BETA)


def main():
    try:
    	th = int(sys.argv[1])
        bin_num = int(sys.argv[2])
        bin_size = int(sys.argv[3])
    except:
    	th = int(input("DB no.(1-4): "))
        bin_num = int(input("bin num: "))
        bin_size = int(input("bin size: "))
    info = simulate(th, bin_num, bin_size, SIZE_DB[th],  SIMU_TIMES)
    write_log(
        th, "../../result/lab4-th{}-binnum{}-binsize{}.txt".format(
        	th, bin_num, bin_size), info)


def write_log(i, name, content):
    with open(name, "a") as f:
        f.write("[{}] TH{}: {}\r\n".format(
            timestamp2string(time.time()), i, content))


def line_txto_txfrom_nfrom(cur, random_num):
    cur.execute("SELECT * FROM tx_in_out LIMIT 1 OFFSET {};".format(random_num))
    for item in cur.fetchall():
        return item[0:3]
    return 0, 0, 0


def block_minitxid_via_txid(cur, tx, n):
    cur.execute("SELECT * FROM TXTOBLOCK WHERE txid = {};".format(tx))
    for item in cur.fetchall():
        return item[1], item[2] + n
    return 3, 3


def block_via_minitxid(cur, mini_id):
    cur.execute(
        "SELECT * FROM TXTOBLOCK WHERE MINITX_STARTING <= {} ORDER BY block desc LIMIT 1;".format(
            mini_id))
    for item in cur.fetchall():
        return item[1]


def minitxid_via_block(cur, block):
    cur.execute(
        "SELECT * FROM TXTOBLOCK WHERE BLOCK = {} LIMIT 1;".format(block))
    for item in cur.fetchall():
        return item[2] + random.randint(-15, 15)


def get_time_stamp(block, mini_id):
    return random.randint(BLOCK_TIME[block - 1], BLOCK_TIME[block])


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


def mapped_bin(mini_tx_id, bin_size):
	res = list(range(-15 * 12, 0)) + list(range(1, 15 * 12))
	random.shuffle(res)
	res.append(0)
	return [i + mini_tx_id for i in res[-bin_size:]]


def add_candidate(L, bins, first_bin=False):
	if first_bin:
		L = bins
		return
    for i in bins:
        if i not in L:
            L.append(i)
        else:
        	i = i-1
            while i in L:
                i = i - 1
            L.append(i)


def simulate(thread_id,  bin_num, bin_size,  max_random,  SIMU_TIMES):
    t1 = time.time()  # get current time

    DB_TX_IN_OUT_PATH = "../../db/new_tx_in_out{}.sqlite".format(thread_id)
    DB_TX_BL_PATH = "../../db/new_tx_block.sqlite"

    cur_tx_in_out = sqlite3.connect(DB_TX_IN_OUT_PATH).cursor()
    cur_tx_block = sqlite3.connect(DB_TX_BL_PATH).cursor()

    guess_times = [0 for i in range(bin_num*bin_size + 1)]

    k = 1
    while k < SIMU_TIMES:
        if k % 10 == 0:
            disp_progress(t1, 0, k, SIMU_TIMES, str(k))

        # selected_mini = [0 for jj in range(pool_size + 1)]
        selected_mini = []
        now_tx = real_tx = real_nfrom = 0

        try:
            while now_tx == 0:
                now_tx, real_tx, real_nfrom = line_txto_txfrom_nfrom(
                    cur_tx_in_out, k * 30 + 1)

            real_block, real_mini_id = block_minitxid_via_txid(
                cur_tx_block, real_tx, real_nfrom)
            now_block, now_mini_id = block_minitxid_via_txid(
                cur_tx_block, now_tx, 0)
            # print("BLOCK at", now_block)

            now_time = get_time_stamp(now_block, now_mini_id)
            real_time = get_time_stamp(real_block, real_mini_id)
            real_age = now_time - real_time

            # print("TH", thread_id, "Random Choose:", now_tx, "from",
            #      real_tx, real_nfrom, "mini_id", real_mini_id, "age:",
            #      real_time_ago)
            # row_prob[0] = 1

            add_candidate(selected_mini,mapped_bin(real_mini_id, bin_size), True)

            for j in range(bin_num-1):
                age = 0
                while age<2 or not sampled_mini:
                    sampled_age = random.gammavariate(ALPHA, BETA)
                    # print("ready choose", time_ago)
                    sampled_block = time_to_block(now_time-sampled_age)
                    sampled_mini = minitxid_via_block(DB_TX_BL_PATH,sampled_block)
                mapped = mapped_bin(sampled_mini, bin_size)
                add_candidate(selected_mini, mapped, False)
            # print("\tTH", thread_id, "choose_time_ago:", selected_mini)

         	
            guess_time = guess(selected_mini, real_time_ago, bin_num*bin_size)
            guess_times[MIX + 1 - guess_time] += 1
            # print("\tTH", thread_id, "final:", now_tx, "from", real_tx,
            #      real_nfrom, "guess time:", MIX + 1 - guess_time)
            k += 1
        except:
            pass

    info = "OK: {}".format(str(guess_times))
    return info


def find_index(arr, element, largest):
    for i in range(largest, -1, -1):
        if arr[i] == element:
            return i
    print("-1")
    return -1


def timestamp2string(timeStamp):
    try:
        d = datetime.datetime.fromtimestamp(timeStamp)
        str1 = d.strftime("%Y-%m-%d-%H-%M-%S.%f")
        # 2015-08-28 16:43:37.283000'
        return str1
    except Exception as e:
        print(e)
        return ''

if __name__ == '__main__':
    main()
