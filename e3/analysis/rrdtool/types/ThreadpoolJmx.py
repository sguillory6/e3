import os
from analysis.rrdtool.types.Graph import Graph


class ThreadpoolJmx(Graph):
    _graph_config = {
        'file': '%s-thread-pool-%s.png',
        'title': 'Thread pool on %s',
        'label': 'Count',
        'stack': False,
        'config': [
            {
                'gauge-PoolSize': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Total threads',
                        'line': '#ffac30',
                        'area': None
                    }
                ],
                'gauge-ActiveCount': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Active threads',
                        'line': '#503ce8',
                        'area': '#c4bcff'
                    }
                ]
            }
        ]
    }

    _pool_dirs = [
        'GenericJMX-com.atlassian.bitbucket.thread-pools_EventThreadPool',
        'GenericJMX-com.atlassian.bitbucket.thread-pools_IoPumpThreadPool',
        'GenericJMX-com.atlassian.bitbucket.thread-pools_ScheduledThreadPool'
    ]

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        for pool_dir in self._pool_dirs:
            pool_name = pool_dir.split('_')[1]
            image_file = os.path.join(self._image_dir, self._graph_config['file'] % (node_name, pool_name.lower()))
            data_dir = os.path.join(self._server_dir, pool_dir)
            self._render(data_dir, image_file, start, end, self._graph_config,
                         graph_width, graph_height, node_name, "%s (%s)" % (node_name, pool_name))
