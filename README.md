## 简介

本项目是[轻松构建基于 Serverless 架构的弹性高可用音视频处理系统](https://yq.aliyun.com/articles/727684) 的示例工程

该工程示例已经上线到函数计算应用中心，免费开通函数计算 即可在控制台应用中心 -> Video Transcoder  新建应用即查看到 。

如下图所示， 假设用户上传一个 mov 格式的视频到 OSS, OSS 触发器自动触发函数执行， 函数调用 FnF 执行，FnF 同时进行 1 种或者多种格式的转码(由 template.yml 中的 DST_FORMATS 参数控制)， 本示例配置的是同时进行 mp4, flv, avi 格式的转码。

您可以实现如下需求:

- 一个视频文件可以同时被转码成各种格式以及其他各种自定义处理，比如增加水印处理或者在 after-process 更新信息到数据库等。

- 当有多个文件同时上传到 OSS，函数计算会自动伸缩， 并行处理多个文件， 同时每次文件转码成多种格式也是并行。

- 结合 NAS + 视频切片， 可以解决超大视频的转码， 对于每一个视频，先进行切片处理，然后并行转码切片，最后合成，通过设置合理的切片时间，可以大大加速较大视频的转码速度。

![image](https://img.alicdn.com/tfs/TB1A.PSzrj1gK0jSZFuXXcrHpXa-570-613.png)

您可以直接基于示例工程部署您的全功能视频处理系统服务， 但是当您想要处理视频逻辑消耗的内存不超过3G，处理时间不超过 10 min，即可以在一次函数执行完成的情况下，这个时候您可以直接参考[简单视频处理系统示例](https://github.com/awesome-fc/fc-fnf-video-processing/tree/master/simple-video-processing)

## 部署步骤

### 准备工作

1. 免费开通相关云服务: [函数计算](https://statistics.functioncompute.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&src=article&url=http://fc.console.aliyun.com)， [函数工作流](https://statistics.functioncompute.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&src=article&url=http://fnf.console.aliyun.com)， [资源编排](https://rosnext.console.aliyun.com/)， [文件存储服务NAS](https://nas.console.aliyun.com/)，[对象存储 OSS](oss.console.aliyun.com/)
2. 安装并配置 [Serverless Devs](https://www.serverless-devs.com/docs/install)

### 1. 克隆本工程 

```bash
git clone  https://github.com/awesome-fc/fc-fnf-video-processing.git
```

### 2. 获取配置所需的 ARN

- 运行 `s deploy -t ram.yaml`
- 此时可以在命令行看到打印出的两个 role 的 ARN

![](https://i.loli.net/2021/07/25/6pcmq83RotBW2h5.png)

- 将获取的 ARN 填入 `s.yaml` 对应位置中

### 3. 修改相关文件

对于 `s.yaml` ：

- 将配置中 role 的 xxx 替换为步骤2中获得的 ARN
- 将 `bucket-demo` 替换为自己的 bucket
- 将日志工程 `sls-transcode-demo` 替换为自己的日志工程，全局共有4处

对于 `deploy.sh` :

- 将日志工程 `sls-transcode-demo` 替换为自己的日志工程

### 4. 部署服务

运行 `deploy.sh`，进行服务的部署。其中，包含 1 个日志工程，1 个函数工作流，以及 5 个函数。

```bash
./deploy.sh
```

### 5. 上传相关文件到 NAS

我们需要将放置在 `bin` 目录中，处理视频转码的相关工具上传到 NAS。

```bash
s nas upload bin nas:///mnt/auto
s nas command ls nas:///mnt/auto
```

## 编排测试 FC 函数的工作流

第1步： 在[函数工作流控制台](https://fnf.console.aliyun.com/fnf/cn-hangzhou/flows)开始 video-demo 的执行，input 如下，替换 {your-bucket-name}：

```json
{
  "oss_bucket_name": "{your-bucket-name}",
  "video_key": "fnf_video/inputs/fc-official-short.mov",
  "output_prefix": "fnf_video/outputs/fc/1",
  "segment_time_seconds": 15,
  "dst_formats": ["flv", "mp4"]
}
```

第2步： 在控制台观察流程执行

## OSS 上传视频, 触发整个转码流程

**效果示意图**

![](https://img.alicdn.com/tfs/TB1jgKSzCf2gK0jSZFPXXXsopXa-1280-720.gif)

