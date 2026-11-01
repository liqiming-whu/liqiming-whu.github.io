---
title: "gtf转bed，提取intron.bed以及一个处理gtf的轮子"
date: 2021-04-06
categories: ["python", "生信入门"]
tags: ["原创", "生信"]
description: "如果你只需要把gtf转成bed12，下载ucsc的两个软件genePredToBed，gtfToGenePred一行代码就完事了。如果你想看看怎么用python实现它，可以看看这个。"
cover: /assets/img/bg4.jpg
---

## 把gtf文件转成bed12文件

bioconda上的ucsc软件都是几万年前的老版本，所以最好直接去[ucsc](http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/%EF%BC%89)下载：

```bash
wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/gtfToGenePred
wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/genePredToBed
chmod +x genePredToBed gtfToGenePred
```

然后：

```bash
./gtfToGenePred gencode.v32.annotation.gtf hg38.genePhred && ./genePredToBed hg38.genePhred hg38.bed12 && rm hg38.genePhred 
```

## 把gtf文件转成bed6文件

我们需要两个软件，用conda装就完事了，也可以clone源码安装最新版。

```bash
conda install -c bioconda bedtools bedops
```

### gtf转gene.bed

```bash
awk '{if($3=="gene")print $0" transcript_id \"\";"}' gencode.v32.annotation.gtf | convert2bed -i gtf | cut -f1-6 > hg38.gene.bed
```

也可以不装bedops，会稍微麻烦一点：

```bash
awk -v OFS="\t" '{if($3=="gene"){match($0,/gene_id "(\S*)"/,a);print $1,$4-1,$5,a[1],$6,$7}}' gencode.v32.annotation.gtf > hg38.gene.bed
```

可以把这两种方法的结果用sort排序生成bed1和bed2，然后用`diff bed1 bed2`检查一下是不是一样的。

### gtf转transcript.bed

gtf转transcript不能用convert2bed了，convert2bed转出来的第4列是gene_id，我们要的是transcript_id。

```bash
awk -v OFS="\t" '{if($3=="transcript"){match($0,/transcript_id "(\S*)"/,a);print $1,$4-1,$5,a[1],$6,$7}}' gencode.v32.annotation.gtf > hg38.transcript.bed
```

### gtf转exon.bed

严格来说，exon和intron是transcript的基本单位，第4列要用transcript_id。

```bash
awk -v OFS="\t" '{if($3=="exon"){match($0,/transcript_id "(\S*)"/,a);print $1,$4-1,$5,a[1],$6,$7}}' gencode.v32.annotation.gtf > hg38.exon.bed
```

### gtf转intron.bed

gtf注释中不含intron，不过我们用bedtools从transcript里面减去exon，剩下的就是intron，也可以直接取bed12的前6列作为transcript。

但是不能直接取差集，为什么呢？因为bedtools只会根据前3列和strand列取差集，不会管第4列的transcipt_id。

不同的transcript之间的exon不能相减，因为有可变剪接，在这个transcript里面的exon可能在另一个transcript里面就不一定是exon了。

网上有教程在直接取差集出错了不仔细思考原因，居然还把transcript和exon合并再取差集，我笑了，你到底懂不懂什么是transcript啊，你知不知道为什么ucsc的bed12文件第四列为什么是transcript_id啊？

但是我们还是能用bedtools，只要把bed6第1列和第4列颠倒就行了

```bash
awk -v OFS="\t" '{print $4,$2,$3,$1,$5,$6}' hg38.transcript.bed > transcript.reverse.bed && \
awk -v OFS="\t" '{print $4,$2,$3,$1,$5,$6}' hg38.exon.bed > exon.reverse.bed && \
bedtools subtract -a transcript.reverse.bed -b exon.reverse.bed -s | awk -v OFS="\t" '{print $4,$2,$3,$1,$5,$6}' > hg38.intron.bed && \
rm transcript.reverse.bed exon.reverse.bed
```

---

把上面的代码合在一起，写在一个脚本gtfparser.sh里面：

```bash
#！/bin/sh
GTF=$1
PREFIX=$2
awk -v OFS="\t" '{if($3=="gene"){match($0,/gene_id "(\S*)"/,a);print $1,$4-1,$5,a[1],$6,$7}}' $GTF > $PREFIX.gene.bed
awk -v OFS="\t" '{if($3=="transcript"){match($0,/transcript_id "(\S*)"/,a);print $1,$4-1,$5,a[1],$6,$7}}' $GTF > $PREFIX.transcript.bed
awk -v OFS="\t" '{if($3=="exon"){match($0,/transcript_id "(\S*)"/,a);print $1,$4-1,$5,a[1],$6,$7}}' $GTF > $PREFIX.exon.bed
awk -v OFS="\t" '{print $4,$2,$3,$1,$5,$6}' $PREFIX.transcript.bed > transcript.reverse.bed && \
awk -v OFS="\t" '{print $4,$2,$3,$1,$5,$6}' $PREFIX.exon.bed > exon.reverse.bed && \
bedtools subtract -a transcript.reverse.bed -b exon.reverse.bed -s | awk -v OFS="\t" '{print $4,$2,$3,$1,$5,$6}' > $PREFIX.intron.bed && \
rm transcript.reverse.bed exon.reverse.bed
```

跑起来：

```bash
chmod +x gtfparser.sh
./gtfparser.sh gencode.v32.annotation.gtf hg38
```

所以说convert2bed其实没啥用~

~~好了，就完了，下面的不用看了~~

---

## 一个还行的轮子：gtfparser.py

### 使用方法

```bash
python gtfparser.py 参数
# 或者
chmod +x gtfparse.py
./gtfparser.py 参数
```

### gtf转bed12

这个很简单：

```bash
./gtfparser.py gencode.v32.annotation.gtf > hg38.bed12
```

### gtf转gene.bed6

```bash
./gtfparser.py gencode.v32.annotation.gtf --attribute gene_id --type gene --format bed6 > hg38.gene.bed
```

### gtf转exon.bed

```bash
./gtfparser.py gencode.v32.annotation.gtf --attribute gene_id --type exon --format bed6 > hg38.exon.bed
```

### gtf转intron.bed

```bash
./gtfparser.py gencode.v32.annotation.gtf --attribute transcript_id --type exon --format intron > hg38.intron.bed
```

### 提取gene_info

```bash
./gtfparser.py gencode.v32.annotation.gtf --attribute gene_id --type gene --format info > hg38.gene_info.tsv
```

### 提取transcript_info

```bash
./gtfparser.py gencode.v32.annotation.gtf --attribute transcript_id --type transcript --format info > hg38.transcript_info
```

---

### gtfparser.py代码如下

```python
#!/usr/bin/env python3
"""
Convert GTF to bed12, bed6, intron and etc..
Author: liqiming@whu.edu.cn
"""
import re
import argparse
from itertools import groupby

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

def parse_attributes(term, attributes):
    parse_attr = re.compile('{term} "([^"]+)"'.format(term=term))
    patterns = parse_attr.findall(attributes)

    if patterns:
        return patterns[0]
    else:
        return 'NA'

class Alias:
    def __init__(self, data):
        self.data = data

    def update(self, data):
        self.data = data

    def __repr__(self):
        return str(self.data)

    __str__ = __repr__

class TransInfo:
    """Get transcript info"""
    __slots__ = ["transcript_id", "transcript_name", "transcript_type",
                 "gene_id", "gene_name", "gene_type", "strand"]

    def __init__(self, gtf, attr):
        self.strand = gtf.strand
        attributes = gtf.attributes
        self.transcript_id = attr
        self.transcript_name = parse_attributes("transcript_name", attributes)
        self.transcript_type = parse_attributes("transcript_type", attributes)
        self.gene_id = parse_attributes("gene_id", attributes)
        self.gene_name = parse_attributes("gene_name", attributes)
        self.gene_type = parse_attributes("gene_type", attributes)

    def __repr__(self):
        return "Transcript({transcript_id} {transcript_type} {strand})".format(
            transcript_id=self.transcript_id,
            transcript_type=self.transcript_type,
            strand=self.strand
            )

    def __str__(self):
        return "\t".join(str(getattr(self, s)) for s in self.__slots__)

class GeneInfo:
    """Get gene info"""
    __slots__ = ["gene_id", "gene_name", "gene_type", "strand"]

    def __init__(self, gtf, attr):
        self.strand = gtf.strand
        attributes = gtf.attributes
        self.gene_id = attr
        self.gene_name = parse_attributes("gene_name", attributes)
        self.gene_type = parse_attributes("gene_type", attributes)

    def __repr__(self):
        return "Gene({gene_id} {gene_type} {strand})".format(
            gene_id=self.gene_id,
            gene_type=self.gene_type,
            strand=self.strand
            )

    def __str__(self):
        return "\t".join(str(getattr(self, s)) for s in self.__slots__)

class Bed6:
    """Convert GTF to Bed6."""
    __slots__ = ["chrom", "start", "end", "name", "score", "strand"]

    def __init__(self, gtf, attr):
        self.chrom = gtf.chrom
        self.start = gtf.start - 1
        self.end = gtf.end
        self.name = attr
        self.score = gtf.score
        self.strand = gtf.strand

    def __repr__(self):
        return "Bed6({chrom}:{start}-{end})".format(
            chrom=self.chrom, start=self.start, end=self.end)

    def __str__(self):
        return "\t".join(str(getattr(self, s)) for s in self.__slots__)

class Bed12:
    """Convert GTF to Bed12."""
    __slots__ = ["chrom", "start", "end", "name", "score", "strand",
                 "thickStart", "thickEnd", "itemRgb", "blockCount",
                 "blockSizes", "blockStarts"]

    def __init__(self, gtf, attr, thickStart, thickEnd):
        self.chrom = gtf.chrom
        self.start = gtf.start - 1
        self.end = Alias(gtf.end)
        self.name = attr
        self.score = 0 if gtf.score == '.' else int(gtf.score)
        self.strand = gtf.strand
        if thickStart and thickEnd:
            self.thickStart = thickStart
            self.thickEnd = thickEnd
        else:
            self.thickStart = self.end
            self.thickEnd = self.end
        self.itemRgb = 0
        self.blockCount = 1
        self.blockSizes = "{size},".format(size=gtf.end - gtf.start + 1)
        self.blockStarts = "{start},".format(start=0)

    def __repr__(self):
        return "Bed12({chrom}:{start}-{end})".format(
            chrom=self.chrom, start=self.start, end=self.end)

    def __str__(self):
        return "\t".join(str(getattr(self, s)) for s in self.__slots__)

    def add_exon(self, gtf):
        self.end.update(gtf.end)
        self.blockSizes += "{size},".format(size=gtf.end - gtf.start + 1)
        self.blockStarts += "{start},".format(start=gtf.start - 1 - self.start)
        self.blockCount += 1

class Intron:
    """Convert GTF to Intron Bed6."""
    __slots__ = ["chrom", "start", "end", "name", "score", "strand"]

    def __init__(self, exon_1, exon_2, attr):
        self.chrom = exon_1.chrom
        self.start = exon_1.end
        self.end = exon_2.start - 1
        assert self.end >= self.start
        self.name = attr
        self.score = '.'
        self.strand = exon_1.strand

    def __repr__(self):
        return "Intron({chrom}:{start}-{end})".format(
            chrom=self.chrom, start=self.start, end=self.end)

    def __str__(self):
        return "\t".join(str(getattr(self, s)) for s in self.__slots__)

class GTF:
    __slots__ = ['seqname', 'source', 'feature', 'start', 'end', 'score',
                 'strand', 'frame', 'attributes', 'chrom']

    def __init__(self, args):
        for s, v in zip(self.__slots__[:9], args):
            setattr(self, s, v)
        self.start = int(self.start)
        self.end = int(self.end)
        self.chrom = self.seqname

    def __repr__(self):
        return "GTF({seqname}:{start}-{end})".format(
            seqname=self.seqname, start=self.start, end=self.end)

def main(gtf, attribute_id, feature, outformat):
    assert outformat in (
        "bed12", "bed6", "intron", "info"
        ), "output file format: {} not support.".format(outformat)
    parse_attr = re.compile(
        '{attribute_id} "([^"]+)"'.format(attribute_id=attribute_id))
    if outformat == 'bed12':
        cds = dict()
        for k, group in groupby(
            reader(
                gtf,
                header=GTF,
                skip_while=lambda toks: toks[0].startswith("#") or not (
                    toks[2] == 'CDS' or toks[2] == 'stop_codon')
                ),
            lambda x: parse_attr.findall(x.attributes)[0]
        ):
            gtfs = list(sorted(group, key=lambda gtf: gtf.start))
            thickStart = gtfs[0].start - 1
            thickEnd = gtfs[-1].end
            cds[k] = (thickStart, thickEnd)
    if outformat == 'info':
        if attribute_id == 'transcript_id':
            head = ["transcript_id", "transcript_name", "transcript_type",
                    "gene_id", "gene_name", "gene_type", "strand"]
            print("\t".join(head))
        elif attribute_id == 'gene_id':
            head = ["gene_id", "gene_name", "gene_type", "strand"]
            print("\t".join(head))
        else:
            raise Exception("GTF attribute and outformat not support.")

    for k, group in groupby(
        reader(
            gtf,
            header=GTF,
            skip_while=lambda toks: toks[0].startswith("#") or not (
                toks[2] == feature)
            ),
        lambda x: parse_attr.findall(x.attributes)[0]
    ):
        # loop over the group building the single bed12 line
        if outformat == 'bed12':
            bed = None
            for gtf_entry in sorted(group, key=lambda gtf: gtf.start):
                if not bed:
                    try:
                        thickStart, thickEnd = cds[k]
                    except Exception:
                        thickStart = thickEnd = None
                    bed = Bed12(gtf_entry, k, thickStart, thickEnd)
                else:
                    bed.add_exon(gtf_entry)
            print(bed)
        elif outformat == 'bed6':
            for gtf_entry in group:
                bed = Bed6(gtf_entry, k)
                print(bed)
        elif outformat == 'intron':
            exons = []
            for gtf_entry in sorted(group, key=lambda gtf: gtf.start):
                exons.append(gtf_entry)
            assert len(exons) > 0
            if len(exons) < 2:
                continue
            for i in range(len(exons) - 1):
                intron = Intron(exons[i], exons[i+1], k)
                print(intron)

        elif outformat == 'info' and attribute_id == 'transcript_id':
            for gtf_entry in group:
                transcript_info = TransInfo(gtf_entry, k)
                print(transcript_info)

        elif outformat == 'info' and attribute_id == 'gene_id':
            for gtf_entry in group:
                gene_info = GeneInfo(gtf_entry, k)
                print(gene_info)

if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('gtf', help="gtf file download from Genecode.")
    p.add_argument('--attribute', dest='attr', default='transcript_id', help="""
    attribute ID by which to group bed entries.
    'gene_id' or 'gene_name' for gene.bed6, gene_info
    'transcript_id' for genome.bed12, exon, intron, transcrpt_info
    """)
    p.add_argument('--type', dest='feature', default='exon', help="""
    annotation type to join, all others are filtered out:
    'exon' genome.bed12, exon, intron, 'gene' for gene.bed6, gene_info,
    'transcript' for transcript_info.
    """)
    p.add_argument('--format', dest='outformat', default='bed12', help="""
    choose output file format:bed12, bed6, intron, info
    """)
    args = p.parse_args()
    main(args.gtf, args.attr, args.feature, args.outformat)
```
