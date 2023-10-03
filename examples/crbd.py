#!/usr/bin/env python3

import sys

sys.path.append("..")

import treeppl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


tree = treeppl.Tree.load("trees/Alcedinidae.phyjson", format="phyjson")

samples = None
with treeppl.Model(filename="crbd.tppl", samples=10_000) as crbd:
    while True:
        res = crbd(tree=tree)
        samples = pd.concat([samples, pd.DataFrame({
            'lambda': res.subsample(10),
            'lweight': res.norm_const,
        })])
        plt.clf()
        sns.kdeplot(data=samples, x="lambda", weights=np.exp(samples.lweight - samples.lweight.max()))
        plt.pause(0.05)
