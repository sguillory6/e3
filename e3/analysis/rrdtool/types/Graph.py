import logging
import os
import rrdtool
import sys
import traceback


class Graph:
    def __init__(self):
        pass

    def _get_definition(self, graph_config, data_dir, stack=False):
        definition_def = []
        definition_cdef = []
        definition_area = []
        definition_lines = []
        data_names = []

        for graph in graph_config:
            for data_file in graph.keys():
                for graph_data in graph[data_file]:
                    data_source = graph_data['ds']
                    multiplier = graph_data['multi']

                    data_description = graph_data['desc']
                    line_color = graph_data['line']
                    area_color = graph_data['area'] if graph_data['area'] else ''

                    data_names.append("%s_%s" % (data_file, data_source))
                    data_description = data_description.ljust(15)

                    data_disk_file = os.path.join(data_dir, data_file + ".rrd").replace(':', '\\:')
                    definition_def.append('DEF:avg_%s_%s_raw=%s:%s:AVERAGE' %
                                          (data_file, data_source, data_disk_file, data_source))

                    definition_cdef.append('CDEF:avg_%s_%s=avg_%s_%s_raw,%0.10f,*' %
                                           (data_file, data_source, data_file, data_source, multiplier))

                    definition_area.append("AREA:area_%s_%s%s" %
                                           (data_file, data_source, area_color))

                    definition_lines.append('LINE1:area_%s_%s%s:%s' %
                                            (data_file, data_source, line_color, data_description))

        definition_stack = []
        data_names.reverse()

        if stack:
            prev_data_name = None
            for name in data_names:
                if prev_data_name:
                    definition_stack.append('CDEF:area_%s=area_%s,avg_%s,ADDNAN' % (name, prev_data_name, name))
                else:
                    definition_stack.append('CDEF:area_%s=avg_%s' % (name, name))
                prev_data_name = name
        else:
            for name in data_names:
                definition_stack.append('CDEF:area_%s=avg_%s' % (name, name))

        graph_definition = definition_def + definition_cdef + definition_stack + definition_area + definition_lines
        # pprint(graph_definition)
        return graph_definition

    def _render(self, data_dir, image_file, start, end, graph, graph_width, graph_height, node_name, graph_name):
        if os.path.exists(image_file):
            os.unlink(image_file)
        if os.path.exists(data_dir):
            title = graph['title'] % node_name
            label = graph['label']
            stack = graph['stack']
            try:
                rrdtool.graphv(image_file,
                               '--imgformat', 'PNG',
                               '--lower-limit', '0',
                               '--width', str(graph_width),
                               '--height', str(graph_height),
                               '--start', start,
                               '--end', end,
                               '--vertical-label', label,
                               '--title', title,
                               self._get_definition(graph['config'], data_dir, stack))
            except rrdtool.OperationalError as ex:
                # Silently skip missing data files
                if "No such file or directory" not in ex.message:
                    traceback.print_exc(file=sys.stderr)
                    logging.error('Failed to generate graph "%s" for node "%s"', graph_name, node_name)
                    logging.error(ex)
