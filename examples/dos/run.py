#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

# Author: Junfeng Qiao <junfeng.qiao@epfl.ch>
"""
Runs a 'tbmodels dos' calculation.
"""

from __future__ import division, print_function, unicode_literals

import os

from aiida.orm import Code
from aiida.orm import SinglefileData
from aiida.orm.querybuilder import QueryBuilder
from aiida.engine import run_get_pk
from aiida.plugins import DataFactory

from aiida_tbmodels.calculations.dos import DosCalculation


def get_singlefile_instance(description, path):
    """
    Retrieve an instance of SinglefileData with the given description, loading it from ``path`` if it does not exist.
    """
    query_builder = QueryBuilder()
    query_builder.append(
        SinglefileData, filters={'description': {
            '==': description
        }}
    )
    res = query_builder.all()
    if len(res) == 0:
        # create archive
        res = SinglefileData(file=os.path.abspath(path))
        res.description = description
        res.store()
    elif len(res) > 1:
        raise ValueError(
            'Query returned more than one matching SinglefileData instance.'
        )
    else:
        res = res[0][0]
    return res


def run_dos():
    """
    Creates and runs the dos calculation.
    """
    builder = DosCalculation.get_builder()
    builder.code = Code.get_from_string('tbmodels')

    builder.tb_model = get_singlefile_instance(
        description=u'InSb TB model', path='../eigenvals/reference_input/model.hdf5'
    )

    # single-core on local machine
    builder.metadata.options = dict(
        resources=dict(num_machines=1, tot_num_mpiprocs=1), withmpi=False
    )

    builder.kpoints = DataFactory('array.kpoints')()
    builder.kpoints.set_kpoints_mesh([4, 4, 4], offset=[0, 0, 0])

    param = {
        'energy_range': [-10, 10],
        'num_energy': 200,
        'smearing_type': 0,
        'smearing_width': 0.1
    }
    builder.parameters = DataFactory('dict')(dict=param)

    result, pid = run_get_pk(builder)
    print('\nRan calculation with PID', pid)
    print('Result:', result)


if __name__ == '__main__':
    run_dos()
