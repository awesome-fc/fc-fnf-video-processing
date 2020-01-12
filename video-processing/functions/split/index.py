# -*- coding: utf-8 -*-
import subprocess
import oss2
import logging
import json
import os
import time
import math

logging.getLogger("oss2.api").setLevel(logging.ERROR)
logging.getLogger("oss2.auth").setLevel(logging.ERROR)

LOGGER = logging.getLogger()

MAX_SPLIT_NUM = 100

NAS_ROOT = "/mnt/auto/"
FFMPEG_BIN = NAS_ROOT + "ffmpeg"
FFPROBE_BIN = NAS_ROOT + "ffprobe"

class FFmpegError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status

def exec_FFmpeg_cmd(cmd_lst):
    try:
        subprocess.check_call(cmd_lst)
    except subprocess.CalledProcessError as exc:
        LOGGER.error('returncode:{}'.format(exc.returncode))
        LOGGER.error('cmd:{}'.format(exc.cmd))
        LOGGER.error('output:{}'.format(exc.output))
        # log json to Log Service as db
        # or insert record in mysql, etc
        raise FFmpegError(exc.output, exc.returncode)

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

def getVideoDuration(input_video):
    cmd = '{0} -i {1} -show_entries format=duration -v quiet -of csv="p=0"'.format(
        FFPROBE_BIN, input_video)
    raw_result = subprocess.check_output(cmd, shell=True)
    result = raw_result.decode().replace("\n", "").strip()
    duration = float(result)
    return duration

@print_excute_time
def handler(event, context):
    evt = json.loads(event)
    video_key = evt['video_key']
    oss_bucket_name = evt['oss_bucket_name']
    segment_time_seconds = str(evt['segment_time_seconds'])
    
    shortname, extension = get_fileNameExt(video_key)
    video_name = shortname + extension
    
    video_proc_dir = NAS_ROOT + context.request_id
    #os.system("mkdir -p {}".format(video_proc_dir))
    os.mkdir(video_proc_dir)
    os.system("chmod -R 777 " + video_proc_dir)

    creds = context.credentials
    auth = oss2.StsAuth(creds.accessKeyId, creds.accessKeySecret, creds.securityToken)
    oss_client = oss2.Bucket(auth, 'oss-%s-internal.aliyuncs.com' % context.region, oss_bucket_name)

    input_path = os.path.join(video_proc_dir,  video_name)
    obj = oss_client.get_object_to_file(video_key, input_path)
    
    video_duration = getVideoDuration(input_path)
    segment_time_seconds = int(segment_time_seconds)
    split_num = math.ceil(video_duration/segment_time_seconds)
    # adjust segment_time_seconds
    if split_num > MAX_SPLIT_NUM:
        segment_time_seconds = int(math.ceil(video_duration/MAX_SPLIT_NUM)) + 1
    
    segment_time_seconds = str(segment_time_seconds)
    exec_FFmpeg_cmd([FFMPEG_BIN, '-i', input_path, "-c", "copy", "-f", "segment", "-segment_time",
                     segment_time_seconds, "-reset_timestamps", "1", video_proc_dir + "/split_" + shortname + '_piece_%02d' + extension])

    split_keys = []
    for filename in os.listdir(video_proc_dir):
        if filename.startswith('split_' + shortname):
            filekey = os.path.join(video_proc_dir, filename)
            split_keys.append(filekey)

    return {"split_keys": split_keys, "video_proc_dir": video_proc_dir}
