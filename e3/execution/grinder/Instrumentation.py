from inspect import getmembers, isfunction, getmodule

from Tools import register
from common.helper import Authentication
from common.helper import Branches
from common.helper import Diff
from common.helper import Inbox
from common.helper import Projects
from common.helper import PullRequests
from common.helper import Repositories

# methods that must be excluded from instrumentation
FUNC_BLACKLIST = ["get_branch_by_id"]


def get_functions(module):
    return [o for o in getmembers(module)
            if o[0] not in FUNC_BLACKLIST and isfunction(o[1]) and getmodule(o[1]) == module]


def instrument():
    mapping = register_all_in_module(1000, get_functions(Authentication)) + \
              register_all_in_module(2000, get_functions(Branches)) + \
              register_all_in_module(3000, get_functions(Diff)) + \
              register_all_in_module(4000, get_functions(Inbox)) + \
              register_all_in_module(5000, get_functions(Projects)) + \
              register_all_in_module(6000, get_functions(PullRequests)) + \
              register_all_in_module(7000, get_functions(Repositories))
    return mapping


def register_all_in_module(base_no, function_pairs):
    mapping = []
    no = base_no
    for name, value in function_pairs:
        register(no, name, value)
        mapping.append({"number": str(no), "name": name})
        no += 1
    return mapping
