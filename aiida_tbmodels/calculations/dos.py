# -*- coding: utf-8 -*-

# Author: Junfeng Qiao <junfeng.qiao@epfl.ch>
"""
Defines the tbmodels.dos calculation.
"""
import six
from aiida import orm
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
            "kpoints",
            valid_type=orm.KpointsData,
            help="k-point mesh used in the DOS calculation"
        )
        spec.input(
            "parameters.energy_min",
            valid_type=orm.Float,
            required=False,
            help="Input parameters for the DOS caluclation"
        )
        spec.input(
            "parameters.energy_max",
            valid_type=orm.Float,
            required=False,
            help="Input parameters for the DOS caluclation"
        )
        spec.input(
            "parameters.energy_step",
            valid_type=orm.Float,
            required=False,
            help="Input parameters for the DOS caluclation"
        )
        spec.input(
            "parameters.smearing_type",
            valid_type=orm.Int,
            required=False,
            help="Input parameters for the DOS caluclation"
        )
        spec.input(
            "parameters.smearing_width",
            valid_type=orm.Float,
            required=False,
            help="Input parameters for the DOS caluclation"
        )
        spec.input(
            'metadata.options.parser_name',
            valid_type=six.string_types,
            default='tbmodels.dos'
        )
        spec.output(
            'dos',
            valid_type=orm.XyData,
            help="calculated DOS data"
        )
        spec.exit_code(400, 'ERROR_CHECK_KPOINTS_MESH',
            message='Wrong input parameter: kpoints, the KpointsData does not contain a mesh'
        )
        spec.exit_code(401, 'ERROR_CHECK_PARAMETERS_ENERGY_RANGE',
            message='Wrong input parameter: energy_mix >= energy_max'
        )
        spec.exit_code(403, 'ERROR_CHECK_PARAMETERS_ENERGY_STEP',
            message='Wrong input parameter: energy_step <= 0'
        )

    def check_parameters(self):
        try:
            kmesh = self.inputs.kpoints.get_kpoints_mesh()
        except AttributeError:
            return self.exit_codes.ERROR_CHECK_KPOINTS_MESH
        try:
            energy_min = self.inputs.parameters['energy_min']
            energy_max = self.inputs.parameters['energy_max']
        except KeyError:
            pass
        else:
            if energy_min >= energy_max:
                return self.exit_codes.ERROR_CHECK_PARAMETERS_ENERGY_RANGE
        try:
            energy_step = self.inputs.parameters['energy_step']
        except KeyError:
            pass
        else:
            if energy_step <= 0:
                return self.exit_codes.ERROR_CHECK_PARAMETERS_ENERGY_STEP

    def prepare_for_submission(self, tempfolder):
        self.check_parameters()

        calcinfo, codeinfo = super(DosCalculation,
                                   self).prepare_for_submission(tempfolder)
        calcinfo.retrieve_list = [self.inputs.metadata.options.output_filename]

        kmesh = self.inputs.kpoints.get_kpoints_mesh()[0]

        cmdline_params = ['dos', '-k', str(kmesh[0]), str(kmesh[1]), str(kmesh[2])]
        try:
            energy_min = self.inputs.parameters['energy_min']
            energy_max = self.inputs.parameters['energy_max']
        except KeyError:
            pass
        else:
            cmdline_params.extend(
                ['-emin', str(energy_min.value), '-emax', str(energy_max.value)])
        try:
            energy_step = self.inputs.parameters['energy_step']
        except KeyError:
            pass
        else:
            cmdline_params.extend(['-de', str(energy_step.value)])
        try:
            smearing_type = self.inputs.parameters['smearing_type']
        except KeyError:
            pass
        else:
            cmdline_params.extend(['-s', str(smearing_type.value)])
        try:
            smearing_width = self.inputs.parameters['smearing_width']
        except KeyError:
            pass
        else:
            cmdline_params.extend(['-w', str(smearing_width.value)])
        codeinfo.cmdline_params = cmdline_params
        # self.report('cmdline_params {}'.format(str(cmdline_params)))
        return calcinfo
