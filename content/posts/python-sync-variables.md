---
title: "Python如何让两个变量保持同步"
date: 2021-04-08
categories: ["python"]
tags: ["原创"]
description: "python就这？连个引用都没有。卖课公众号还好意思吹什么无所不能的编程语言呢。就这？"
cover: /assets/img/bg3.jpg
---

众所周知，连Java都有的引用，Python都没有。可谁让我智商低下，学不会C++呢。找了一圈，也没有发现一个优雅地方法去实现这样一个函数：`track(a) = b` ，然后a和b同步改变。

只能用这样丑陋的方式：

```python
class Alias:
    def __init__(self, data):
        self.data = data

    def update(self, data):
        self.data = data

    def __repr__(self):
        return str(self.data)

    __str__ = __repr__
```

然后定义变量a：

```python
a = Alias(1)
>>> a
1
>>>
```

令b=a：

```python
b = a
>>> b
1
>>>
```

更新a:

```python
a.update("Python就这？")
>>> a
Python就这？
>>>
```

b也会同步改变：

```python
>>> b
Python就这？
>>>
```

看完这个，你可能想说：就这？

没错，就这。

我也想对卖Python编程课的公众号说一句：就这？别恶心人啦。
