## 简介

本项目是[轻松构建基于 Serverless 架构的弹性高可用视频处理系统](https://yq.aliyun.com/articles/727684) 的示例工程。

- [函数计算](https://help.aliyun.com/product/50980.html) ：阿里云函数计算是事件驱动的全托管计算服务。通过函数计算，您无需管理服务器等基础设施，只需编写代码并上传。函数计算会为您准备好计算资源，以弹性、可靠的方式运行您的代码，并提供日志查询、性能监控、报警等功能。

- [函数工作流](https://help.aliyun.com/product/113549.html)：函数工作流（Function Flow，以下简称 FnF）是一个用来协调多个分布式任务执行的全托管云服务。您可以用顺序，分支，并行等方式来编排分布式任务，FnF 会按照设定好的步骤可靠地协调任务执行，跟踪每个任务的状态转换，并在必要时执行用户定义的重试逻辑，以确保工作流顺利完成。

simple-video-processing 是基于函数计算 (FC) 实现的简单视频处理(转码)系统。

video-processing 是基于函数计算 (FC) + 函数工作流（FnF）实现的全功能视频处理(转码)系统。

[免费开通函数计算](https://statistics.functioncompute.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&src=article&url=http://fc.console.aliyun.com)，按量付费，函数计算有很大的免费额度。

[免费开通函数工作流](https://statistics.functioncompute.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&src=article&url=http://fnf.console.aliyun.com)，按量付费，函数工作流有很大的免费额度。

## 简单视频处理系统

假设您是对短视频进行简单的处理， 架构方案图如下：

![image](simple-video-processing/main.png)

如上图所示， 用户上传一个视频到 OSS, OSS 触发器自动触发函数执行， 函数调用 FFmpeg 进行视频转码， 并且将转码后的视频保存回 OSS。

您可以直接基于示例工程 `simple-video-processing` 部署您的简单视频处理系统服务， 但是当您想要处理大视频，比如 [test_huge.mov](https://fc-hz-demo.oss-cn-hangzhou.aliyuncs.com/fnf_video/inputs/test_huge.mov) 的时候， 您会发现函数会执行失败， 原因是函数计算的执行环境存在一些限制， 比如最大执行时间为 10 分钟， 最大内存为 3G。

为了突破函数计算执行环境的限制，引入函数工作流 FnF 去编排函数实现一个功能强大的全功能视频处理系统。

## 全功能视频处理系统

![image](video-processing/flow.png)

如上图所示， 假设用户上传一个 mov 格式的视频到 OSS, OSS 触发器自动触发函数执行， 函数调用 FnF 执行， FnF 会并行进行提取音频文件，同时进行 avi, mp4, flv 格式的转码。 所以您可以实现如下需求：

- 一个视频文件可以同时被转码成各种格式以及其他各种自定义处理，比如增加水印处理或者 在 after-process 更新信息到数据库等

- 同时有多个文件上传到 OSS, 函数计算会自动伸缩， 多个文件的处理也同时并发进行

- 对于每一个视频， 先进行切片处理， 然后并行转码切片，最后合成，通过设置合理的切片时间，可以加速较大视频的转码速度

- 结合 NAS + 视频分片, 可以解决超大视频(大于3G)的转码

详情参考 `video-processing` 目录