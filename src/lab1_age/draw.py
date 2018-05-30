# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-30 21:31:30
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-30 22:45:49

import os
import time
import sys

LOG_FILE = "age_group{}.m"


def main():
    X = int(sys.argv[1])
    # X = 0 1 2 3

    gn = [0 for i in range(4)]
    g = [0 for i in range(4)]

    for i in range(4):
        gn[i], g[i] = count(i + 1, "../../result/age_distri{}.txt", i + 1)
    gsn, gs = count(0, "../../result/age_distri_{}-60000-1.txt", 0, 6e3, 600)

    ratio = [0 for i in range(4)]
    for i in range(X,X+1):
        ratio[i] = gn[i][0] / gn[0][0]  # 0-5999

    GN = [int(num * sum(ratio)) for num in gsn[:-1]]

    # GN_ = [gn[0][i] + gn[1][i] + gn[2][i] + gn[3][i]
    GN_ = [ gn[X][i]
           for i in range(1, len(gn[0]), 1)]
    G_Num = GN + GN_
    G_Left_B = gs[:-1] + g[0][1:]

    print(G_Left_B)
    print(len(G_Left_B), len(G_Num))

    with open(LOG_FILE.format(X), "w") as f:
        f.write("x=" + str(G_Left_B) + ";\n")
        f.write("y=" + str(G_Num) + ";\n")
        f.write("xx = x(1,1:end-1);\n")
        f.write("yy = y(1,1:end-1);\n")
        f.write("xxi = xx'; yyi=yy'; xxln= log(xx');")


def count(th, name, fmt, AGE_MAX=6e7, AGE_INTERVAL=int(6e7 * 1.0 / 1e4)):
    AGE_MIN = 0
    TXT_FILE = name.format(fmt)

    group_left_bound = list(
        range(AGE_MIN, int(AGE_MAX) + AGE_INTERVAL, AGE_INTERVAL))
    line = read_last_line(TXT_FILE.format(0))
    group_num = get_list(line)

    if len(group_num) == len(group_left_bound):
        return group_num, group_left_bound


def read_last_line(name):
    with open(name, "rb") as f:
        file_size = os.path.getsize(name)
        # f.seek(file_size - 1024 * 41)
        return f.readlines()[-1].decode()


def get_list(line):
    return [int(i.strip()) for i in line.split("[")[-1].split("]")[0].split(",")]

if __name__ == '__main__':
    main()
