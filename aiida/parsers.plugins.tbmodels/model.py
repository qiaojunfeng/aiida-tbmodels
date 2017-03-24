# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>

import json

from aiida.parsers.parser import Parser
from aiida.orm.data.singlefile import SinglefileData

class ModelParser(Parser):
    """
    Parse TBmodels output to a SinglefileData containing the model file.
    """
    def parse_with_retrieved(self, retrieved):
        try:
            out_folder = retrieved[self._calc._get_linkname_retrieved()]
        except KeyError:
            self.logger.error("No retrieved folder found")

        model_file = out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME)
        model_node = DataFactory('singlefile')()
        model_node.add_path(model_file)
        new_nodes_list = [('tb_model', model_node)]

        return True, new_nodes_list
