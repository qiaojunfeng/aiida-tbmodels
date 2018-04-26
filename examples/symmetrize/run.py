#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
"""
Runs a 'tbmodels symmetrize' calculation.
"""

from __future__ import division, print_function, unicode_literals

import os

from aiida.orm import Code
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm.data.singlefile import SinglefileData
from aiida.work.launch import run_get_pid

from aiida_tbmodels.calculations.symmetrize import SymmetrizeCalculation


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
        res = SinglefileData()
        res.add_path(os.path.abspath(path))
        res.description = description
        res.store()
    elif len(res) > 1:
        raise ValueError(
            'Query returned more than one matching SinglefileData instance.'
        )
    else:
        res = res[0][0]
    return res


def run_symmetrize():
    """
    Creates and runs the symmetrize calculation.
    """
    builder = SymmetrizeCalculation.get_builder()

    builder.code = Code.get_from_string('tbmodels')

    # single-core on local machine
    builder.options = dict(
        resources=dict(num_machines=1, tot_num_mpiprocs=1), withmpi=False
    )

    builder.tb_model = get_singlefile_instance(
        description=u'InAs unsymmetrized TB model',
        path='./reference_input/model_nosym.hdf5'
    )

    builder.symmetries = get_singlefile_instance(
        description=u'InAs symmetries',
        path='./reference_input/symmetries.hdf5'
    )

    result, pid = run_get_pid(builder)
    print('\nRan calculation with PID', pid)
    print('Result:', result)


if __name__ == '__main__':
    run_symmetrize()
