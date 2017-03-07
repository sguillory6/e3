import os
from analysis.rrdtool.types.Graph import Graph


class ConfluenceJmx(Graph):
    _graph_config = [
        {
            'file': '%s-confluence-all-content-usage.png',
            'title': 'All content usage on %s',
            'label': 'Usage',
            'stack': True,
            'config': [
                {
                    'gauge-Confluence.Usage.AllContent': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'All content',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.AllContent',
            'graph_name': 'all-content-usage'
        },
        {
            'file': '%s-confluence-current-content-usage.png',
            'title': "Current content usage on %s",
            'label': 'Usage',
            'stack': True,
            'config': [
                {
                    'gauge-Confluence.Usage.CurrentContent': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Current content',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.CurrentContent',
            'graph_name': 'current-content-usage'
        },
        {
            'file': '%s-confluence-global-spaces-usage.png',
            'title': "Global spaces usage on %s",
            'label': 'Usage',
            'stack': False,
            'config': [
                {
                    'gauge-Confluence.Usage.GlobalSpaces': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Global spaces',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.GlobalSpaces',
            'graph_name': 'global-spaces-usage'
        },
        {
            'file': '%s-confluence-personal-spaces-usage.png',
            'title': "Personal spaces usage on %s",
            'label': 'Usage',
            'stack': False,
            'config': [
                {
                    'gauge-Confluence.Usage.PersonalSpaces': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Personal spaces',
                            'line': '#bc2214',
                            'area': '#ff9f96'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.PersonalSpaces',
            'graph_name': 'personal-spaces-usage'
        },
        {
            'file': '%s-confluence-total-spaces-usage.png',
            'title': "Total spaces usage for %s",
            'label': 'Usage',
            'stack': True,
            'config': [
                {
                    'gauge-Confluence.Usage.TotalSpace': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Total space',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.TotalSpace',
            'graph_name': 'total-space-usage'
        },
        {
            'file': '%s-confluence-local-users-usage.png',
            'title': "Local users usage for %s",
            'label': 'Usage',
            'stack': True,
            'config': [
                {
                    'gauge-Confluence.Usage.LocalUsers': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Local users',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.LocalUsers',
            'graph_name': 'local-users-usage'
        },
        {
            'file': '%s-confluence-local-groups-usage.png',
            'title': "Local groups usage for %s",
            'label': 'Usage',
            'stack': True,
            'config': [
                {
                    'gauge-Confluence.Usage.LocalGroups': [
                        {
                            'ds': 'value',
                            'multi': 1,
                            'desc': 'Local groups',
                            'line': '#18ad31',
                            'area': '#bcffc7'
                        }
                    ]
                }
            ],
            'data_subdir': 'GenericJMX-confluence_Confluence.Usage.LocalGroups',
            'graph_name': 'local-groups-usage'
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
