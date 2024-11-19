#!/usr/bin/env python3

import treeppl
import matplotlib.pyplot as plt
import seaborn as sns


with treeppl.Model(filename="coin.tppl", samples=100000) as coin:
    res = coin(
        outcomes=[
            True, True, True, False, True, False, False, True, True, False,
            False, False, True, False, True, False, False, False, False, False,
        ]
    )
    sns.histplot(
        x=res.samples, weights=res.nweights, bins=100, stat="density", kde=True
    )
    plt.show()
