## Akka Quickstart with Java 快速开始 Akka（java 语言版本）
- 原文链接：[http://developer.lightbend.com/guides/akka-quickstart-java/](http://developer.lightbend.com/guides/akka-quickstart-java/ "http://developer.lightbend.com/guides/akka-quickstart-java/")

Akka 是一套用于在 JVM 构建高并发、分布式、容错高、事件驱动的应用程序的运行、开发工具包。Akka 可以用于 Java 和 Scala。

Actors 是 Akka 的执行单元。Actors 是一种抽象模型，使得编写正确的并发、分布式系统更加容易。

尝试 “hello world” 之后，全面的了解 “Getting Started Guide（入门指南）” 可以很好的继续学习更多有关 Akka 知识。

### What Hello World does

首先，类 main 创建了一个 akka.actor.ActorSystem，这是一个容器，所有的 Actors 都运行在这个容器里。然后创建了三个 Greeter Actor 实例，和一个 Printer Actor 实例。

示例，发送消息给 Greeter Actor 实例，并在存储在实例。最后，向 Greeter Actors 发送指令触发使他们发送消息给 Printer Actor，然后 Printer Actor 把内容输出在控制台：

代码就不用解释了：

- 首先是要创建 Actor，可以通过 Props.create 来传参数给继承 AbstractActor 的构造函数；
- 然后要给相应的 Actor 发送消息的时候，就调用 Actor 实例的 tell 方法，有一个参数，是传发送者的；

### 使用 Actor 模型的好处

Akka 以下特征让你更加直观的解决并发和可拓展的问题：

- 事件驱动模型 -- Actor 是响应消息来执行动作的。Actor 之间的通信是异步的，所以允许 Actor 发送完消息后，继续做自己的事，而不用阻塞在等待回复那里。
- 强大的隔离原则 -- 不像常规的 Java 对象，Actor 没有公共的方法让你可以调用。替代的是，它的公共 api 是通过消息处理定义的（也就是说，他的 api 调用，是必须通过消息传递来调用）。这阻止了 Actor 之间共享任何状态；观察 Actor 状态的唯一途径，是通过发送消息询问。
- 位置透明 -- 系统调用工厂构造 Actor 并返回实例的引用。因为位置无关紧要，Actor 实例可以启动、停止、移除和重新启动，来扩大和缩小，以及从异常中恢复。
- 轻量级 -- 每个实例仅仅消耗几百个字节，所以一个应用程序实际上允许有许许多多个 Actor 存在。

让我们来看一下，在 Hello World 的上下文中，使用 Actor 和 message 的最佳方法。 

======================================================================================================

## Defining Actors and messages
- 原文链接：[http://developer.lightbend.com/guides/akka-quickstart-java/define-actors.html](http://developer.lightbend.com/guides/akka-quickstart-java/define-actors.html "http://developer.lightbend.com/guides/akka-quickstart-java/define-actors.html")

定义 Actor 和相应的 message 时，牢记下面这些建议：

- 由于 message 是 Actor 的公有 api，所以定义好名称（有风雨予以和特定含义）的 message 是一种好的做法，即使它们只是对你的数据类型做封装。这会让它们更加容易使用、理解还有调试。
- Message 应该是不变的（暂时不太理解这里说的不变），因为它们在不同的线程共享。
- 把一个 actor 相应的 message 作为一个静态类放在一个 Actor 类里面是一个很好的做法。这样会更加容易理解 actor 期望处理的是什么类型的 message。
- 在 Actor 类中使用静态的 props 来描述如何构造 Actor 也是一个常见的通用的做法。

### The Greeter Actor

下面是 Greeter.java 的部分代码，实现了 Greeter Actor：

	package com.lightbend.akka.sample;
	
	import akka.actor.AbstractActor;
	import akka.actor.ActorRef;
	import akka.actor.Props;
	import com.lightbend.akka.sample.Printer.Greeting;
	
	public class Greeter extends AbstractActor {
	  static public Props props(String message, ActorRef printerActor) {
	    return Props.create(Greeter.class, () -> new Greeter(message, printerActor));
	  }
	
	  static public class WhoToGreet {
	    public final String who;
	
	    public WhoToGreet(String who) {
	        this.who = who;
	    }
	  }
	
	  static public class Greet {
	    public Greet() {
	    }
	  }
	
	  private final String message;
	  private final ActorRef printerActor;
	  private String greeting = "";
	
	  public Greeter(String message, ActorRef printerActor) {
	    this.message = message;
	    this.printerActor = printerActor;
	  }
	
	  @Override
	  public Receive createReceive() {
	    return receiveBuilder()
	        .match(WhoToGreet.class, wtg -> {
	          this.greeting = message + ", " + wtg.who;
	        })
	        .match(Greet.class, x -> {
	          printerActor.tell(new Greeting(greeting), getSelf());
	        })
	        .build();
	  }
	}

下面对功能做一个分解：

- `Greeter` 类继承了 `akka.actor.AbstractActor` 类，还有实现了 `createReceive` 方法；
- `Greeter` 的构造函数接收两个参数：`String message`，这个会用于构建 greeting message he `ActorRef printerActor`，这是处理 greeting 输出的 Actor 的引用。
- `receiveBuilder` 定义了行为，Actor 针对接收不同的 message 应该做出哪些反应。一个 Actor 可以有状态。 访问和改变 Actor 的内部状态(内部变量)，完全是线程安全的，因为它收到 Actor 模型的保护（这个得再捋捋）。`createReceive` 方法应该处理 actor 所期望的 message。例如上面的 `Greetre` 例子，它希望两种类型的 message：`WhoToGreet` 和 `Greet`。前者将会更新 actor `greeting` 的状态，后者会被触发发送 `greeting` 给 `Printer` Actor.
- 静态 `props` 方法创建还有返回一个 `Props` 实例。`Props` 是一个配置类，用于创建 actor 需要的特殊参数，把它认为是一个不变，然后可以自用分享，用于创建一个可以包含相应部署信息的 actor（这里也有点拗口，不是很理解）。这里示例简单的传递 Actor 构造需要的参数。我们会在后面看到 `props` 方法在行为里面。

======================================================================================================

## Creating the Actors
- 原文链接：[http://developer.lightbend.com/guides/akka-quickstart-java/create-actors.html](http://developer.lightbend.com/guides/akka-quickstart-java/create-actors.html "http://developer.lightbend.com/guides/akka-quickstart-java/create-actors.html")

目前位置，我们已经看了 Actor 和相应的 message 的定义。现在让我们深入的了解位置透明的功能，并了解创建 Actor 实例。

### The power of location transparency（暂时不知道中文如何描述恰当）

在 Akka 里，你不能用 `new` 这个关键字来创建 Actor 的实例。代替的，你得用 factory 来创建 Actor 实例。factory 不会返回一个 actor 实例，而是返回一个引用，`akka.actor.ActorRef`，这个指向 actor 实例。这种间接级别在分布式系统中增加了大量的功能和灵活性。

在 Akka 里，位置无关紧要（这里说的应该是指本地和远程）。位置透明，意味着 ActorRef 可以位置一样的语义，表示一个本进程实例或者远程实例（意思就是说实例引用的对象，不管是本地或者是在其他物理机上，对使用者根本没差别）。如果需要，可以在运行的时候，通过改变 Actor 的位置或者整个应用的拓扑结构来优化系统。这样就可以用 “let it crash” 失败管理模型，来 “治愈” 系统本身，通过冲突错误 Actor 然后启动正常的一个。（字面好难用中文描述，觉得意思就是说，这种模型，即使某一个 Actor 发生冲突错误了，也可以通过启动正常的那些来解决问题）

### The Akka ActorSystem

`akka.actor.ActorSystem` factory 某种程度跟 Spring 的 `BeanFactory` 很相似。它扮演了一个 Actor 容器，管理着他们的生命周期。`actorOf` factory 方法创建 Actor 并采用了两个参数，一个是叫做 `Props` 的配置对象，一个是 name。

Actor 和 `ActorSystem` 的名称在 Akka 很重要。例如：你可以用他们进行查找。使用与你领域一致的，有含义的名字，可以使得更加容易猜它们的用途（说的就跟一般变量名一样，名字要起得一看就知道是什么用的）。

上一个话题回顾了 Hello World Actor 的定义。看下 `AkkaQuickstart.java` 的代码，创建了 `Greeter` 和 `Printer` Actor 实例：

	final ActorRef printerActor =  system.actorOf(Printer.props(), "printerActor");
	final ActorRef howdyGreeter = system.actorOf(Greeter.props("Howdy", printerActor), "howdyGreeter");
	final ActorRef helloGreeter = system.actorOf(Greeter.props("Hello", printerActor), "helloGreeter");
	final ActorRef goodDayGreeter = system.actorOf(Greeter.props("Good day", printerActor), "goodDayGreeter");

注意下面事项：

- `ActorSystem` 的 `actorOf` 方法创建了 `Printer` Actor。就像我们之前讨论的，这个使用了 `Printer` 的静态方法 `props` 来获得 `Props` 值。`ActorRef` 提供新创建的 `Printer` Actor 实例的引用。
- 对与 `Greeter`，上面的代码创建了三个 Actor 实例，每一个都有特殊的 greeting message。

注意：在这个例子，所有的 `Greeter` Actor 都用了同一个 `Printer` 实例，但是我们可以创建多个 `Printer` Actor 实例。 该例子使用了一个来说明我们稍后将介绍到的消息传递的重要概念。

======================================================================================================

## Asynchronous communication

- 原文链接：[http://developer.lightbend.com/guides/akka-quickstart-java/communicate-with-actors.html](http://developer.lightbend.com/guides/akka-quickstart-java/communicate-with-actors.html "http://developer.lightbend.com/guides/akka-quickstart-java/communicate-with-actors.html")

Actor 是反应性的和消息驱动的。一个 Actor 不会做任何事知道接收到 message。Actor 之间使用异步消息进行通信。这确保发送者不用一直等着接收者处理完他们收到的消息。相反的，发送者把消息发给接收者的“邮箱”然后可以去做自己的事。Actor 的“邮箱”实际上是一个有顺序的消息队列。从同一个 Actor 发送的多条消息的顺序会被保留，但是可能会和其他 Actor 发送的消息交错（意思就是是，同一个 Actor 发送过来的消息，会保证顺序）。

你可能会疑惑，Actor 不处理消息的时候，在干什么，例如做什么实际工作？如果它除了内存外，不消耗任何资源，那么它会被挂起。再次说明了，它的轻量级，高效。

### Sending message to an Actor

把消息放入一个 Actor 的邮箱，对在 `ActorRef` 使用 `tell` 方法。例如，Hello World 的 main class 发送 message 给 `Greeter` Actor，像下面：

	howdyGreeter.tell(new WhoToGreet("Akka"), ActorRef.noSender());
	howdyGreeter.tell(new Greet(), ActorRef.noSender());
	
	howdyGreeter.tell(new WhoToGreet("Lightbend"), ActorRef.noSender());
	howdyGreeter.tell(new Greet(), ActorRef.noSender());
	
	helloGreeter.tell(new WhoToGreet("Java"), ActorRef.noSender());
	helloGreeter.tell(new Greet(), ActorRef.noSender());
	
	goodDayGreeter.tell(new WhoToGreet("Play"), ActorRef.noSender());
	goodDayGreeter.tell(new Greet(), ActorRef.noSender());

`Greeter` Actor 同样发送 message 给 `Printer` Actor：

	printerActor.tell(new Greeting(greeting), getSelf());

我们已经知道了如何创建 actor 和发送 message。现在让我们通过 Main class 查看全部内容。

======================================================================================================

## The Main class

- 原文链接：[http://developer.lightbend.com/guides/akka-quickstart-java/main-class.html](http://developer.lightbend.com/guides/akka-quickstart-java/main-class.html "http://developer.lightbend.com/guides/akka-quickstart-java/main-class.html")

Hello World 的 `Main` class 创建和控制 actor。注意到像容器一样使用一个 `ActorSystem`，还有使用 `actorOf` 方法创建 Actor。最后，class 创建了发送给 Actor 的 message。 

	package com.lightbend.akka.sample;
	
	import akka.actor.ActorRef;
	import akka.actor.ActorSystem;
	import com.lightbend.akka.sample.Greeter.*;
	
	import java.io.IOException;
	
	public class AkkaQuickstart {
	  public static void main(String[] args) {
	    final ActorSystem system = ActorSystem.create("helloakka");
	    try {
	      final ActorRef printerActor = 
	        system.actorOf(Printer.props(), "printerActor");
	      final ActorRef howdyGreeter = 
	        system.actorOf(Greeter.props("Howdy", printerActor), "howdyGreeter");
	      final ActorRef helloGreeter = 
	        system.actorOf(Greeter.props("Hello", printerActor), "helloGreeter");
	      final ActorRef goodDayGreeter = 
	        system.actorOf(Greeter.props("Good day", printerActor), "goodDayGreeter");
	
	      howdyGreeter.tell(new WhoToGreet("Akka"), ActorRef.noSender());
	      howdyGreeter.tell(new Greet(), ActorRef.noSender());
	
	      howdyGreeter.tell(new WhoToGreet("Lightbend"), ActorRef.noSender());
	      howdyGreeter.tell(new Greet(), ActorRef.noSender());
	
	      helloGreeter.tell(new WhoToGreet("Java"), ActorRef.noSender());
	      helloGreeter.tell(new Greet(), ActorRef.noSender());
	
	      goodDayGreeter.tell(new WhoToGreet("Play"), ActorRef.noSender());
	      goodDayGreeter.tell(new Greet(), ActorRef.noSender());
	
	      System.out.println(">>> Press ENTER to exit <<<");
	      System.in.read();
	    } catch (IOException ioe) {
	    } finally {
	      system.terminate();
	    }
	  }
	}

相似的，我们再看一次所有定义 Actor 的代码，还有他们所接受的 Message。