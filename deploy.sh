set -e
s sls-transcode-demo create
s video-demo-flow deploy
s fc-video-demo-split deploy
s fc-video-demo-transcode deploy
s fc-video-demo-merge deploy
s fc-video-demo-after-process deploy
s fc-oss-trigger-trigger-fnf deploy