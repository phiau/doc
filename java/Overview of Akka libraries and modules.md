## Overview of Akka libraries and modules （Akka 库和模块概述）
- 原文链接：[http://doc.akka.io/docs/akka/current/java/guide/modules.html](http://doc.akka.io/docs/akka/current/java/guide/modules.html "http://doc.akka.io/docs/akka/current/java/guide/modules.html")

在深入写最佳 actor 练习之前，预览最常用的 akka 库将会有所帮助。这会帮助你开始思考你的系统要使用的功能。所有 akka 核心工功能都是开源软件（OSS Open Source Software）。Lightbend 赞助 akka 开发，但也可以帮助你提供培训、咨询、支持和企业套件等商业产品，这是一套用于管理 akka 系统的综合工具。

Akka OSS 包含一下功能，稍后将在此页面介绍：

- Actor 库
- Remoting 远程处理
- Cluster 集群
- Cluster Sharding 集群分片
- Cluster Singleton 集群单例
- Cluster Publish-Subscribe 集群发布订阅
- Persistence 持久化
- Distributed Data 分布式数据
- HTTP

使用 Lightbend 订阅，你可以在生产中使用企业套件。企业套件包括 Akka 核心功能的以下拓展：

- Split Brain Resolver 从网络分区检测和恢复，消除数据不一致和可能的宕机；
- Configuration Checker 检查潜在的配置问题和日志建议；
- Diagnostics Recorder 以一种格式捕获配置和系统信息，使其易于在开发和生产过程中排除问题；
- Thread Starvation Detector 监控一个 Akka 调度程序，如果它没有响应，记录警告；

这里不会列出所有可用的模块，但是会概述主要的功能，并让你了解，在你开始在 akka 上构建的系统可以达到的复杂程度。

### Actor 库

Akka 核心库是 akka-actor。但是 actor 使用 akka 库，提供了一致的综合模式，可以帮助你解决并发或分布式系统设计中出现的挑战。From a birds-eye view,actor 是一种编程范式，将封装（OOP的特性之一）封装到了极致。和对象不同，actor 不仅封装了他们的状态，还包括执行。actor 之间交互不是通过调用方法，而是通过传递消息。虽然这种差异很小，但是实际上它允许我们打破 OOP 的限制，在涉及到并发和远程通讯时。不用担心这个描述感觉水平太高，难以完全掌握，在下个章节我们会详细解释 actor。现在，重要的一点是，这是一个在基本层面处理并发和分发的模型，而不是尝试将这些特性带到 OOP。

Actor 解决的挑战包括：

- 如何构建和设计高性能的并发应用程序；
- 如何处理多线程环境中的错误；
- 如何保护我的项目免受并发的陷阱；

### Remoting

Remoting 可以让不同物理机上的 actor 无缝的交换消息。虽然想一个 jar 包一样的发布，Remoting 与一个库相比，更像一个模块。你主要通过配置启用它，它只有几个 api。多亏 actor 模型，远程和本地的消息发送看起来完全一样。你本地系统使用的模式，可以直接转换为远程系统。你很少需要直接使用 Remoting，但它为构建集群子系统提供了基础。

Remoting 解决的挑战包括：

- 如何标识位于远程位置的 actor 系统；
- 如何标识位于远程位置的 actor 系统的某个 actor；
- 如何将消息转换成通信中的字节流；
- 如何管理主机间低级别，网络连接（和重新链接），检测错误的 actor 系统和主机，全部透明；
- 如何在相同的网络连接上，不相关的一组 actor 之间的复杂通信，全部透明；

## Cluster

如果你有一组 actor 系统合作解决一些业务问题，然后你想有秩序的管理这些系统。而 Remoting 解决了寻址和与远程系统的组件进行通信的问题，集群使你能够将其组织成为“meta-system”通过成员之间的协议。在大多数情况下，你要使用集群模块，而不是直接使用远程。集群在 Remoting 之上提供了大量的真实应用程序需要的附加服务。

Cluster 模块解决的挑战包括：
- 如何维护一组可以彼此通信并且互相认为是集群的一部分的 actor 系统（集群）；
- 如何将新的系统安全的引入已经存在的一组成员；
- 如何可靠的检测暂时无法访问的系统；
- 如何移除失败的主机/系统（或者缩小系统），以便余下的所有成员都同意集群的剩余子集？
- 如何在当前的成员集中分配计算；
- 如何将集群的成员指定为某一个角色，换句话说，提供某些服务而不是其他服务器；

## Cluster Sharding 集群分片

分片有助于解决在 Akka 集群成员之间分配一组角色的问题。分片是一种大多时候和 Persistence （持久化）一起使用的模式，用于平衡大量的持久化实体到集群成员，并在成员奔溃或离开时，将它们迁移到其他节点。

解决的问题包括：
- 如何在一套系统上构建和拓展一大组有状态的实体；
- 如何确保集群中的实体正确分配，以使整个机器之间的负载均衡；
- 如何确保从奔溃的系统中迁移实体，而不会丢失状态；
- 如何确保实体在同一个时间不存在于多个系统，因此保持一致；