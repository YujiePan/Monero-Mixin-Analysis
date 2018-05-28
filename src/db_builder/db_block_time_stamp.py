# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-28 12:37:27
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-28 19:37:25

import time
import random,os

def block_age_write(inputfile, outputfile):
    with open(inputfile,'rb') as infile, open(outputfile,"wb") as outfile:
        for line in infile:
            data = line.strip().decode("ascii").split('\t');
            useful = data[0]+"\t"+data[2]+"\n"
            outfile.write(useful.encode())


def init():
    file = '../../db/block_time_stamp.tsv'
    bh = [0 for i in range(509000)]
    with open(file,"rb") as f:
        for line in f:
            dat =  line.strip().decode("ascii").split("\t")
            bh[int(dat[0])] = int(dat[1]) 
    return bh


# block_age_write("d:/blockchain/bh.dat/bh.dat",'block_time_stamp.tsv')