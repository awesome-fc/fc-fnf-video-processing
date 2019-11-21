# -*- coding: utf-8 -*-
import os
import json
import logging

from aliyunsdkcore.client import AcsClient
from aliyunsdkfnf.request.v20190315 import StartExecutionRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import StsTokenCredential

LOGGER = logging.getLogger()

OUTPUT_DST = os.environ["OUTPUT_DST"]
FLOW_NAME = os.environ["FLOW_NAME"]

def handler(event, context):
    evt = json.loads(event)
    evt = evt["events"]
    oss_bucket_name = evt[0]["oss"]["bucket"]["name"]
    object_key = evt[0]["oss"]["object"]["key"]
    
    creds = context.credentials
    sts_token_credential = StsTokenCredential(creds.access_key_id, creds.access_key_secret, creds.security_token)
    client = AcsClient(region_id=context.region, credential=sts_token_credential)

    input = {
        "oss_bucket_name": oss_bucket_name,
        "video_key": object_key,
        "output_prefix": OUTPUT_DST,
        "segment_time_seconds": 25  # 视频 25 s 一个分片
    }
    
    try:
        request = StartExecutionRequest.StartExecutionRequest()
        request.set_FlowName(FLOW_NAME)
        request.set_Input(json.dumps(input))
        return client.do_action_with_exception(request)
    except ServerException as e:
        LOGGER.info(e.get_request_id())
    
    return "ok"
