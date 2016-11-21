import os
from analysis.rrdtool.types.Graph import Graph


class HibernateJmx(Graph):
    _graph_config = [
        {
            'file': '%s-hibernate-collections.png',
            'title': 'Hibernate collections on %s',
            'label': 'Collection operations',
            'stack': True,
            'config': [
                {
                    'gauge-CollectionFetchCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Fetch',
                            'line': '#5b32ff',
                            'area': '#c5b7ff'
                        }
                    ]
                },
                {
                    'gauge-CollectionUpdateCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Update',
                            'line': '#ac1cbc',
                            'area': '#f59eff'
                        }
                    ]
                },

                {
                    'gauge-CollectionLoadCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Load',
                            'line': '#18a54e',
                            'area': '#8bd6a7'
                        }
                    ]
                },
                {
                    'gauge-CollectionRecreateCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Recreate',
                            'line': '#bc8d1e',
                            'area': '#ddc17e'
                        }
                    ]
                },
                {
                    'gauge-CollectionRemoveCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Remove',
                            'line': '#a33b1b',
                            'area': '#f7a991'
                        }
                    ]
                }
            ],
            'graph_name': 'hibernate-collections'
        },
        {
            'file': '%s-hibernate-entities.png',
            'title': 'Hibernate entities on %s',
            'label': 'Entity operations',
            'stack': True,
            'config': [
                {
                    'gauge-EntityFetchCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Fetch',
                            'line': '#5b32ff',
                            'area': '#c5b7ff'
                        }
                    ]
                },
                {
                    'gauge-EntityUpdateCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Update',
                            'line': '#ac1cbc',
                            'area': '#f59eff'
                        }
                    ]
                },

                {
                    'gauge-EntityLoadCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Load',
                            'line': '#18a54e',
                            'area': '#8bd6a7'
                        }
                    ]
                },
                {
                    'gauge-EntityInsertCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Insert',
                            'line': '#bc8d1e',
                            'area': '#ddc17e'
                        }
                    ]
                },
                {
                    'gauge-EntityDeleteCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Delete',
                            'line': '#a33b1b',
                            'area': '#f7a991'
                        }
                    ]
                }
            ],
            'graph_name': 'hibernate-entities'
        },
        {
            'file': '%s-hibernate-query-cache.png',
            'title': 'Hibernate query cache on %s',
            'label': 'Cache operations',
            'stack': True,
            'config': [
                {
                    'gauge-QueryCachePutCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Put',
                            'line': '#5b32ff',
                            'area': '#c5b7ff'
                        }
                    ]
                },
                {
                    'gauge-QueryExecutionCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Execution',
                            'line': '#ac1cbc',
                            'area': '#f59eff'
                        }
                    ]
                },
                {
                    'gauge-QueryCacheMissCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Miss',
                            'line': '#bc8d1e',
                            'area': '#ddc17e'
                        }
                    ]
                },
                {
                    'gauge-QueryCacheHitCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Hit',
                            'line': '#18a54e',
                            'area': '#8bd6a7'
                        }
                    ]
                }
            ],
            'graph_name': 'hibernate-query-cache'
        },
        {
            'file': '%s-hibernate-L2-cache.png',
            'title': 'Hibernate L2 cache on %s',
            'label': 'Cache operations',
            'stack': True,
            'config': [
                {
                    'gauge-SecondLevelCachePutCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'L2 Put',
                            'line': '#5b32ff',
                            'area': '#c5b7ff'
                        }
                    ]
                },
                {
                    'gauge-SecondLevelCacheMissCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'L2 Miss',
                            'line': '#bc8d1e',
                            'area': '#ddc17e'
                        }
                    ]
                },
                {
                    'gauge-SecondLevelCacheHitCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'L2 Hit',
                            'line': '#18a54e',
                            'area': '#8bd6a7'
                        }
                    ]
                }
            ],
            'graph_name': 'hibernate-l2'
        },
        {
            'file': '%s-hibernate-update-timestamps.png',
            'title': 'Hibernate update timestamps on %s',
            'label': 'Update operations',
            'stack': True,
            'config': [
                {
                    'gauge-UpdateTimestampsCachePutCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Put',
                            'line': '#5b32ff',
                            'area': '#c5b7ff'
                        }
                    ]
                },
                {
                    'gauge-UpdateTimestampsCacheMissCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Miss',
                            'line': '#bc8d1e',
                            'area': '#ddc17e'
                        }
                    ]
                },
                {
                    'gauge-UpdateTimestampsCacheHitCount': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Hit',
                            'line': '#18a54e',
                            'area': '#8bd6a7'
                        }
                    ]
                }
            ],
            'graph_name': 'hibernate-timestamps'
        }
    ]

    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        data_dir = os.path.join(self._server_dir, 'GenericJMX-org.hibernate.core_')
        for graph_config in self._graph_config:
            image_file = os.path.join(self._image_dir, graph_config['file'] % node_name)
            graph_name=graph_config['graph_name']
            self._render(data_dir, image_file, start, end, graph_config,
                         graph_width, graph_height, node_name, graph_name)
