import json
from operator import itemgetter
from tempfile import TemporaryDirectory
from subprocess import Popen, PIPE, STDOUT
import numpy as np

import tarfile
import shutil
import os
import importlib

from .exceptions import CompileError, InferenceError
from .serialization import from_json, to_json

def get_tpplc_binary():
    tpplc = shutil.which("tpplc")
    if tpplc:
        return tpplc

    # NOTE(vipa, 2025-06-04): The selfcontained compiler must be
    # deployed to a directory somewhere. There are three important
    # limitatations:
    # - The target directory must have a path that's at most 40
    #   characters long. This is because the compiler and its
    #   dependencies contain hard-coded absolute paths that must be
    #   rewritten, and we can't replace arbitrarily long strings in a
    #   binary. The temporary directory typically has a very short
    #   path.
    # - We'd like to remove the deployed compiler when we remove the
    #   python package. The temporary directory is cleared regularly
    #   on most systems.
    # - We'd like to allow multiple versions to be installed at once,
    #   e.g., via virtual envs. We accomplish this by including the
    #   package version in the deployed directory. This means that we
    #   might share (immutable) deployed directories between virtual
    #   envs, which seems fine, and that differing versions will get
    #   differing deployed directories.
    tmp_dir = '/tmp'
    deployed_basename = "@DEPLOYED_BASENAME@" # This will be substituted by nix when building the wheel
    tarball_name = "@TARBALL_NAME@" # This will be substituted by nix when building the wheel
    tppl_dir_path = os.path.join(tmp_dir, deployed_basename)
    if not os.path.isdir(tppl_dir_path):
        with importlib.resources.path('treeppl', tarball_name) as tarball:
            with tarfile.open(tarball) as tar:
                tar.extractall(tmp_dir)
    return os.path.join(tppl_dir_path, "tpplc")

class Model:
    def __init__(
        self,
        source=None,
        filename=None,
        method="smc-bpf",
        samples=1000,
        subsamples=None,
        **kwargs,
    ):
        self.temp_dir = TemporaryDirectory(prefix="treeppl_")
        if filename:
            source = open(filename).read()
        if not source:
            raise CompileError("No source code to compile.")
        with open(self.temp_dir.name + "/__main__.tppl", "w") as f:
            f.write(source)
        args = [
            get_tpplc_binary(),
            "__main__.tppl",
            "-m",
            method,
            "-p",
            str(samples),
        ]
        if subsamples:
            args.extend(["--subsample", "-n", str(subsamples)])
        for k, v in kwargs.items():
            args.append(f"--{k.replace('_', '-')}")
            if v is not True:
                args.append(str(v))
        with Popen(
            args=args, cwd=self.temp_dir.name, stdout=PIPE, stderr=STDOUT
        ) as proc:
            try:
                proc.wait()
            except KeyboardInterrupt:
                output = proc.stdout.read().decode("utf-8")
                output = output.replace("__main__.tppl", "source code")
                raise CompileError(f"Could not compile the TreePPL model:\n{output}")
            if proc.returncode != 0:
                output = proc.stdout.read().decode("utf-8")
                output = output.replace("__main__.tppl", "source code")
                raise CompileError(f"Could not compile the TreePPL model:\n{output}")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.temp_dir.cleanup()

    def __call__(self, **kwargs):
        with open(self.temp_dir.name + "/input.json", "w") as f:
            to_json(kwargs or {}, f)
        args = [
            f"{self.temp_dir.name}/out",
            f"{self.temp_dir.name}/input.json",
        ]
        with Popen(args=args, stdout=PIPE) as proc:
            return InferenceResult(proc.stdout)


class InferenceResult:
    def __init__(self, stdout):
        try:
            result = from_json(stdout)
        except json.decoder.JSONDecodeError:
            raise InferenceError("Could not parse the output from TreePPL.")
        self.samples = result.get("samples", [])
        self.weights = np.array(result.get("weights", []))
        self.nweights = np.exp(self.weights)
        self.norm_const = result.get("normConst", np.nan)

    def items(self, *args):
        return list(map(itemgetter(*args), self.samples))
