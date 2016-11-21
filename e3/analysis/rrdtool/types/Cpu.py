import os
from analysis.rrdtool.types.Graph import Graph


class Cpu(Graph):
    _graph_config = {
        'file': '%s-cpu-usage-%s.png',
        'title': 'CPU usage on %s',
        'label': 'CPU %',
        'stack': True,
        'config': [
            {
                'cpu-idle': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Idle',
                        'line': '#b2ffcf',
                        'area': '#aaefa7'
                    }
                ]
            },
            {
                'cpu-nice': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Nice',
                        'line': '#3d9eaf',
                        'area': '#baf4ff'
                    }
                ]
            },
            {
                'cpu-user': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'User',
                        'line': '#c4aa27',
                        'area': '#ffee9b'
                    }
                ]
            },
            {
                'cpu-wait': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'IO-Wait',
                        'line': '#bc3636',
                        'area': '#ffa0a0'
                    }
                ]
            },
            {
                'cpu-system': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'System',
                        'line': '#1f25e0',
                        'area': '#abadf4'
                    }
                ]
            },
            {
                'cpu-softirq': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'SoftIRQ',
                        'line': '#3d9ece',
                        'area': '#abe1fc'
                    }
                ]
            },
            {
                'cpu-interrupt': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'IRQ',
                        'line': '#2c66b2',
                        'area': '#7a98bf'
                    }
                ]
            },
            {
                'cpu-steal': [
                    {
                        'ds': 'value',
                        'multi': 1,
                        'desc': 'Steal',
                        'line': '#000000',
                        'area': '#6c6e70'
                    }
                ]
            }
        ]
    }

    _max_cpus = 8
    _image_dir = None
    _server_dir = None

    def __init__(self, image_dir, server_dir):
        self._image_dir = image_dir
        self._server_dir = server_dir

    def render(self, node_name, start, end, graph_width=350, graph_height=100):
        # Uncomment this to get per CPU graphs
        # for cpu_no in range(0, self._get_num_cpus()):
        #     cpu_name = 'cpu-%d' % cpu_no
        #     data_dir = os.path.join(self._server_dir, cpu_name)
        #     image_file = os.path.join(self._image_dir, self._graph_config['file'] % (node_name, cpu_name))
        #     self._render(data_dir, image_file, start, end, self._graph_config, graph_width, graph_height, node_name,
        #                  '%s on %s' % (cpu_name, node_name))

        data_dir = os.path.join(self._server_dir, 'aggregation-cpu-average')
        image_file = os.path.join(self._image_dir, '%s-cpu-all-average.png' % node_name)
        self._render(data_dir, image_file, start, end, self._graph_config, graph_width, graph_height,
                     node_name, 'cpu-all-average')

        data_dir = os.path.join(self._server_dir, 'aggregation-cpu-sum')
        image_file = os.path.join(self._image_dir, '%s-cpu-all-sum.png' % node_name)
        self._render(data_dir, image_file, start, end, self._graph_config, graph_width, graph_height,
                     node_name, 'cpu-all-sum')

    def _get_num_cpus(self):
        cpu_count = 0
        for cpu_no in range(0, self._max_cpus, 1):
            cpu_dir = os.path.join(self._server_dir, 'cpu-%i' % cpu_no)
            if os.path.isdir(cpu_dir):
                cpu_count += 1
            if not os.path.isdir(cpu_dir):
                break
        return cpu_count
