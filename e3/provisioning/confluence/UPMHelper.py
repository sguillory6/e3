import requests
from requests.auth import HTTPBasicAuth


def disable_plugin(base_url, plugin_key):
    print "--------------------Disable Onboarding %s---------------------------" % plugin_key
    plugin_key = 'com.atlassian.confluence.plugins.confluence-onboarding'
    response_obj = requests.put(
        base_url + "rest/plugins/1.0/%s-key" % plugin_key,
        auth=HTTPBasicAuth('admin', 'admin'),
        json={'enabled': 'false'},
        headers={'content-type': 'application/vnd.atl.plugins.plugin+json'})
    print "disable %s status %s" % (plugin_key, response_obj.text)
    return response_obj.status_code