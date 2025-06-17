# Building a self-contained python package

This directory contains `nix` derivations for building a python wheel
for the current platform. Assuming you have `nix` installed, and have
enabled flakes (`nix` will warn you otherwise, and tell you how to
temporarily enable them), you can build a wheel like so:

```bash
# From the root of the repository:
nix build ./misc/packaging#treeppl-python
```

After that there should be a `.whl` file in `./result/` that can be
installed as usual through `pip`.


## Updating the treeppl version

First look in `flake.nix` for `treeppl.url` and make sure the url is
for the appropriate repository and branch. After that, run:

```bash
# From the root of the repository:
nix flake update --flake ./misc/packaging treeppl
```

This will update the `flake.lock` file to point to current commits.

## Updating the python package version

The version number presented to `pip` is presently specified in
`treeppl-python.nix`, look for `version = "<something>"` early
on. Editing this value will change the version number of the wheel the
next time it is built.

