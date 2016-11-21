import json
import os
import re
import requests
import time

from provisioning.BitbucketDataCenter import BitbucketDataCenter

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class BitbucketDataCenterLDAP(BitbucketDataCenter):
    """ Extends BitbucketDataCenter to use BitbucketDataCenterLDAP.template and configures LDAP after provisioning. """

    def __init__(self, aws, e3_properties):
        self.e3_properties = e3_properties
        BitbucketDataCenter.__init__(self, aws, e3_properties, template="BitbucketDataCenterLDAP")

    def after_provision(self):
        BitbucketDataCenter.after_provision(self)
        # ldap_host is hard-coded into `BitbucketDataCenterLDAP.template` as an entry in the `/etc/hosts` file
        ldap_host = "ldap.server"
        ldap_config_name = "ldap_config"
        # This group is hard-coded in the LDAP directory configuration of the Docker image
        group_name = "a-large-group"
        group_permission = "ADMIN"

        # Only attempt LDAP config when not using snapshot
        if not self.e3_properties['snapshot']:
            self.configure_ldap(ldap_host, ldap_config_name)
            self.wait_for_ldap_sync()
            self.add_ldap_group(group_name, group_permission)
            self.configure_group_members_key(group_name, 1000)

    def configure_ldap(self, ldap_host, ldap_config_name):
        self._log.info("Attempting to configure LDAP server '%s'" % ldap_host)
        data = {
            'ldapConnectionTimeoutInSec': '10',
            'ldapUserLastname': 'sn',
            'ldapUserUsername': 'cn',
            'ldapPermissionOption': 'READ_ONLY',
            'newForm': 'false',
            'ldapReadTimeoutInSec': '120',
            'ldapUserUsernameRdn': 'cn',
            'ldapUserdn': 'cn=admin,dc=openstack,dc=org',
            'directoryId': '0',
            'ldapUserFilter': '(objectclass=inetorgperson)',
            'crowdSyncIncrementalEnabled': 'true',
            'ldapGroupDescription': 'description',
            'port': '389',
            'ldapUserEncryption': 'sha',
            '_ldapFilterExpiredUsers': 'visible',
            'ldapAutoAddGroups': 'stash-users',
            'ldapSearchTimelimitInSec': '60',
            '_ldapUsermembershipUse': 'visible',
            'ldapUserDisplayname': 'displayName',
            'hostname': ldap_host,
            'ldapGroupName': 'cn',
            '_ldapReferral': 'visible',
            '_ldapRelaxedDnStandardisation': 'visible',
            '_ldapPagedresults': 'visible',
            'ldapUserFirstname': 'givenName',
            'ldapGroupObjectclass': 'groupOfUniqueNames',
            'ldapGroupFilter': '(objectclass=groupOfUniqueNames)',
            'ldapUserEmail': 'mail',
            'type': 'com.atlassian.crowd.directory.OpenLDAP',
            '_localUserStatusEnabled': 'visible',
            'ldapUserObjectclass': 'inetorgperson',
            '_nestedGroupsEnabled': 'visible',
            'ldapUserGroup': 'memberOf',
            'ldapRelaxedDnStandardisation': 'true',
            'ldapGroupUsernames': 'uniqueMember',
            'ldapUserPassword': 'ldapUserPassword',
            '_useSSL': '_useSSL',
            'save': 'Save+and+Test',
            'ldapBasedn': 'dc=openstack,dc=org',
            'name': ldap_config_name,
            'ldapCacheSynchroniseIntervalInMin': '60',
            '_ldapUsermembershipUseForGroups': 'visible',
            'ldapExternalId': 'entryUUID',
            '_ldapSecure': 'visible',
            'ldapPassword': 'password',
            '_crowdSyncIncrementalEnabled': 'visible'
        }
        try:
            self.post_with_security_info("/plugins/servlet/embedded-crowd/configure/ldap/", data)
        except Exception as e:
            self._log.error("LDAP Config error [%s]" % e)

    def add_ldap_group(self, group, level):
        self._log.info("Adding group '%s' with permission level '%s'" % (group, level))
        url = self.get_stack_output(self._stack_config["StackName"], 'URL') + "/rest/api/1.0/admin/permissions/groups"
        requests.put(url, params={'permission': level, 'name': group}, auth=('admin', self._admin_password))

    def wait_for_ldap_sync(self):
        self._log.info("Waiting for LDAP to synchronise")
        # Wait for sync to start
        time.sleep(15)
        url = self.get_stack_output(self._stack_config["StackName"], 'URL') + "/rest/crowd/1/directory"
        response = requests.get(url, auth=('admin', self._admin_password))
        status = re.search(".*<syncStatus>(.*?)</syncStatus>", response.text).group(1)

        while status != "Full synchronisation completed successfully.":
            self._log.debug("LDAP sync status: %s" % status)
            time.sleep(60)
            response = requests.get(url, auth=('admin', self._admin_password))
            status = re.search(".*<syncStatus>(.*?)</syncStatus>", response.text).group(1)

        self._log.info("LDAP synchronisation completed successfully")

    def configure_group_members_key(self, group, num_keys):
        url = self.get_stack_output(self._stack_config["StackName"], 'URL')

        # Get users in group
        group_url = url + "/rest/api/1.0/admin/groups/more-members"
        response = requests.get(group_url,
                                params={"context": group, "limit": num_keys},
                                auth=('admin', self._admin_password))
        users = json.loads(response.content)['values']

        # Load keys
        key_file_path = os.path.join(root, 'e3-home', 'keys', '%s-keys.json' % num_keys)
        with open(key_file_path, 'r') as key_file:
            key_pairs = json.load(key_file)

        # Loop through users, adding an SSH key to each
        for i in range(0, len(users) - 1):
            username = users[i]['name']
            public_key = key_pairs['key_pairs'][i]['public_key']

            add_key_url = url + "/rest/ssh/1.0/keys"
            data = json.dumps({'text': public_key})
            params = {"user": username}
            r = requests.post(add_key_url, auth=("admin", self._admin_password), params=params, data=data,
                              headers={"Content-Type": "application/json"})
            if r.status_code > 300:
                self._log.debug("Failed to add SSH key to user '%s' %s" % username)
