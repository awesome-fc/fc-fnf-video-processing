## 简介

本项目是[轻松构建基于 Serverless 架构的弹性高可用视频处理系统](https://yq.aliyun.com/articles/727684) 的示例工程

假设您是对短视频进行简单的处理， 架构方案图如下：

![image](main.png)

如上图所示， 用户上传一个视频到 OSS, OSS 触发器自动触发函数执行， 函数调用 FFmpeg 进行视频转码， 并且将转码后的视频保存回 OSS。

您可以直接基于示例工程部署您的简单视频处理系统服务， 但是当您想要处理大视频(比如 test_huge.mov ) 或者对小视频进行多种耗时较长组合操作的时候，您会发现函数很大概率会执行失败，原因是函数计算的执行环境存在一些限制， 比如最大执行时间为 10 分钟， 最大内存为 3G。这个时候您可以参考[全功能视频处理系统示例](https://github.com/awesome-fc/fc-fnf-video-processing/tree/master/video-processing)

## 操作部署

[免费开通函数计算](http://statistics.cn-shanghai.1221968287646227.cname-test.fc.aliyun-inc.com/?title=ServerlessVideo&theme=ServerlessVideo&author=rsong&type=click&url=http://fc.console.aliyun.com)，按量付费，函数计算有很大的免费额度。

[免费开通对象存储 OSS](oss.console.aliyun.com/)

#### 1. clone 该工程

```bash
git clone  https://github.com/awesome-fc/fc-fnf-video-processing.git
```

进入 `simple-video-processing` 目录

复制 `.env_example` 文件为 `.env`, 并且修改 `.env` 中的信息为自己的信息

#### 2. 安装并且配置最新版本的 [fun](https://help.aliyun.com/document_detail/64204.html)

[fun 安装手册](https://github.com/alibaba/funcraft/blob/master/docs/usage/installation-zh.md)

在使用前，我们需要先进行配置，通过键入 fun config，然后按照提示，依次配置 Account ID、Access Key Id、Secret Access Key、 Default Region Name 即可

#### 3. 执行部署命令

- 先在响应的 region 指定的目录上传 FFmpeg 可执行文件到 OSS 上， 比如该示例是在杭州名为 fc-hz-demo 的 bucket 的 fnf_video/binary/ffmpeg 目录中

> FFmpeg 可执行文件可以直接使用 video-processing/.fun/nas/auto-default/video-demo/ffmpeg, 也可以从 [https://www.johnvansickle.com/ffmpeg/](https://www.johnvansickle.com/ffmpeg/) 下载最新版。

- 更新 template.yml 文件， 如下图所示：
    ![image](diy.png)
    > 其中 2 必须更改，因为 bucket 名字是唯一的， 其他可以参考，不用修改

- 执行 `fun deploy`