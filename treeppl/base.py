import json
from operator import itemgetter
from tempfile import TemporaryDirectory
import subprocess
import numpy as np
import tarfile
import os
import importlib
import shlex

from .exceptions import CompileError, InferenceError
from .serialization import from_json, to_json


def get_tpplc_binary():
    if os.environ.get("TPPLC"):
        return os.environ["TPPLC"]
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
    tmp_dir = "/tmp"
    deployed_basename = "@DEPLOYED_BASENAME@"  # This will be substituted by nix when building the wheel
    tarball_name = "@TARBALL_NAME@"  # This will be substituted by nix when building the wheel
    tppl_dir_path = os.path.join(tmp_dir, deployed_basename)
    if not os.path.isdir(tppl_dir_path):
        with importlib.resources.path("treeppl", tarball_name) as tarball:
            with tarfile.open(tarball) as tar:
                if hasattr(tarfile, "tar_filter"):
                    tar.extractall(tmp_dir, filter="tar")
                else:
                    # NOTE(vipa, 2025-11-20): This allows us to support Python < 3.12
                    tar.extractall(tmp_dir)
    return os.path.join(tppl_dir_path, "tpplc")


class Arguments(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class CompileArguments(Arguments):
    def as_list(self):
        res = []
        for k, v in self.items():
            k = k.replace("_", "-")
            res.append(f"-{k}" if len(k) == 1 else f"--{k}")
            if v is not True:
                res.append(str(v))
        return res

    def parse_opts(self, s):
        t = shlex.split(s)
        i = 0
        while i < len(t):
            k = t[i].lstrip("-").replace("-", "_")
            if i + 1 < len(t) and not t[i + 1].startswith("-"):
                v = t[i + 1]
                i += 1
                if v.isdigit():
                    v = int(v)
                else:
                    try:
                        v = float(v)
                    except:
                        pass
            else:
                v = True
            self[k] = v
            i += 1


class RunArguments(Arguments):
    def load_json(self, filename):
        with open(filename) as f:
            self.update(from_json(f))

    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            data = from_json(f)
        return cls(**data)

    def save_json(self, filename):
        with open(filename, "w") as f:
            to_json(self, f)


class Model:
    def __init__(self, source=None, filename=None, **kwargs):
        self.compile_arguments = None
        self.run_arguments = None
        self.source = source
        if filename:
            with open(filename) as f:
                self.source = f.read()
        self.temp_dir = TemporaryDirectory(prefix="treeppl_")
        self.compile(**kwargs)

    def compile(self, **kwargs):
        self.compile_arguments = CompileArguments(kwargs)
        if not self.source:
            raise CompileError("no source code to compile")
        with open(self.temp_dir.name + "/__main__.tppl", "w") as f:
            f.write(self.source)
        args = [get_tpplc_binary(), "__main__.tppl"]
        args.extend(self.compile_arguments.as_list())
        result = None
        try:
            result = subprocess.run(args=args, cwd=self.temp_dir.name, capture_output=True, text=True)
        except KeyboardInterrupt:
            pass
        if result is None:
            raise CompileError("could not compile the TreePPL model")
        elif result.returncode != 0:
            output = result.stdout.replace("__main__.tppl", "source code")
            raise CompileError(f"could not compile the TreePPL model:\n{output}")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.temp_dir.cleanup()

    def run(self, arguments=None, **kwargs):
        self.run_arguments = RunArguments(arguments or {}, **kwargs)
        self.run_arguments.save_json(self.temp_dir.name + "/input.json")
        args = [
            f"{self.temp_dir.name}/out",
            f"{self.temp_dir.name}/input.json",
        ]
        with subprocess.Popen(args=args, stdout=subprocess.PIPE) as proc:
            return InferenceResult(proc.stdout)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


class InferenceResult:
    def __init__(self, stdout):
        self.result = None
        try:
            self.result = from_json(stdout)
        except json.decoder.JSONDecodeError:
            raise InferenceError("could not parse the output from TreePPL")
        self.samples = self.result.get("samples", [])
        self.weights = np.array(self.result.get("weights", []))
        self.nweights = np.exp(self.weights)
        self.norm_const = self.result.get("normConst", np.nan)

    def items(self, *args):
        return list(map(itemgetter(*args), self.samples))

    def save_json(self, filename):
        with open(filename, "w") as f:
            to_json(self.result, f)
