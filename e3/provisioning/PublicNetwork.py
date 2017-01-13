from provisioning.Template import Template
import copy


class PublicNetwork(Template):
    def __init__(self, aws, e3_properties):
        stack_config = {
            "StackName": "",
            "Template": "PublicNetwork",
            "CloudFormation": {},
            "Orchestration": {
                "StackNamePrefix": "network"
            },
            "Output": {}
        }
        # We do not want to pass any parameters here
        e3_properties_without_parameters = copy.deepcopy(e3_properties)
        e3_properties_without_parameters.update({'parameters': ""})
        Template.__init__(self, aws, e3_properties_without_parameters, stack_config)
