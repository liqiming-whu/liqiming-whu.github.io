---
title: "python按长度拆分容器"
date: 2021-04-14
categories: ["python"]
tags: ["小技巧"]
description: "一个python烂活，输入任意长度列表，根据长度列表对容器进行拆分。"
cover: /assets/img/bg2.jpg
---

## 输入任意长度列表，拆分容器或者有限迭代器。

假设有这样一个列表`[1,2,2,3,3,3,4,4,4,4,5,5,5,5,5]`，现在输入一个度列表`[1,2,3,4,5]`，把列表按长度依次拆分。

代码如下：

```python
def slice_by_len(length_list, container):
    container = list(container)
    container_len = len(container)
    length_sum = sum(length_list)
    if container_len > length_sum:
        length_list.append(container_len - length_sum)
    for i, length in enumerate(length_list):
        start = sum(length_list[:i])
        end = start + length
        block = container[start:end]
        if block:
            results.append(block)
    return results
```

测试：

```python
>>> a = [1,2,2,3,3,3,4,4,4,4,5,5,5,5,5]
>>> slice_by_len([1,2,3,4,5], a)
[[1], [2, 2], [3, 3, 3], [4, 4, 4, 4], [5, 5, 5, 5, 5]]
>>> slice_by_len([1,2,3,4,10], a)
[[1], [2, 2], [3, 3, 3], [4, 4, 4, 4], [5, 5, 5, 5, 5]]
>>> slice_by_len([1,2,3,4], a)
[[1], [2, 2], [3, 3, 3], [4, 4, 4, 4], [5, 5, 5, 5, 5]]
>>> slice_by_len([1,2,3,3], a)
[[1], [2, 2], [3, 3, 3], [4, 4, 4], [4, 5, 5, 5, 5, 5]]
>>> slice_by_len([1,2,3,100,1000], a)
[[1], [2, 2], [3, 3, 3], [4, 4, 4, 4, 5, 5, 5, 5, 5]]
>>> slice_by_len([1,2,3,3,3,3,3,3,8,9], a)
[[1], [2, 2], [3, 3, 3], [4, 4, 4], [4, 5, 5], [5, 5, 5]]
```
