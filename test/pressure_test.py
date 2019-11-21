# -*- coding: utf-8 -*-

import fc2
import threading, json, os, sys
from aliyunsdkcore.client import AcsClient
from aliyunsdkfnf.request.v20190315 import StartExecutionRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException

# 修改成自己的
OUTPUT_DST = "fnf_video/outputs/pressureTest/"
FLOW_NAME = "video-fc-prod-fc"
AK_ID = "xxxxxxx"
AK_SECRET = "yyyyyyyy"
REGION = "cn-hangzhou"

# 主要是修改 evt[0]["oss"]["bucket"]["name"] 和 evt[0]["oss"]["object"]["key"] 这两个参数
TEST_OSS_EVENT ='''
{
  "events": [
    {
      "eventName": "ObjectCreated:PutObject",
      "eventSource": "acs:oss",
      "eventTime": "2017-04-21T12:46:37.000Z",
      "eventVersion": "1.0",
      "oss": {
        "bucket": {
          "arn": "acs:oss:cn-hangzhou:123456789:fc-hz-demo",
          "name": "fc-hz-demo",
          "ownerIdentity": "123456789",
          "virtualBucket": ""
        },
        "object": {
          "deltaSize": 122539,
          "eTag": "688A7BF4F233DC9C88A80BF985AB7329",
          "key": "fnf_video/inputs/480P.mov",
          "size": 122539
        },
        "ossSchemaVersion": "1.0",
        "ruleId": "9adac8e253828f4f7c0466d941fa3db81161e853"
      },
      "region": "cn-shanghai",
      "requestParameters": {
        "sourceIPAddress": "140.205.128.221"
      },
      "responseElements": {
        "requestId": "58F9FF2D3DF792092E12044C"
      },
      "userIdentity": {
        "principalId": "123456789"
      }
    }
  ]
}
'''

# 模拟 oss 上传事件触发函数， oss 上提前准备好相应的测试视频
def mock_upload_video_2_oss(event, index):
    evt = json.loads(event)
    evt = evt["events"]
    oss_bucket_name = evt[0]["oss"]["bucket"]["name"]
    object_key = evt[0]["oss"]["object"]["key"]

    client = AcsClient(AK_ID, AK_SECRET, REGION)
    input = {
        "oss_bucket_name": oss_bucket_name,
        "video_key": object_key,
        "output_prefix": os.path.join(OUTPUT_DST, str(index)),
        # 视频 25 s 一个分片, 这个值根据具体情况设置， 
        # 如果想加速视频转码，这个值可以设置小点， 但是此时对于一个视频，转码需要更多的机器资源
        "segment_time_seconds": 25
    }

    try:
        request = StartExecutionRequest.StartExecutionRequest()
        request.set_FlowName(FLOW_NAME)
        request.set_Input(json.dumps(input))
        return client.do_action_with_exception(request)
    except ServerException as e:
        print(e.get_request_id())

def main(threads_num):
    ts = []
    for i in range(threads_num):
        t = threading.Thread(
            target=mock_upload_video_2_oss, args=(TEST_OSS_EVENT, i))
        t.start()
        ts.append(t)
        
    for t in ts:
        t.join()
        
    print("all fnf excutution is started")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("args error")
    threads_num = int(sys.argv[1])
    main(threads_num)
    
