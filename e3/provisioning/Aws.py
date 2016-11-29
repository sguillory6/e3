from botocore.session import get_session
from boto3.session import Session

from common.E3 import e3


class Aws:
    cloud_formation = None
    ec2 = None
    s3 = None
    s3_client = None
    auto_scaling = None
    region = None

    def __init__(self):
        bc_session = get_session()
        self._session = Session(botocore_session=bc_session)

        self._auth = e3.load_authentication()
        if self._auth:
            creds_provider = bc_session.get_component('credential_provider')
            creds_provider.insert_before('env', self._auth)

        self.cloud_formation = self._session.resource("cloudformation")
        self.ec2 = self._session.client("ec2")
        self.rds = self._session.client("rds")
        self.s3 = self._session.resource("s3")
        self.s3_client = self._session.client("s3")
        self.auto_scaling = self._session.client('autoscaling')
        self.region = self._session.region_name
