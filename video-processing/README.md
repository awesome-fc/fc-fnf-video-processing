## 简介

本项目是[轻松构建基于 Serverless 架构的弹性高可用音视频处理系统](https://yq.aliyun.com/articles/727684) 的示例工程

该工程示例已经上线到函数计算应用中心，免费开通函数计算 即可在控制台应用中心 -> Video Transcoder  新建应用即查看到 。

如下图所示， 假设用户上传一个 mov 格式的视频到 OSS, OSS 触发器自动触发函数执行， 函数调用 FnF 执行， FnF 会并行进行提取音频文件，同时进行 avi, mp4, flv 格式的转码。

您可以实现如下需求：

- 一个视频文件可以同时被转码成各种格式以及其他各种自定义处理，比如增加水印处理或者 在 after-process 更新信息到数据库等

- 同时有多个文件上传到 OSS, 函数计算会自动伸缩， 多个文件的处理也同时并发进行

- 对于每一个视频， 先进行切片处理， 然后并行转码切片，最后合成，通过设置合理的切片时间，可以加速较大视频的转码速度

- 结合 NAS + 视频分片, 可以解决超大视频(大于3G)的转码

![image](flow.png)

您可以直接基于示例工程部署您的全功能视频处理系统服务， 但是当您想要处理视频逻辑消耗的内存不超过3G，处理时间不超过 10 min，即可以在一次函数执行完成的情况下，这个时候您可以直接参考[简单视频处理系统示例](https://github.com/awesome-fc/fc-fnf-video-processing/tree/master/simple-video-processing)

## 步骤
1. 免费开通相关云服务: [函数计算](https://statistics.functioncompute.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&src=article&url=http://fc.console.aliyun.com)， [函数工作流](https://statistics.functioncompute.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&src=article&url=http://fnf.console.aliyun.com)， [资源编排](https://rosnext.console.aliyun.com/)， [文件存储服务NAS](https://nas.console.aliyun.com/)，[对象存储 OSS](oss.console.aliyun.com/)

2. 安装并配置 [Fun 工具](https://help.aliyun.com/document_detail/64204.html)

3. 部署 FC, FnF 资源

```bash
git clone  https://github.com/awesome-fc/fc-fnf-video-processing.git
```

进入 `video-process` 目录

复制 `.env_example` 文件为 `.env`, 并且修改 `.env` 中的信息为自己的信息

- 将 template.yml 文件中 `trigger-fnf` 函数的中 Event 中 bucketName 修改成自己的

> 注: 如果修改 template.yml 中的 serviceName, 需要先执行 `fun nas init`, 生成本地对应的目录 `.fun/nas/auto-default/$(yourServiceName)`, 然后将 ffmpeg 和 ffprobe 的 binary 拷贝到该目录下。 ffmpeg 的 binary 可以直接使用.fun/nas/auto-default/video-demo 目录下面的 ffmpeg 和 ffprobe。

```bash
./deploy.sh
```

后面如果更新函数或者流程(不修改 serviceName 创建新的 service)， 只需要执行 `fun deploy` 即可

## 编排测试 FC 函数的工作流
第1步： 在[函数工作流控制台](https://fnf.console.aliyun.com/fnf/cn-hangzhou/flows)开始 video-demo 的执行，input 如下，替换 {your-bucket-name}：

```json
{
  "oss_bucket_name": "{your-bucket-name}",
  "video_key": "fnf_video/inputs/fc-official-short.mov",
  "output_prefix": "fnf_video/outputs/fc/1",
  "segment_time_seconds": 10
}
```

第2步： 在控制台观察流程执行

## OSS 上传视频, 触发整个转码流程

**效果示意图**

![](fnf-video-process.gif)