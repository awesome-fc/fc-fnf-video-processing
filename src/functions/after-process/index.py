# -*- coding: utf-8 -*-
import os
import json
import shutil

def handler(event, context):
    evt = json.loads(event)
    video_process_dir = evt['video_proc_dir']
    # delete all files in nas
    shutil.rmtree(video_process_dir)
    
    # do your logic, for example, insert/update a record in to db
    
    return {}
