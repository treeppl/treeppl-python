#!/usr/bin/env python3

import sys

sys.path.append("..")

import treeppl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


tree = treeppl.Tree.load_phyjson("trees/Alcedinidae.phyjson")

sweep_samples = 10_000
sweep_subsamples = 100

lweights = []
samples = []
with treeppl.Model(filename="crbd.tppl", samples=sweep_samples) as crbd:
    #
    while True:
        res = crbd(tree=tree)
        samples.extend(res.subsample(sweep_subsamples))
        lweights.extend([res.norm_const] * sweep_subsamples)
        plt.clf()
        sns.kdeplot(x=samples, weights=np.exp(np.array(lweights) - max(lweights)))
        plt.pause(0.05)
