---
title: "pybiotk：把四年的生信脚本攒成一个工具包"
date: 2026-11-01
categories: ["生信", "python"]
tags: ["pybiotk", "造轮子", "GTF", "BAM", "RNA-seq"]
description: "gtf 转 bed、统计 fragment 长度、表格按列去重……这些当年写在博客里的轮子，后来都被收进了 pybiotk。现在它有 30 个命令行工具，pip 一行就能装。"
cover: /assets/img/bg5.jpg
---

2021 年这个博客刚开张的时候，我写过几个"轮子"：[gtf 转 bed](/posts/gtf-tools/)、[统计 bam 文件的 fragment 长度](/posts/bam-fragment-length/)、[表格按指定列去重再合并](/posts/python-merge-rows/)。写完就散落在各个文件夹里，下次要用还得先翻半天，翻到了还得想起来它要什么参数。

后来实在受不了，2022 年干脆把它们收拢成一个 Python 包，这就是 [pybiotk](https://github.com/liqiming-whu/pybiotk)。四年下来攒了 200 多次提交，现在是 1.3.7 版，装好之后有 30 个命令行工具，也能当 Python 库直接 import。

这篇挑几个最常用的介绍一下。

## 安装

已经发布到 PyPI，一行搞定：

```bash
pip install pybiotk
```

依赖里有 pysam 和 pyBigWig，在 Linux 上装最省心。想用最新代码的话，从 GitHub 或 Gitee clone 下来 `pip install .` 也行。

装好以后先敲一下：

```bash
pybiotk
```

它会列出所有已安装的命令和一句话说明。这个列表直接读取包的元数据，以后加了新工具也不用手动维护文档，再也不会出现"我是不是写过这个功能"的灵魂拷问。

## 格式转换：gtf2bed

当年那篇 gtf 转 bed 的文章，又是下 ucsc 的老软件，又是 conda 装 bedops，最后还要用 bedtools 减出 intron。现在一条命令就够了：

```bash
# 转录本 BED12，用 transcript_id 当名字
gtf2bed genes.gtf --outfmt bed12 --name transcript_id > transcripts.bed12

# 基因层面的 BED6，用基因名
gtf2bed genes.gtf --outfmt bed6 --feature gene --name gene_name > genes.bed6

# 直接提取 intron
gtf2bed genes.gtf --outfmt intron --name transcript_id > introns.bed
```

输出格式支持 `bed12`、`bed6`、`intron`、`gene_info`、`trans_info`，还能按基因类型、转录本类型、ID 或名字过滤。输入输出都支持管道，`zcat genes.gtf.gz | gtf2bed --outfmt bed12` 这种写法完全没问题。

## 给比对结果做注释：pyanno

拿到一堆 peak 或 reads，第一个问题往往是：它们落在基因的哪儿？`pyanno` 就是干这个的。输入 BAM 或 BED，配一个 GTF，输出每条记录的注释类别（TSS、上游、外显子、内含子、CDS、起始/终止密码子、TES、下游、基因间区）、所在基因的坐标、名字、ID 和类型。

```bash
# 注释 BED 区间，考虑链方向，自定义 TSS 区域和下游范围
pyanno -i regions.bed6 -g genes.gtf -o regions.annotation.tsv \
  --strand --tss_region -3000 0 --downstream 3000
```

对双端 RNA-seq，还可以按 fragment 而不是单条 read 来注释：

```bash
pyanno -i aligned.name_sorted.bam -g genes.gtf \
  -o fragments.annotation.tsv \
  --level gene --pair --ordered_by_name --strand \
  --rule '1+-,1-+,2++,2--'
```

最后那个 `--rule` 是什么？看下一节。

## 先搞清楚建库方式：infer_experiment

拿到别人的测序数据，最怕的就是不知道它是不是链特异性的、reads 和基因是同向还是反向。猜错了，后面的定量和注释全白干。

`infer_experiment` 会从 BAM 里抽一部分比对结果（默认 20 万条），对照 GTF 判断这是单端还是双端，以及哪种链规则最能解释这些比对，思路参考了 RSeQC 的同名工具：

```bash
infer_experiment aligned.bam -g genes.gtf --mapq 30
```

它报出来的规则（比如 `1+-,1-+,2++,2--`）可以直接填进 `pyanno --rule`，省得自己对着说明书推。

## 那些当年的轮子，后来怎么样了

- **fragment 长度**：当年那个"不愧是 python，就是慢"的脚本，现在是 `rna_fragment_size`，自动识别单端还是双端，name-sorted 的 BAM 可以边读边算。
- **表格按列去重**：`merge-rows` 那篇文章里的脚本变成了 `merge_row`，按指定列去重，其他列合并、求和、求均值都还在。
- **基因组取序列**：`genomefetcher` 可以按坐标取一段序列，也可以按 GTF 批量取外显子、内含子、5′UTR、3′UTR、CDS 等区域。

```bash
genomefetcher -f genome.fa -l 'chr1:100000-101000(+)' -o region.fa
```

## 几个新写的小工具

**fastq_uniq**：按序列去除重复 reads，支持单端和双端。默认不把整条序列存在内存里，而是存 128 位的 BLAKE2b 摘要，大文件也不至于把内存撑爆；需要绝对精确的比较时，加 `--key-mode exact`。

```bash
fastq_uniq R1.fq.gz R2.fq.gz \
  -o R1.unique.fq.gz R2.unique.fq.gz \
  --key-mode digest --gzip-level 4
```

**fastx_rename**：把 reads 改成 `read_1`、`read_2` 这样的短名字，双端模式下保证两端名字一一对应，多个 lane 的文件按顺序接着编号。

**bed2bedgraph**：BED 转 bedGraph 覆盖度。1.3.6 版把它重写成了区间端点扫描，不再一个碱基一个碱基地展开，未排序、压缩、多个文件的输入都能直接吃。

## 当作 Python 库用

命令行之外，各种格式的读写也能直接在代码里用。比如读 GTF、只看某个基因的外显子：

```python
from pybiotk.io import GtfFile

with GtfFile("genes.gtf") as gtf:
    for exon in gtf.iter_exon(gene_names=["TP53"]):
        print(exon.transcript_id(), exon.start, exon.end, exon.strand)
```

BAM、BED、FASTA、FASTQ、bigWig 都有对应的模块，在 `pybiotk.io` 下面。

## 最后

pybiotk 是我读博这几年处理数据时一点点攒出来的，很多工具诞生的原因就一句话：现成的软件差一点点，自己写一个更快。所以它不追求大而全，只求每个工具都把一件小事做好。

如果你也天天跟 BAM、GTF 打交道，欢迎试试：

- GitHub：<https://github.com/liqiming-whu/pybiotk>
- Gitee：<https://gitee.com/liqiming_whu/pybiotk>
- PyPI：<https://pypi.org/project/pybiotk/>

用着有问题，或者觉得哪个功能该有却没有，欢迎提 issue，或者直接给我写邮件。
