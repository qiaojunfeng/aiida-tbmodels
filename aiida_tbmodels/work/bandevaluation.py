#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>

# from aiida.work.run import submit
from aiida.orm.data.base import Str, Float
from aiida.work.run import submit
from aiida.work.workchain import WorkChain, ToContext
from aiida.orm import Code, Computer, DataFactory, CalculationFactory

class BandEvaluation(WorkChain):
    @classmethod
    def define(cls, spec):
        super(BandEvaluation, cls).define(spec)

        spec.input('tb_model', valid_type=DataFactory('singlefile'))
        spec.input('reference_bands', valid_type=DataFactory('array.bands'))
        spec.input('bands_inspect_code', valid_type=Code)
        spec.input('tbmodels_code', valid_type=Code)

        spec.outline(
            cls.calculate_bands, cls.calculate_difference, cls.finalize
        )

    def setup_calc(self, calc_string, code_param):
        process = CalculationFactory(calc_string).process()
        inputs = process.get_inputs_template()
        inputs.code = self.inputs[code_param]
        inputs._options.resources = {'num_machines': 1}
        inputs._options.withmpi = False
        return process, inputs

    def calculate_bands(self):
        process, inputs = self.setup_calc('tbmodels.eigenvals', 'tbmodels_code')
        inputs.tb_model = self.inputs.tb_model
        inputs.kpoints = self.inputs.reference_bands
        import time
        time.sleep(5)
        self.report("Running TBmodels eigenvals calculation...")
        pid = submit(process, **inputs)
        return ToContext(calculated_bands=pid)

    def calculate_difference(self):
        process, inputs = self.setup_calc('bands_inspect.difference', 'bands_inspect_code')
        inputs.bands1 = self.inputs.reference_bands
        inputs.bands2 = self.ctx.calculated_bands.out.bands
        self.report("Running difference calculation...")
        pid = submit(process, **inputs)
        return ToContext(difference=pid)

    def finalize(self):
        self.out("difference", Float(self.ctx.difference.out.difference))
