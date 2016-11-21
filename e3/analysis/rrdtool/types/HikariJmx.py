import os
from analysis.rrdtool.types.Graph import Graph


class HikariJmx(Graph):
    _graph_config = {
        'file': '%s-hikari.png',
        'title': 'Hikari Connection Pooling on %s',
        'label': 'Connections',
        'stack': False,
        'config': [
            {
                'gauge-TotalConnections': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Total',
                        'line': '#18ad31',
                        'area': '#bcffc7'
                    }
                ]
            },
            {
                'gauge-ActiveConnections': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Active',
                        'line': '#5f2ad3',
                        'area': '#bfa4f9'
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
        data_dir = os.path.join(self._server_dir, 'GenericJMX-com.zaxxer.hikari_Poolbitbucket')
        self._render(data_dir, image_file, start, end, self._graph_config,
                     graph_width, graph_height, node_name, 'hikari-connections')
