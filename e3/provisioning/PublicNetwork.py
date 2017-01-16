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
        Template.__init__(self, aws, e3_properties, stack_config)
