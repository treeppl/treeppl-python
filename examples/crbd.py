#!/usr/bin/env python3

import treeppl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


alcedinidae = treeppl.Tree.load("trees/Alcedinidae.phyjson", format="phyjson")
samples = None
with treeppl.Model(filename="crbd.tppl", samples=10000, subsamples=10) as crbd:
    for i in range(1000):
        res = crbd(tree=alcedinidae)
        samples = pd.concat([
            samples,
            pd.DataFrame({
                "lambda": res.items(0), "mu": res.items(1), "lweight": res.norm_const
            })
        ])
        weights = np.exp(samples.lweight - samples.lweight.max())
        plt.clf()
        sns.kdeplot(data=samples, x="lambda", weights=weights)
        sns.kdeplot(data=samples, x="mu", weights=weights)
        plt.pause(0.05)
