set -e

STACK_NAME=video-processing-demo-$(date +%s)

# init nas and vpc
fun nas init

# sync .fun/nas/auto-default/video-demo/ffmpeg to nas, then you can use /mnt/auto/ffmpeg when excute funtion
# you can download latest ffmpeg at https://www.johnvansickle.com/ffmpeg/
fun nas sync

# Deploy FC functions and Flows
fun deploy