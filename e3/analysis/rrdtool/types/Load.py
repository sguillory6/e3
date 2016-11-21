import os
from analysis.rrdtool.types.Graph import Graph


class Load(Graph):
    _graph_config = {
        'file': '%s-load.png',
        'title': 'System load on %s',
        'label': 'Load',
        'stack': False,
        'config': [
            {
                'load': [
                    {
                        'ds': 'shortterm',
                        'multi': 1,
                        'desc': '1 minute avg',
                        'line': '#00e000',
                        'area': None
                    },
                    {
                        'ds': 'midterm',
                        'multi': 1,
                        'desc': '5 minute avg',
                        'line': '#0000ff',
                        'area': None
                    },
                    {
                        'ds': 'longterm',
                        'multi': 1,
                        'desc': '15 minute avg',
                        'line': '#ff0000',
                        'area': None
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
        image_file = os.path.join(self._image_dir, self._graph_config['file'] % node_name)
        data_dir = os.path.join(self._server_dir, 'load')
        self._render(data_dir, image_file, start, end, self._graph_config,
                     graph_width, graph_height, node_name, 'load')
