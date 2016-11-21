import os
from analysis.rrdtool.types.Graph import Graph


class BitbucketJmx(Graph):
    _graph_config = [
        {
            'file': '%s-bitbucket-command-tickets.png',
            'title': 'Command tickets on %s',
            'label': 'Ticket count',
            'stack': True,
            'config': [
                {
                    'gauge-QueuedRequests': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Queued requests',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                },
                {
                    'gauge-Available': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Available tickets',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        }
                    ]
                },
                {
                    'gauge-Used': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Used tickets',
                            'line': '#5f2ad3',
                            'area': '#bfa4f9'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-com.atlassian.bitbucket_CommandTickets',
            'graph_name': 'command-tickets'
        },
        {
            'file': '%s-bitbucket-hosting-tickets.png',
            'title': "Hosting tickets on %s",
            'label': 'Ticket count',
            'stack': True,
            'config': [
                {
                    'gauge-QueuedRequests': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Queued requests',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                },
                {
                    'gauge-Available': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Available tickets',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        }
                    ]
                },
                {
                    'gauge-Used': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Used tickets',
                            'line': '#5f2ad3',
                            'area': '#bfa4f9'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-com.atlassian.bitbucket_HostingTickets',
            'graph_name': 'hosting-tickets'
        },
        {
            'file': '%s-bitbucket-projects.png',
            'title': "Projects on %s",
            'label': 'Project count',
            'stack': False,
            'config': [
                {
                    'gauge-Count': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Projects',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-com.atlassian.bitbucket_Projects',
            'graph_name': 'project-count'
        },
        {
            'file': '%s-bitbucket-repositories.png',
            'title': "Repositories on %s",
            'label': 'Repository count',
            'stack': False,
            'config': [
                {
                    'gauge-Count': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Repositories',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-com.atlassian.bitbucket_Repositories',
            'graph_name': 'repository-count'
        },
        {
            'file': '%s-bitbucket-scm-stats.png',
            'title': "SCM Statistics for %s",
            'label': 'Total',
            'stack': True,
            'config': [
                {
                    'gauge-Pushes': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Pushes',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        }
                    ]
                },
                {
                    'gauge-Pulls': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Pulls',
                            'line': '#5f2ad3',
                            'area': '#bfa4f9'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-com.atlassian.bitbucket_ScmStatistics',
            'graph_name': 'scm-statistics'
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
            graph_name = graph_config['graph_name']
            self._render(data_dir, image_file, start, end, graph_config,
                         graph_width, graph_height, node_name, graph_name)
