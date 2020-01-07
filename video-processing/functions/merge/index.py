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
    return fileDir, shortname, extension


@print_excute_time
def handler(event, context):
    evt = json.loads(event)
    video_key = evt['video_key']
    oss_bucket_name = evt['oss_bucket_name']
    split_keys = evt['split_keys']
    output_prefix = evt['output_prefix']
    video_type = evt['target_type']
    video_process_dir = evt['video_proc_dir']
    
    transcoded_split_keys = []
    for k in split_keys:
        fileDir, shortname, extension = get_fileNameExt(k)
        transcoded_filename = 'transcoded_%s%s' % (shortname, video_type)
        transcoded_filepath = os.path.join(fileDir, transcoded_filename)
        transcoded_split_keys.append(transcoded_filepath)

    creds = context.credentials
    auth = oss2.StsAuth(creds.accessKeyId,
                        creds.accessKeySecret, creds.securityToken)
    oss_client = oss2.Bucket(
        auth, 'oss-%s-internal.aliyuncs.com' % context.region, oss_bucket_name)

    if len(transcoded_split_keys) == 0:
        raise Exception("no transcoded_split_keys")
    
    LOGGER.info({
        "target_type": video_type,
        "transcoded_split_keys": transcoded_split_keys
    })
    
    _, shortname, extension = get_fileNameExt(video_key)
    segs_filename = 'segs_%s.txt' % (shortname + video_type)
    segs_filepath = os.path.join(video_process_dir, segs_filename)

    if os.path.exists(segs_filepath):
        os.remove(segs_filepath)

    with open(segs_filepath, 'a+') as f:
        for filepath in transcoded_split_keys:
            f.write("file '%s'\n" % filepath)

    merged_filename = 'merged_' + shortname + video_type
    merged_filepath = os.path.join(video_process_dir, merged_filename)

    if os.path.exists(merged_filepath):
        os.remove(merged_filepath)

    subprocess.call([FFMPEG_BIN, '-f', 'concat', '-safe', '0', '-i',
                     segs_filepath, '-c', 'copy', '-fflags', '+genpts', merged_filepath])

    LOGGER.info('output_prefix ' + output_prefix)
    merged_key = os.path.join(output_prefix, shortname, merged_filename)
    oss_client.put_object_from_file(merged_key, merged_filepath)
    LOGGER.info("Uploaded %s to %s" % (merged_filepath, merged_key))

    res = {
        video_type: merged_key,
        "video_proc_dir": video_process_dir
    }

    return res
