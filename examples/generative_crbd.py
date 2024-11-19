#!/usr/bin/env python3

import treeppl
from Bio import Phylo


params = {"time": 5.0, "lambda": 1.0, "mu": 0.1}

with treeppl.Model(filename="generative_crbd.tppl", samples=1) as generative_crbd:
    result = generative_crbd(**params)
    tree = result.samples[0]
    tree = Phylo.BaseTree.Clade(
        branch_length=params["time"] - tree.age, clades=[tree.to_biopython()]
    )
    Phylo.draw(tree)
