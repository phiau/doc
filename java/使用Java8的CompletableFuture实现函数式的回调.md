## 使用Java 8的CompletableFuture实现函数式的回调
- 原文链接：[http://www.infoq.com/cn/articles/Functional-Style-Callbacks-Using-CompletableFuture](http://www.infoq.com/cn/articles/Functional-Style-Callbacks-Using-CompletableFuture "http://www.infoq.com/cn/articles/Functional-Style-Callbacks-Using-CompletableFuture")

### 并发与并行
  Java7 开始，允许将数据集分解为子集，每个子集可以由独立且同质的子任务来负责处理（意思就是说，可以将大的数据集分解成很多子集，然后每个子集由不同的线程处理，线程的处理方式都是一样的）。这种风格的基础库是 **fork/join** 框架，但是不是所有的问题都适合这么处理：所处理的数据集要足够大，每个元素的处理成本要足够高，这样才能补偿建立 fork/join 框架所消耗的成本。（它的本质，是因为问题集是可以分割，逻辑跟顺序无关，然后再将子集合的结果结合，所以这需要新的消耗）

  本文将会探讨CompletableFuture类，有一些系统会依赖于不同类型的异步执行任务，本文将会阐述该类为什么会对这种类型的系统如此重要，并介绍了它是如何补充fork/join风格的并行机制和并行流的。

### 页面渲染器
    // 程序清单1：使用Future等待所有的图片下载完成
	public void renderPage(CharSequence source) {

		List<ImageInfo> info = scanForImageInfo(source);
		//创建Callable，它代表了下载所有的图片
		final Callable<List<ImageData>> task = () -> info.stream().map(ImageInfo::downloadImage).collect(Collectors.toList());
		// 将下载任务提交到executor
		Future<List<ImageData>> images = executor.submit(task);
		// renderText(source);

		try {
		   // 获得所有下载的图片（在所有图片可用之前会一直阻塞）
		   final List<ImageData> imageDatas = images.get();
		   // 渲染图片
		   imageDatas.forEach(this::renderImage);
		} catch (InterruptedException e) {
		   // 重新维护线程的中断状态
		   Thread.currentThread().interrupt();
		   // 我们不需要结果，所以取消任务
		   images.cancel(true);
		} catch (ExecutionException e) {
		  throw launderThrowable(e.getCause()); 
		}
	}

  当文本渲染 renderText 好之后，就调用 Future.get 方法，这个方法会一直阻塞知道所有图片下载好。这样在所有图片下载好之前，一张图片都渲染不了。程序清单 2 用 CompletionService 对该问题做了下优化。 

	// 程序清单2：借助CompletionService，当图片可用时立即将其渲染出来（为了保持简洁性，省略掉了中断和错误处理的代码）
	public void renderPage(CharSequence source) { 
	   List<ImageInfo> info = scanForImageInfo(source); 
	   CompletionService<ImageData> completionService = 
	     new ExecutorCompletionService<>(executor); 
	
	   // 将每个下载任务提交到completion service中
	   info.forEach(imageInfo -> completionService.submit(imageInfo::downloadImage)); 
	
	   renderText(source); 
	
	   // 当每个RunnableFuture可用时（并且我们也准备处理它的时候），
	   // 将它们检索出来 
	   for (int t = 0; t < info.size(); t++) { 
	     Future<ImageData> imageFuture = completionService.take(); 
	     renderImage(imageFuture.get()); 
	   } 
	 }

### CompletableFuture简介
  程序清单2代表了Java 5所能达到的水准，不过2014年之后，在Java中，编写异步系统的表现性得到了巨大的提升，这是通过引入CompletableFuture (CF)类实现的。

  与很多其他的 **CompletableFuture (CF)** 方法类似，thenAccept有两个变种形式，在第一个中，Consumer会由通用fork/join池中的某一个线程来执行；在第二个中，它会由Executor中的某一个线程来负责执行，而Executor是我们在调用时提供的。这形成了三种重载形式：同步运行、在ForkJoinPool中异步运行以及在调用时所提供的线程池中异步运行，CompletableFuture中有近60个方法，上述的这三种重载形式占了绝大多数。

	// 程序清单3：使用CompletableFuture来实现页面渲染功能
	public void renderPage(CharSequence source) { 
	        List<ImageInfo> info = scanForImageInfo(source); 
	        info.forEach(imageInfo -> CompletableFuture.supplyAsync(imageInfo::downloadImage).thenAccept(this::renderImage)); 
	        renderText(source); 
	 }

  第一次看，有点懵，自己先写一个更加简单明了的例子，然后再来看上面的例子

	Consumer<Integer> consumer = num -> {
        CompletableFuture.supplyAsync(new Supplier<Object>() {
            @Override
            public Object get() {
                return num * 2;
            }
        }).thenAccept(new Consumer<Object>() {
            @Override
            public void accept(Object o) {
                System.out.println(o);
            }
        });
    };
	
    List<Integer> list = Arrays.asList(1,2,3);
    list.forEach(consumer);

  结合关键字的意思，更好理解，Supplier（供应商）Consumer（顾客）。num 作为参数（原料）通过 Supplier 进行加工，然后把加工好的产品传给 Consumer。加工这个过程是异步的，有了这个作为例子，理解清单3就更容易了。info 作为原料（地址）给 supplyAsync 中的 Supplier 加工（下载图片），然后将结果（下载好的图片）进行渲染。

  CompletableFuture.supplyAsync 可以指定 Executor。就是上面说的，thenAccept 有两个变种形式。