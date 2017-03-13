import xmlrpclib

def read_file_as_bytes(filename):
    file = open(filename, "rb")
    handle = file.read()
    file.close()

    return handle

def authenticate_rpc(base_url):
    confluence_xmlrpc = xmlrpclib.ServerProxy(base_url + "/rpc/xmlrpc")
    confluence_xmlrpc = confluence_xmlrpc.confluence2

    rpc_token = confluence_xmlrpc.login("admin", "admin")
    print "XmlRpc login token: %s" % rpc_token

    return confluence_xmlrpc, rpc_token

def import_space(confluence_xmlrpc, token, filename):
    space_file = read_file_as_bytes(filename)
    return confluence_xmlrpc.importSpace(token, xmlrpclib.Binary(space_file))

def has_space(confluence_rpc, token, space_key):
    return confluence_rpc.getSpace(token, space_key) is not None
