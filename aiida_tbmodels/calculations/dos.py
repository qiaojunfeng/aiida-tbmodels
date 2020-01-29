# -*- coding: utf-8 -*-

# Author: Junfeng Qiao <junfeng.qiao@epfl.ch>
"""
Defines the tbmodels.dos calculation.
"""

import six

from aiida.plugins import DataFactory

from ._base import ModelInputBase


class DosCalculation(ModelInputBase):
    """
    Calculation class for the 'tbmodels dos' command, which computes the density of states from a given tight-binding model.
    """

    _DEFAULT_OUTPUT_FILE = 'dos.hdf5'

    @classmethod
    def define(cls, spec):
        super(DosCalculation, cls).define(spec)

        spec.input(
            "parameters",
            valid_type=DataFactory('dict'),
            help="Input parameters for the DOS caluclation"
        )
        spec.input(
            "kpoints",
            valid_type=DataFactory('array.kpoints'),
            help="k-point mesh used in the DOS calculation"
        )
        spec.input(
            'metadata.options.parser_name',
            valid_type=six.string_types,
            default='tbmodels.dos'
        )
        spec.output(
            'output_dos',
            valid_type=DataFactory('array.xy'),
            help="calculated DOS data"
        )
        spec.exit_code(400, 'ERROR_CHECK_KPOINTS_MESH',
            message='Wrong input parameter: kmesh'
        )
        spec.exit_code(401, 'ERROR_CHECK_PARAMETERS_ENERGY_RANGE',
            message='Wrong input parameter: energy range'
        )
        spec.exit_code(402, 'ERROR_CHECK_PARAMETERS_NUM_ENERGY',
            message='Wrong input parameter: number of energy points'
        )
        spec.exit_code(403, 'ERROR_CHECK_PARAMETERS_SMEARING',
            message='Wrong input parameter: smearing type'
        )
        spec.exit_code(404, 'ERROR_CHECK_PARAMETERS_SMEARING_WIDTH',
            message='Wrong input parameter: smearing width'
        )

    def check_parameters(self):
        try:
            kmesh = self.inputs.kpoints.get_kpoints_mesh()
        except AttributeError:
            self.exit_code.ERROR_CHECK_KPOINTS_MESH
        try:
            energy_range = self.inputs.parameters['energy_range']
        except AttributeError:
            self.exit_code.ERROR_CHECK_PARAMETERS_ENERGY_RANGE
        if len(energy_range) != 2:
            self.exit_code.ERROR_CHECK_PARAMETERS_ENERGY_RANGE
        if energy_range[1] <= energy_range[0]:
            self.exit_code.ERROR_CHECK_PARAMETERS_ENERGY_RANGE
        try:
            num_energy = self.inputs.parameters['num_energy']
        except AttributeError:
            self.exit_code.ERROR_CHECK_PARAMETERS_NUM_ENERGY
        if num_energy < 1:
            self.exit_code.ERROR_CHECK_PARAMETERS_NUM_ENERGY
        try:
            smearing = self.inputs.parameters['smearing_type']
        except AttributeError:
            self.exit_code.ERROR_CHECK_PARAMETERS_SMEARING
        try:
            smearing_width = self.inputs.parameters['smearing_width']
        except AttributeError:
            self.exit_code.ERROR_CHECK_PARAMETERS_SMEARING_WIDTH
        

    def prepare_for_submission(self, tempfolder):
        self.check_parameters()

        calcinfo, codeinfo = super(DosCalculation,
                                   self).prepare_for_submission(tempfolder)
        calcinfo.retrieve_list = [self.inputs.metadata.options.output_filename]

        kmesh = self.inputs.kpoints.get_kpoints_mesh()[0]

        codeinfo.cmdline_params = ['dos',
        '-k', str(kmesh[0]), str(kmesh[1]), str(kmesh[2]), 
        '-e', str(self.inputs.parameters['energy_range'][0]), str(self.inputs.parameters['energy_range'][1]),
        '-n', str(self.inputs.parameters['num_energy']),
        '-s', str(self.inputs.parameters['smearing_type']),
        '-w', str(self.inputs.parameters['smearing_width'])
        ]
        return calcinfo
