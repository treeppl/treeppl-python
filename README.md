# Python Interface to TreePPL

This Python package serves as a versatile interface for creating and running inference on [TreePPL](https://treeppl.org/) programs.

## Installation

Begin by installing the package through pip, using the following shell command:

```shell
pip install "git+https://github.com/treeppl/treeppl-python#egg=treeppl"
```

Make sure that you have already installed [TreePPL](https://treeppl.org/) and that the `tpplc` executable is accessible in your system's `PATH`.

## Example of use

```python
import treeppl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define a TreePPL model source code
source = """\
model function coin(outcomes: Bool[]) => Real {
  assume p ~ Beta(2.0, 2.0);
  for i in 1 to (length(outcomes)) {
    observe outcomes[i] ~ Bernoulli(p);
  }
  return(p);
}
"""

# Create a TreePPL model instance
with treeppl.Model(source=source, samples=10_000) as coin:
    # Run the inference on the model
    res = coin(outcomes=[True, True, True, False, True, False, False, True, True, False, False, False, True, False, True, False, False, True, False, False])
    
    # Visualize the results using Seaborn and Matplotlib
    sns.histplot(x=res.samples, weights=res.nweights, bins=100, stat="density", kde=True)
    plt.show()
```

Parameters of `treeppl.Model()`:

- `source`: The source code of a TreePPL model.
- `filename`: The name of the TreePPL model file.
- `method`: The inference method to be used, with `smc-bpf` as the default.
- `samples`: The number of samples to be collected, with a default value of 1,000.
- Any additional named parameters will be passed as additional arguments to `tpplc`. For example, `stack_size=10000` will add `--stack-size 10000` to the arguments of `tpplc`.

Please note that either `source` or `filename` must be explicitly specified when creating a `treeppl.Model` instance.

`treeppl.Model()` returns an instance that can be called directly to run inference, specifying the model's arguments as named parameters, as shown in the example above.

The return value is an instance of `treeppl.InferenceResult`, which includes the following properties:

- `samples`: The samples returned from TreePPL.
- `weights`: The log-weights of the samples.
- `nweights`: The normalized weights of the samples.
- `norm_const`: The logarithm of the marginal likelihood.
