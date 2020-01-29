# -*- coding: utf-8 -*-

# Author: Junfeng Qiao <junfeng.qiao@epfl.ch>
"""
Defines the parser for dos in TBmodels HDF5 format.
"""

from aiida.plugins import DataFactory
from aiida.parsers.parser import Parser


class DosParser(Parser):
    """
    Parse TBmodels DOS output to a XyData.
    """
    def parse(self, **kwargs):  # pylint: disable=inconsistent-return-statements
        try:
            out_folder = self.retrieved
        except KeyError as err:
            self.logger.error("No retrieved folder found")
            raise err

        try:
            with out_folder.open(
                self.node.get_option('output_filename'), 'rb'
            ) as output_file:
                import h5py
                f = h5py.File(output_file, 'r')
                import numpy as np
                e = f['energy'][:]
                d = f['dos'][:]
                dos_node = DataFactory('array.xy')()
                dos_node.set_x(e, 'dos_energy', 'eV')
                dos_node.set_y(d, 'dos', 'states/eV')
        except IOError:
            return self.exit_codes.ERROR_OUTPUT_DOS_FILE

        self.out('output_dos', dos_node)
