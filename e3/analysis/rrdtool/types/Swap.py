import os
from analysis.rrdtool.types.Graph import Graph


class Swap(Graph):
    _graph_config = {
        'file': '%s-swap.png',
        'title': 'Swap space IO on %s',
        'label': 'Bytes per second',
        'stack': False,
        'config': [
            {
                'swap_io-in': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'IO input',
                        'line': '#4286f4',
                        'area': '#afceff'
                    }
                ],
                'swap_io-out': [
                    {
                        'ds': 'value',
                        'multi': -1,
                        'desc': 'IO output',
                        'line': '#1f8e31',
                        'area': '#a6ddaf'
                    }
                ]
            }
        ]
    }

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        data_dir = os.path.join(self._server_dir, 'swap')
        image_file = os.path.join(self._image_dir, self._graph_config['file'] % node_name)
        self._render(data_dir, image_file, start, end, self._graph_config,
                     graph_width, graph_height, node_name, 'swap')
