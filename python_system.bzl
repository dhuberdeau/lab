# Copyright 2021 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""Generates a local repository that points at the system's Python installation."""

_BUILD_FILE = '''# Description:
#   Build rule for Python

exports_files(["defs.bzl"])

cc_library(
    name = "python_headers",
    hdrs = select({
        "@bazel_tools//tools/python:PY2": glob(["python2/**/*.h", "numpy2/**/*.h"]),
        "@bazel_tools//tools/python:PY3": glob(["python3/**/*.h", "numpy3/**/*.h"]),
    }),
    includes = select({
        "@bazel_tools//tools/python:PY2": ["python2", "numpy2"],
        "@bazel_tools//tools/python:PY3": ["python3", "numpy3"],
    }),
    visibility = ["//visibility:public"],
)
'''

_GET_PYTHON_INCLUDE_DIR = """
import sys
from distutils.sysconfig import get_python_inc
from numpy import get_include
sys.stdout.write("{}\\n{}\\n".format(get_python_inc(), get_include()))
""".strip()

def _python_repo_impl(repository_ctx):
    """Creates external/<reponame>/BUILD, a python3 symlink, and other files."""

    repository_ctx.file("BUILD", _BUILD_FILE)

    if repository_ctx.attr.py_version in ["PY2", "PY2AND3"]:
        result = repository_ctx.execute(["python2", "-c", _GET_PYTHON_INCLUDE_DIR])
        if result.return_code:
            fail("Failed to run local Python2 interpreter: %s" % result.stderr)
        pypath, nppath = result.stdout.splitlines()
        repository_ctx.symlink(pypath, "python2")
        repository_ctx.symlink(nppath, "numpy2")

    if repository_ctx.attr.py_version in ["PY3", "PY2AND3"]:
        result = repository_ctx.execute(["python3", "-c", _GET_PYTHON_INCLUDE_DIR])
        if result.return_code:
            fail("Failed to run local Python3 interpreter: %s" % result.stderr)
        pypath, nppath = result.stdout.splitlines()
        repository_ctx.symlink(pypath, "python3")
        repository_ctx.symlink(nppath, "numpy3")

python_repo = repository_rule(
    implementation = _python_repo_impl,
    configure = True,
    local = True,
    attrs = {"py_version": attr.string(default = "PY2AND3", values = ["PY2", "PY3", "PY2AND3"])},
)
