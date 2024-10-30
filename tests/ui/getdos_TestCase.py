#!/usr/bin/env python
#

import os
import tempfile
import unittest

import pytest

pytestmark = pytest.mark.needs_ipywe

interactive = False

here = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(here, "..", "data")


class TestCase(unittest.TestCase):
    def test_contextload(self):
        from multiphonon.ui import Context

        with tempfile.TemporaryDirectory() as tmpdirname:
            context_filepath = os.path.join(tmpdirname, "context.yaml")
            cntxt = Context()
            cntxt.to_yaml(context_filepath)
            cntxt2 = Context()
            cntxt2.from_yaml(context_filepath)
            return


def exec_cmd(cmd):
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)


if __name__ == "__main__":
    interactive = True
    unittest.main()
