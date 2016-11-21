import os
from analysis.rrdtool.types.Graph import Graph


class TomcatJmx(Graph):
    _graph_config = [
        {
            'file': '%s-tomcat-processing-time.png',
            'title': 'Total processing time on %s',
            'label': 'CPU time (ms)',
            'stack': False,
            'config': [
                {
                    'total_time_in_ms-global-processing': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Average CPU time',
                            'line': '#0000ff',
                            'area': '#A3A3FF'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-catalina_request_processor-"http-nio-7990"',
            'graph_name': 'tomcat-processing-time'
        },
        {
            'file': '%s-tomcat-total-requests.png',
            'title': "Tomcat HTTP requests on %s",
            'label': 'Requests per second',
            'stack': False,
            'config': [
                {
                    'total_requests-global': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Average requests',
                            'line': '#0000ff',
                            'area': '#A3A3FF'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-catalina_request_processor-"http-nio-7990"',
            'graph_name': 'tomcat-requests'
        },
        {
            'file': '%s-tomcat-io-global.png',
            'title': 'Tomcat IO on %s',
            'label': 'Bytes per second',
            'stack': False,
            'config': [
                {
                    'io_octets-global': [
                        {
                            'ds': 'rx',
                            'multi': 1,
                            'desc': 'Bytes received (+)',
                            'line': '#4286f4',
                            'area': '#afceff'
                        },
                        {
                            'ds': 'tx',
                            'multi': -1,
                            'desc': 'Bytes transmitted (-)',
                            'line': '#1f8e31',
                            'area': '#a6ddaf'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-catalina_request_processor-"http-nio-7990"',
            'graph_name': 'tomcat-io'
        },
        {
            'file': '%s-tomcat-request-threads.png',
            'title': 'Tomcat request threads on %s',
            'label': 'Threads',
            'stack': False,
            'config': [
                {
                    'threads-total': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Total threads',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        },
                    ]
                },
                {
                    'threads-running': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Running threads',
                            'line': '#5f2ad3',
                            'area': '#bfa4f9'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-request_processor-"http-nio-7990"',
            'graph_name': 'tomcat-threads'
        }
    ]

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        for graph_config in self._graph_config:
            image_file = os.path.join(self._image_dir, graph_config['file'] % node_name)
            data_dir = os.path.join(self._server_dir, graph_config['data_subdir'])
            graph_name=graph_config['graph_name']
            self._render(data_dir, image_file, start, end, graph_config,
                         graph_width, graph_height, node_name, graph_name)
