import os
from analysis.rrdtool.types.Graph import Graph


class GenericJmx(Graph):
    _graph_config = [
        {
            'file': '%s-jvm-cpu-usage.png',
            'title': 'JVM CPU usage on %s',
            'label': 'CPU time (ms)',
            'stack': False,
            'config': [
                {
                    'counter-os-process_cpu_time': [
                        {
                            'ds': 'value',
                            # javadoc: Returns the CPU time used by the process on which the
                            # Java virtual machine is running in nanoseconds
                            'multi': 0.001,
                            'desc': 'CPU average',
                            'line': '#e09226',
                            'area': '#e5caa5'
                        }
                    ]
                }
            ],
            'subdir': 'GenericJMX',
            'graph_name': 'jvm-cpu'
        },
        {
            'file': '%s-jvm-file-handles.png',
            'title': "JVM file handles on %s",
            'label': 'Count',
            'stack': False,
            'config': [
                {
                    'gauge-os-max_fd_count': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Max handles',
                            'line': '#d3ca26',
                            'area': '#feffef'
                        }
                    ]
                },
                {
                    'gauge-os-open_fd_count': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Open handles',
                            'line': '#3581dd',
                            'area': '#b7d7ff'
                        }
                    ]
                }
            ],
            'subdir': 'GenericJMX',
            'graph_name': 'jvm-file-descriptors'
        },
        {
            'file': '%s-java-loaded-classes.png',
            'title': "Java loaded classes on %s",
            'label': 'Class count',
            'stack': False,
            'config': [
                {
                    'gauge-loaded_classes': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Loaded classes',
                            'line': '#d3ca26',
                            'area': '#feffef'
                        }
                    ]
                }
            ],
            'subdir': 'GenericJMX-java',
            'graph_name': 'jvm-load-classes'
        },
        {
            'file': '%s-java-compilation-time.png',
            'title': "Java compilation time on %s",
            'label': 'Time (ms)',
            'stack': False,
            'config': [
                {
                    'total_time_in_ms-compilation_time': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Average compilation time',
                            'line': '#d3ca26',
                            'area': '#feffef'
                        }
                    ]
                }
            ],
            'subdir': 'GenericJMX-java',
            'graph_name': 'jvm-compilation-time'
        },
        {
            'file': '%s-java-memory-heap.png',
            'title': "Java heap memory on %s",
            'label': 'Memory usage',
            'stack': False,
            'config': [
                {
                    'memory-heap-init': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Initial heap',
                            'line': '#38c3ff',
                            'area': None
                        }
                    ]
                },
                {
                    'memory-heap-used': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Used heap',
                            'line': '#28af5a',
                            'area': '#ddffea'
                        }
                    ]
                },
                {
                    'memory-heap-committed': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Committed heap',
                            'line': '#fff787',
                            'area': None
                        }
                    ]
                },
                {
                    'memory-heap-max': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Max heap',
                            'line': '#ed4b15',
                            'area': None
                        }
                    ]
                }
            ],
            'subdir': 'GenericJMX-java_memory',
            'graph_name': 'jvm-heap'
        },
        {
            'file': '%s-java-memory-non-heap.png',
            'title': "Java non-heap memory on %s",
            'label': 'Memory usage',
            'stack': False,
            'config': [
                {
                    'memory-nonheap-init': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Initial heap',
                            'line': '#38c3ff',
                            'area': None
                        }
                    ]
                },
                {
                    'memory-nonheap-used': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Used heap',
                            'line': '#28af5a',
                            'area': '#ddffea'
                        }
                    ]
                },
                {
                    'memory-nonheap-committed': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Committed heap',
                            'line': '#fff787',
                            'area': None
                        }
                    ]
                },
                {
                    'memory-nonheap-max': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Max heap',
                            'line': '#ed4b15',
                            'area': None
                        }
                    ]
                }
            ],
            'subdir': 'GenericJMX-java_memory',
            'graph_name': 'jvm-nonheap'
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
            data_dir = os.path.join(self._server_dir, graph_config['subdir'])
            graph_name=graph_config['graph_name']
            self._render(data_dir, image_file, start, end, graph_config,
                         graph_width, graph_height, node_name, graph_name)
