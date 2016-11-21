import os
from analysis.rrdtool.types.Graph import Graph


class Disk(Graph):
    _graph_config = {
        'file': '%s-disk-%s.png',
        'title': 'Disk usage on %s',
        'label': 'Bytes per second',
        'stack': False,
        'config': [
            {
                'disk_octets': [
                    {
                        'ds': 'read',
                        'multi': 1,
                        'desc': 'Bytes read (+)',
                        'line': '#4286f4',
                        'area': '#afceff'
                    },
                    {
                        'ds': 'write',
                        'multi': -1,
                        'desc': 'Bytes written (-)',
                        'line': '#1f8e31',
                        'area': '#a6ddaf'
                    }
                ]
            }
        ]
    }

    _image_dir = None
    _server_dir = None

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        for disk in ['xvda', 'xvdb', 'xvdf']:
            image_file = os.path.join(self._image_dir, self._graph_config['file'] % (node_name, disk))
            data_dir = os.path.join(self._server_dir, 'disk-%s' % disk)
            self._render(data_dir, image_file, start, end, self._graph_config,
                         graph_width, graph_height, node_name, '%s (%s)' % (node_name, disk))
