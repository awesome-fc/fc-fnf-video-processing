# -*- coding: utf-8 -*-
import logging
import oss2
import os
import time
import json

logging.getLogger("oss2.api").setLevel(logging.ERROR)
logging.getLogger("oss2.auth").setLevel(logging.ERROR)

FFMPEG_BUKCET_NAME = os.environ["FFMPEG_BUKCET_NAME"]
FFMPEG_BIN_KEY = os.environ["FFMPEG_BIN_KEY"]
OUTPUT_DST = os.environ["OUTPUT_DST"]
DST_TARGET = os.environ["DST_TARGET"]


# a decorator for print the excute time of a function
def print_excute_time(func):
    def wrapper(*args, **kwargs):
        local_time = time.time()
        ret = func(*args, **kwargs)
        print('current Function [%s] excute time is %.2f' %
              (func.__name__, time.time() - local_time))
        return ret
    return wrapper


def get_fileNameExt(filename):
    (fileDir, tempfilename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(tempfilename)
    return shortname, extension

# initializer downlaod ffmpeg
@print_excute_time
def initializer(context):
    if not os.path.exists('/tmp/ffmpeg'):
        creds = context.credentials
        auth = oss2.StsAuth(creds.accessKeyId, creds.accessKeySecret, creds.securityToken)
        oss_client = oss2.Bucket(auth, 'oss-%s-internal.aliyuncs.com' % context.region, FFMPEG_BUKCET_NAME)
        oss_client.get_object_to_file(FFMPEG_BIN_KEY, '/tmp/ffmpeg')
        os.system("chmod 777 /tmp/ffmpeg")

@print_excute_time
def handler(event, context):
    evt = json.loads(event)
    evt = evt["events"]
    oss_bucket_name = evt[0]["oss"]["bucket"]["name"]
    object_key = evt[0]["oss"]["object"]["key"]
    shortname, extension = get_fileNameExt(object_key)
    input_path = '/tmp/' + shortname + extension
    creds = context.credentials
    auth = oss2.StsAuth(creds.accessKeyId, creds.accessKeySecret, creds.securityToken)
    oss_client = oss2.Bucket(auth, 'oss-%s-internal.aliyuncs.com' % context.region, oss_bucket_name)
    obj = oss_client.get_object_to_file(object_key, input_path)

    transcoded_filepath = '/tmp/' + shortname + DST_TARGET
    command = '/tmp/ffmpeg -y -i {0} -preset superfast {1}'.format(
        input_path, transcoded_filepath)

    os.system(command)
    oss_client.put_object_from_file(OUTPUT_DST + shortname + DST_TARGET , transcoded_filepath)

    return "ok"
