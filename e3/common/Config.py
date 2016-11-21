def run_config(node):
    if '@' in node:
        hostname = node.split('@')[1]
    else:
        hostname = node
    if hostname == 'localhost':
        data_dir = "/tmp"
    else:
        data_dir = "/media/data"

    return {
        "data_dir": data_dir,
        "tmp_dir": "%s/tmp" % data_dir,
        "work_dir": '%s/work/' % data_dir,
        "worker_e3_dir": "%s/e3" % data_dir,
        "worker_run_dir": "%s/runs" % data_dir
    }
