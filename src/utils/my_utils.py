# -*- coding: utf-8 -*-
# @Author: pyj
# @Date:   2018-05-27 05:54:09
# @Last Modified by:   pyj
# @Last Modified time: 2018-05-27 05:54:22


import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as  plt

def gamma_pdf(x, alpha, beta):
    return beta**alpha * x**(alpha - 1) * np.exp(-beta * x) / gamma(alpha)


def gamma_cdf(x, alpha, beta):
    return [integrate.quad(gamma_pdf, 0, t, args=(alpha, beta)) for t in x]


ALPHA = 19.28
BETA = 1.61
D = gamma(ALPHA, scale=1/BETA)

x = np.linspace(0,20,1000)
plt.plot(x, D.pdf(x))
plt.show()