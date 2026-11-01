---
title: "统计bam文件中的fragments长度分布"
date: 2021-04-16
categories: ["python", "生信入门"]
tags: ["原创", "生信"]
description: "输入bam文件，输出两列，一列是fragment的长度，一列是数量。不愧是python，就是慢。"
cover: /assets/img/bg.jpg
---

[RSeQC](https://github.com/MonashBioinformaticsPlatform/RSeQC)的[RNA_fragment_size.py](https://github.com/MonashBioinformaticsPlatform/RSeQC/blob/master/rseqc/modules/RNA_fragment_size.py)虽然可以统计fragments的长度，但只能输出每个比对到每个转录本的片段的均值，中位数等信息：

> `calculate fragment size for each gene/transcript. For each transcript/gene, it Will report:`  
> `1) # of fragment that was used.`  
> `2) mean of fragment size`  
> `3) median of fragment size`  
> `4) stdev of fragment size`

所以我参考它造了一个轮子，按照每个基因的一个转录本来统计所有的fragment长度，方便生成fragment长度分布图。

原理：根据read1和read2比对到基因组上的坐标，统计该区域包含的exon长度之和。当read1和read2没有overlap，且在一个转录本上比对到了两个很远的位置，它们中间的所有exon都会被统计进去，这时候fragment长度就会很长。但这种pair reads比较少，可以设置一个阈值去掉比例比较低的fragment。

因为python和双重循环的原因，会比较慢，需要几个小时。

### 使用方法：

```shell
usage: fragment_sizes.py [-h] -i INPUT_FILE [-o OUTPUT_FILE] -r REFGENE_BED -g
                         GTF_FILE [-m FILTER_METHOD] [-q MAP_QUAL]
                         [-n FRAGMENT_NUM] [-b FILTERED_BED] [-f FILTERED_GTF]
                         [-t TEMP_FILE]

Calculate fragment sizes for mapped bam file. Author: liqiming@whu.edu.cn

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input INPUT_FILE
                        Input BAM file (default: None)
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Output file (default: None)
  -r REFGENE_BED, --refgene REFGENE_BED
                        Reference gene model in BED format. Must be strandard
                        12-column BED file. [required] (default: None)
  -g GTF_FILE, --gtf GTF_FILE
                        Reference gene model in GTF format. Used to filter
                        12-column transcipt BED. [required] (default: None)
  -m FILTER_METHOD, --method FILTER_METHOD
                        Method to maintain transcipt when filtering 12-column
                        transcipt BED. [first|last|max_len|min_len] (default:
                        first)
  -q MAP_QUAL, --mapq MAP_QUAL
                        Minimum mapping quality (phred scaled) for an
                        alignment to be called "uniquely mapped" (default: 30)
  -n FRAGMENT_NUM, --frag-num FRAGMENT_NUM
                        Minimum number of fragment (default: 1)
  -b FILTERED_BED, --bed_filtered FILTERED_BED
                        Output file to store filtered 12-column transcipt BED
                        (default: /dev/null)
  -f FILTERED_GTF, --filtered_gtf FILTERED_GTF
                        Output file to store filtered GTF file, support *.gz
                        (default: /dev/null)
  -t TEMP_FILE, --temp TEMP_FILE
                        Output file to store processing data, support *.gz
                        (default: /dev/null)
```

讲人话就是：

```shell
./fragment_sizes.py -i $bam文件 -r $bed12文件 -g $gtf文件 -m $筛选方式 -b $筛选后的bed12 -f $筛选后的gtf -o $输出文件 -t $缓存文件
```

-i输入比对得到的bam文件，必须用samtools建立索引。

-r输入bed12文件，每一行是一个transcript。

-g基因组注释文件gtf。

-m筛选方式。每个基因的区域会有多个转录本，为了避免一个fragment在同一个基因上按不同转录本统计多次，所以必须对转录本进行筛选，每个基因保留一个转录本。有4种保留方式`[first|last|max_len|min_len]` 。分别是注释中的第一条，最后一条，最长和最短。

-b输出筛选后的bed12，可选。

-f输出筛选后的gtf，可选。支持gzip压缩格式，后缀加“.gz”就行了。

-o输出文件，可选。不设置这个参数，就会打印到标准输出。

-t缓存文件，可选。每一行一个fragment的长度，支持gzip压缩格式，后缀加“.gz”。

### 源码：

```python
#!/usr/bin/env python3
'''
Calculate fragment sizes for mapped bam file.
Author: liqiming@whu.edu.cn
'''
import os
import re
import sys
import gzip
import pysam
import argparse
import pandas as pd
from itertools import groupby
from collections import Counter

class GTF:
    __slots__ = ['seqname', 'source', 'feature', 'start', 'end', 'score',
                 'strand', 'frame', 'attributes', 'chrom', 'size']

    def __init__(self, args):
        for s, v in zip(self.__slots__[:9], args):
            setattr(self, s, v)
        self.start = int(self.start)
        self.end = int(self.end)
        self.chrom = self.seqname
        self.size = abs(self.end - self.start)

    def __repr__(self):
        return "GTF({seqname}:{start}-{end})".format(
            seqname=self.seqname, start=self.start, end=self.end)

    def __str__(self):
        return "\t".join(str(getattr(self, s)) for s in self.__slots__[:9])

    @property
    def gene_id(self):
        return re.compile('gene_id "([^"]+)"').findall(self.attributes)[0]

    @property
    def transcript_id(self):
        results = re.compile(
            'transcript_id "([^"]+)"').findall(self.attributes)
        if results:
            return results[0]

def reader(fname, header=None, sep="\t", skip_while=None):
    sep = re.compile(sep)
    with open(fname) as f:
        for line in f:
            toks = sep.split(line.rstrip("\r\n"))
            if skip_while:
                if skip_while(toks):
                    continue
            if header:
                yield header(toks)
            else:
                yield toks

def filter_transcript(gtffile, method, filtered_file=os.devnull):
    assert method in (
        "first", "last", "max_len", "min_len"), f"{method} not support"
    transcript_idlist = []
    for _, group in groupby(
        reader(
            gtffile,
            header=GTF,
            skip_while=lambda toks: toks[0].startswith("#") or not (
                toks[2] == "transcript")
        ),
        lambda x: x.gene_id
    ):
        transcript = None
        if method == 'first':
            transcript = list(group)[0]
        elif method == 'last':
            transcript = list(group)[-1]
        elif method == 'max_len':
            transcript = max(group, key=lambda x: x.size)
        else:
            transcript = min(group, key=lambda x: x.size)
        transcript_idlist.append(transcript.transcript_id)
        filtered_file.write(f"{str(transcript)}\n".encode())

    return transcript_idlist

def overlap_length(lst1, lst2):
    l = 0
    for x in lst1:
        for y in lst2:
            l += len(range(max(x[0], y[0]), min(x[-1], y[-1]) + 1))
    return l

def fragment_size(bedfile, samfile, transcript_idlist, qcut=30, ncut=1, filtered_bed=os.devnull, temp=os.devnull):
    '''calculate the fragment size for each gene'''
    for line in open(bedfile, 'r'):
        exon_range = []
        if line.startswith(('#', 'track', 'browser')):
            continue
        fields = line.split()
        chrom = fields[0]
        tx_start = int(fields[1])
        tx_end = int(fields[2])
        geneName = fields[3]
        if geneName not in transcript_idlist:
            continue
        filtered_bed.write(line)
        trand = fields[5].replace(" ", "_")
        exon_starts = map(int, fields[11].rstrip(',\n').split(','))
        exon_starts = map((lambda x: x + tx_start), exon_starts)
        exon_ends = map(int, fields[10].rstrip(',\n').split(','))
        exon_ends = map((lambda x, y: x + y), exon_starts, exon_ends)

        for st, end in zip(exon_starts, exon_ends):
            exon_range.append([st + 1, end + 1])
        try:
            alignedReads = samfile.fetch(chrom, tx_start, tx_end)
        except:
            continue

        frag_sizes = []
        for aligned_read in alignedReads:
            if not aligned_read.is_paired:  # skip single sequencing
                continue
            if aligned_read.is_read2:
                continue
            if aligned_read.mate_is_unmapped:
                continue
            if aligned_read.is_qcfail:
                continue  # skip low quanlity
            if aligned_read.is_duplicate:
                continue  # skip duplicate read
            if aligned_read.is_secondary:
                continue  # skip non primary hit
            if aligned_read.mapq < qcut:
                continue

            read_st = aligned_read.pos
            mate_st = aligned_read.pnext
            if read_st > mate_st:
                (read_st, mate_st) = (mate_st, read_st)
            if read_st < tx_start or mate_st > tx_end:
                continue
            read_len = aligned_read.qlen
            map_range = [[read_st+1, mate_st]]
            frag_len = overlap_length(exon_range, map_range) + read_len
            frag_sizes.append(frag_len)
        if len(frag_sizes) < ncut:
            continue
        else:
            for i in frag_sizes:
                temp.write(f"{i}\n".encode())
                yield i

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", dest="input_file",
                        type=str, required=True, help="Input BAM file")
    parser.add_argument("-o", "--output", dest="output_file",
                        type=str, help="Output file")
    parser.add_argument("-r", "--refgene", dest="refgene_bed", type=str, required=True,
                        help="Reference gene model in BED format. Must be strandard 12-column BED file. [required]")
    parser.add_argument("-g", "--gtf", dest="gtf_file", type=str, required=True,
                        help="Reference gene model in GTF format. Used to filter 12-column transcipt BED. [required]")
    parser.add_argument("-m", "--method", dest="filter_method", type=str, default="first",
                        help="Method to maintain transcipt when filtering 12-column transcipt BED. [first|last|max_len|min_len]")
    parser.add_argument("-q", "--mapq", dest="map_qual", type=int, default=30,
                        help="Minimum mapping quality (phred scaled) for an alignment to be called \"uniquely mapped\"")
    parser.add_argument("-n", "--frag-num", dest="fragment_num", type=int, default=1,
                        help="Minimum number of fragment")
    parser.add_argument("-b", "--bed_filtered", dest="filtered_bed", type=str, default=os.devnull,
                        help="Output file to store filtered 12-column transcipt BED")
    parser.add_argument("-f", "--filtered_gtf", dest="filtered_gtf", type=str, default=os.devnull,
                        help="Output file to store filtered GTF file, support *.gz")
    parser.add_argument("-t", "--temp", dest="temp_file", type=str, default=os.devnull,
                        help="Output file to store processing data, support *.gz")

    args = parser.parse_args()

    if not os.path.exists(args.input_file + '.bai'):
        print >>sys.stderr, "cannot find index file of input BAM file"
        print >>sys.stderr, args.input_file + '.bai' + " does not exists"
        sys.exit(0)

    bed_writer = open(args.filtered_bed, "w")
    gtf_writer = gzip.open(args.filtered_gtf, "wb") if args.filtered_gtf.endswith(
        ".gz") else open(args.filtered_gtf, "wb")
    temp_writer = gzip.open(args.temp_file, "wb") if args.temp_file.endswith(
        ".gz") else open(args.temp_file, "wb")

    transcript_idlist = filter_transcript(
        args.gtf_file, args.filter_method, gtf_writer)
    gtf_writer.close()

    fragment_sizes = Counter(i for i in fragment_size(
        args.refgene_bed,
        pysam.Samfile(args.input_file),
        transcript_idlist,
        args.map_qual,
        args.fragment_num,
        bed_writer,
        temp_writer
    ))
    bed_writer.close()
    temp_writer.close()

    frag_sizes_df = pd.DataFrame(
        {"Length": fragment_sizes.keys(), "Count": fragment_sizes.values()})
    frag_sizes_df.sort_values(by="Length", ascending=True, inplace=True)

    if args.output_file:
        frag_sizes_df.to_csv(args.output_file, sep="\t",
                             header=True, index=False)
    else:
        print("Length\tCount")
        for _, i in frag_sizes_df.iterrows():
            print(i["Length"], i["Count"], sep="\t")
```
