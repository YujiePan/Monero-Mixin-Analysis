# -*- coding: utf-8 -*-
# @Author: pyj
# @Date:   2018-05-27 05:54:09
# @Last Modified by:   pyj
# @Last Modified time: 2018-05-27 05:54:22

from scipy.special import gamma
from scipy import integrate
import numpy as np

def gamma_pdf(x, alpha, beta):
    return beta**alpha * x**(alpha - 1) * np.exp(-beta * x) / gamma(alpha)


def gamma_cdf(x, alpha, beta):
    return [integrate.quad(gamma_pdf, 0, t, args=(alpha, beta)) for t in x]