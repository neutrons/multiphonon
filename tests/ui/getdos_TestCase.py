#!/usr/bin/env python
#

import os
import unittest

import pytest

pytestmark = pytest.mark.needs_ipywe

interactive = False

here = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(here, "..", "data")


class TestCase(unittest.TestCase):
    def test_contextload(self):
        from multiphonon.ui import Context

        cntxt = Context()
        cntxt.to_yaml("context.yaml")
        cntxt2 = Context()
        cntxt2.from_yaml("context.yaml")
        return

    def test1(self):
        """multiphonon.ui.getdos"""
        from multiphonon.ui import Context, getdos

        context = Context()
        context.to_yaml("context.yaml")
        context2 = Context()
        context2.from_yaml("context.yaml")
        s = str(context)

        context.sample_nxs = "sample.nxs"
        wiz = getdos.NxsWizardStart(context)
        wiz.show()
        wiz.sample_nxs = context.sample_nxs
        wiz.validate()
        wiz.nextStep()

        wiz = getdos.GetMTNxs(context)
        wiz.show()
        wiz.mt_nxs = "mt.nxs"
        wiz.validate()
        wiz.nextStep()

        wiz = getdos.GetEiT(context)
        wiz.show()
        wiz.validate()
        wiz.nextStep()

        wiz = getdos.GetEAxis(context)
        wiz.show()
        wiz.validate()
        context.Emin, context.Emax, context.dE = -50.0, 50.0, 1.0
        wiz.nextStep()

        wiz = getdos.GetQAxis(context)
        wiz.show()
        wiz.validate()
        context.Qmin, context.Qmax, context.dQ = 0.0, 15.0, 0.1
        # wiz.nextStep()

        context.initdos = "initdos.h5"
        wiz = getdos.GetInitDOS(context)
        wiz.show()
        wiz.initdos = "initdos.h5"
        wiz.validate()
        wiz.nextStep()

        wiz = getdos.GetParameters(context)
        wiz.show()
        wiz.validate()
        # wiz.nextStep()
        return

    pass  # end of TestCase


def exec_cmd(cmd):
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)


if __name__ == "__main__":
    interactive = True
    unittest.main()
