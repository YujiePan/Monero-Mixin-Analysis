# -*- coding: utf-8 -*-
# @Author: Yujie Pan
# @Date:   2018-05-29 01:25:44
# @Last Modified by:   Yujie Pan
# @Last Modified time: 2018-05-30 10:22:38

RESULT_FILE_NAME = "../../result/lab2-th{}-mix{}.txt"
LOG_OUTPUT = "../../result/lab2-th..-mix..-summary.log"

MIXS = [1, 3, 5, 7, 9, 11]
THREADS = [1, 2, 3, 4]

total = [[0 for trials in range(MIXS[m] + 2)] for m in range(len(MIXS))]
ge = [[t for t in range(MIXS[m] + 2)] for m in range(len(MIXS))]


def main():
    with open(LOG_OUTPUT, "w") as log:
        for m in range(len(MIXS)):
            for t in range(len(THREADS)):
                with open(RESULT_FILE_NAME.format(
                        THREADS[t], MIXS[m]), "r") as f:
                    nums = f.readlines(
                    )[-1].split('[')[1].split(']')[0].split(' ')
                    total[m] = list(map(
                        lambda x: int(x[0]) + int(x[1]), zip(nums, total[m])))
            ge[m] = sum(list(map(lambda x: int(x[0]) * int(x[1]),
                                 zip(ge[m], total[m])))) / sum(total[m])
            result = "MIX = {:0>2d}   GE = {:.3f}   {}".format(MIXS[m],
                                                               ge[m],
                                                               total[m])
            print(result)
            log.write(result + "\n")
    print("See result in", LOG_OUTPUT)

if __name__ == '__main__':
    main()
