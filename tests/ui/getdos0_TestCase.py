#!/usr/bin/env python
#

import pytest

pytestmark = pytest.mark.needs_ipywe

interactive = False

import os

here = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(here, "..", "data")


import unittest


class TestCase(unittest.TestCase):
    def test1(self):
        "multiphonon.ui.getdos0"
        from multiphonon.ui import getdos0

        getdos0.notebookUI("sample.nxs", "mt.nxs")
        getdos0.log_progress("message")
        return

    pass  # end of TestCase


def exec_cmd(cmd):
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)


if __name__ == "__main__":
    interactive = True
    unittest.main()

# End of file
