import os
from analysis.rrdtool.types.Graph import Graph


class Interface(Graph):
    _graph_config = {
        'file': '%s-interface-%s.png',
        'title': 'Network usage on %s',
        'label': 'Bytes per second',
        'stack': False,
        'config': [
            {
                'if_octets': [
                    {
                        'ds': 'rx',
                        'multi': 1,
                        'desc': 'Bytes received (+)',
                        'line': '#ce2a1e',
                        'area': '#ffb5af'
                    },
                    {
                        'ds': 'tx',
                        'multi': -1,
                        'desc': 'Bytes transmitted (-)',
                        'line': '#11ad38',
                        'area': '#bfffcf'
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
        for interface in ['eth0']:
            image_file = os.path.join(self._image_dir, self._graph_config['file'] % (node_name, interface))
            data_dir = os.path.join(self._server_dir, 'interface-%s' % interface)
            self._render(data_dir, image_file, start, end, self._graph_config,
                         graph_width, graph_height, node_name,
                         '%s (%s)' % (node_name, interface))
