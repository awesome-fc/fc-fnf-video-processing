# -*- coding: utf-8 -*-
import subprocess
import oss2
import logging
import json
import os
import time
import shutil

logging.getLogger("oss2.api").setLevel(logging.ERROR)
logging.getLogger("oss2.auth").setLevel(logging.ERROR)

LOGGER = logging.getLogger()

NAS_ROOT = "/mnt/auto/"
FFMPEG_BIN = NAS_ROOT + "ffmpeg"

# a decorator for print the excute time of a function
def print_excute_time(func):
    def wrapper(*args, **kwargs):
        local_time = time.time()
        ret = func(*args, **kwargs)
        LOGGER.info('current Function [%s] excute time is %.2f' %
              (func.__name__, time.time() - local_time))
        return ret
    return wrapper

def get_fileNameExt(filename):
    (fileDir, tempfilename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(tempfilename)
    return shortname, extension

@print_excute_time
def handler(event, context):
    evt = json.loads(event)
    video_key = evt['video_key']
    output_prefix = evt['output_prefix']
    oss_bucket_name = evt['oss_bucket_name']

    creds = context.credentials
    auth = oss2.StsAuth(creds.accessKeyId, creds.accessKeySecret, creds.securityToken)
    oss_client = oss2.Bucket(auth, 'oss-%s-internal.aliyuncs.com' % context.region, oss_bucket_name)

    video_proc_dir = NAS_ROOT + context.request_id
    os.system("mkdir -p {}".format(video_proc_dir))
    
    shortname, extension = get_fileNameExt(video_key)
    video_name = shortname + extension
    input_path = os.path.join(video_proc_dir, video_name)
    obj = oss_client.get_object_to_file(video_key, input_path)

    mp3_filename = '{}.mp3'.format(shortname)
    mp3_filepath = video_proc_dir + "/" + mp3_filename
    mp3_key = os.path.join(output_prefix, mp3_filename)

    if os.path.exists(mp3_filepath):
        os.remove(mp3_filepath)

    subprocess.call([ FFMPEG_BIN, '-i', input_path, '-q:a',
                     '0', '-map', 'a', mp3_filepath])
    
    oss_client.put_object_from_file(mp3_key, mp3_filepath)
    
    LOGGER.info("Uploaded %s to %s tp " % (mp3_key, mp3_filepath))
    
    # delete all files in nas
    shutil.rmtree(video_proc_dir)
    
    return {"mp3_key": mp3_key}
