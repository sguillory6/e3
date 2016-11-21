import os
from analysis.rrdtool.types.Graph import Graph


class Memory(Graph):
    _graph_config = {
        'file': '%s-memory.png',
        'title': 'Memory usage on %s',
        'label': 'Bytes',
        'stack': True,
        'config': [
            {
                'memory-free': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Free',
                        'line': '#109617',
                        'area': '#e0ffe1'
                    }
                ]
            },
            {
                'memory-cached': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Cached',
                        'line': '#0000ff',
                        'area': '#A3A3FF'
                    }
                ]
            },
            {
                'memory-buffered': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Buffered',
                        'line': '#ffb000',
                        'area': '#FCDF9D'
                    }
                ]
            },
            {
                'memory-used': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Used',
                        'line': '#ff0000',
                        'area': '#FFA6A6'
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
        data_dir = os.path.join(self._server_dir, 'memory')
        image_file = os.path.join(self._image_dir, self._graph_config['file'] % node_name)
        self._render(data_dir, image_file, start, end, self._graph_config,
                     graph_width, graph_height, node_name, 'memory')
