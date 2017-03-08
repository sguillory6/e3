import xmlrpclib
from org.slf4j import LoggerFactory


logger = LoggerFactory.getLogger("atlassian")


def create_new_user(base_url, user_name, group_name):
    confluence_xmlrpc = xmlrpclib.ServerProxy(base_url + "/rpc/xmlrpc")
    confluence_xmlrpc = confluence_xmlrpc.confluence2
    rpc_token = confluence_xmlrpc.login("admin", "admin")
    logger.info("XmlRpc login token: %s" % rpc_token)
    if confluence_xmlrpc.hasUser(rpc_token, user_name):
        return

    confluence_xmlrpc.addUser(
        rpc_token,
        {
            "email": "%s@atlassian.net" % user_name,
            "fullname": user_name,
            "name": user_name,
            "url": "/admin/users/viewuser.action?username=%s" % user_name
        },
        user_name)
    confluence_xmlrpc.addPersonalSpace(rpc_token, {"name": user_name, "key": "~%s" % user_name}, user_name)
    confluence_xmlrpc.addPermissionToSpace(rpc_token, "VIEWSPACE", "confluence-users", "~%s" % user_name)
    if not confluence_xmlrpc.hasGroup(rpc_token, group_name):
        confluence_xmlrpc.addGroup(rpc_token, group_name)

    confluence_xmlrpc.addUserToGroup(rpc_token, user_name, group_name)
