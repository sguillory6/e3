import os
from analysis.rrdtool.types.Graph import Graph


class HazelcastEventServiceJmx(Graph):
    _graph_config = {
        'file': '%s-hazelcast-events.png',
        'title': 'Hazelcast Events on %s',
        'label': 'Operations',
        'stack': False,
        'config': [
            {
                'gauge-eventThreadCount': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Threads',
                        'line': '#9b7a0d',
                        'area': '#dbcb9760'
                    }
                ]
            }
        ]
    }

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        Graph.__init__(self)
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        image_file = os.path.join(self._image_dir, self._graph_config['file'] % node_name)
        data_dir = os.path.join(self._server_dir,
                                'GenericJMX-com.hazelcast_HazelcastInstance.EventService.hazelcast.hazelcas')
        self._render(data_dir, image_file, start, end, self._graph_config,
                     graph_width, graph_height, node_name, 'hazelcast-operations')
