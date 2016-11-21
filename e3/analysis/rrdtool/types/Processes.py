import os
from analysis.rrdtool.types.Graph import Graph


class Processes(Graph):
    _graph_config = [
        {
            'file': '%s-processes-resident-%s.png',
            'title': 'Process resident size on %s',
            'label': 'Process memory',
            'stack': False,
            'config': [
                {
                    'ps_rss': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Resident size',
                            'line': '#3581dd',
                            'area': '#b7d7ff'
                        }
                    ]
                }
            ]
        },
        {
            'file': '%s-processes-count-%s.png',
            'title': 'Process count on %s',
            'label': 'Count',
            'stack': False,
            'config': [
                {
                    'ps_count': [
                        {
                            'ds': 'processes',
                            'multi': 1,
                            'desc': 'Processes (+)',
                            'line': '#e09226',
                            'area': '#e5caa5'
                        },
                        {
                            'ds': 'threads',
                            'multi': -1,
                            'desc': 'Threads (-)',
                            'line': '#3581dd',
                            'area': '#b7d7ff'
                        }
                    ]

                }
            ]
        },
        {
            'file': '%s-processes-cputime-%s.png',
            'title': 'Process CPU on %s',
            'label': 'CPU jiffies',
            'stack': True,
            'config': [
                {
                    'ps_cputime': [
                        {
                            'ds': 'user',
                            'multi': 1,
                            'desc': 'User',
                            'line': '#3581dd',
                            'area': '#b7d7ff'
                        },
                        {
                            'ds': 'syst',
                            'multi': 1,
                            'desc': 'System',
                            'line': '#e09226',
                            'area': '#e5caa5'
                        }
                    ]
                }
            ]
        },
        {
            'file': '%s-processes-disk-io-%s.png',
            'title': 'Process Disk IO on %s',
            'label': 'Bytes per second',
            'stack': False,
            'config': [
                {
                    'ps_disk_octets': [
                        {
                            'ds': 'read',
                            'multi': 1,
                            'desc': 'Read',
                            'line': '#4286f4',
                            'area': '#afceff'
                        },
                        {
                            'ds': 'write',
                            'multi': -1,
                            'desc': 'Written',
                            'line': '#1f8e31',
                            'area': '#a6ddaf'
                        }
                    ]
                }
            ]
        }
    ]

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        process_name = 'git'
        for graph in self._graph_config:
            data_dir = os.path.join(self._server_dir, 'processes-%s' % process_name)
            image_file = os.path.join(self._image_dir, graph['file'] % (node_name, process_name))
            self._render(data_dir, image_file, start, end, graph, graph_width, graph_height,
                         node_name, '%s (%s)' % (node_name, process_name))
