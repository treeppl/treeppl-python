---
layout: default
title: Installation
---
# Installation

To make using TreePPL with Python convenient, you can install the bundled Python package that includes the TreePPL compiler.
Follow the steps below to install the package.

## Download the prebuilt package

1. Go to the [TreePPL Python releases page](https://github.com/treeppl/treeppl-python/releases).
2. Under the latest release, expand the *Assets* section.
3. Download the `.whl` (wheel) file corresponding to your operating system.

Prebuilt wheels are currently available for Linux and macOS.
If you are using Windows, please install the Linux wheel via WSL (Windows Subsystem for Linux).

## Install the package

After downloading the `.whl` file, open a terminal and navigate to the directory containing it.
Then install it using `pip`:

```bash
pip install treeppl-<version>-py3-none-<os>.whl
```

For example:
```bash
treeppl-0.1-py3-none-macosx_11_0_arm64.whl
```

## Verify the installation

To confirm the installation was successful, import the package inside a Python session:
```python
import treeppl
```
If the command run without errors, TreePPL is ready to use.

## Next steps

You can now proceed to the [Getting Started](getting-started) guide to learn how to define and run TreePPL models in Python.
