---
title: "python将列表按指定的列去重，并合并其它行的内容"
date: 2021-04-29
categories: ["python"]
tags: ["pandas", "造轮子"]
description: "pandas的drop_duplicates在按某列去重时，其他列每组只能保留其中一行。如何把这一组的若干行合并在一行，是本文主要解决的问题。"
cover: /assets/img/bg9.jpg
---

pandas的去重方法`df.drop_duplicates(subset=keys, keep='first')`在按某列去重时，其他列每组只能保留其中一行。如何想要把这一组的所有内容合并在一行，或者进行简单的统计呢？我造了个轮子，以解决这个问题。

`merge_row.py`可以对指定的列进行去重，并输出指定的其他列合并后的内容，可自定义分隔符。可以对指定的其他列的每组求和，均值，最大值，最小值，中位数等，可以对分组进行去重，可以输出每个分组的数据个数。

输入输出支持`csv`、`tsv`表格和excel表格，使用`.csv`，`.tsv`和`.xlsx`后缀加以区分。

## 使用方法：

```shell
usage: merge_row.py [-h] -i INPATH [-o OUTPATH] [-header HEADER] -by BY [-c COLUMNS] [-m METHOD] [-sep SEP] [-delim DELIM] [-count]

optional arguments:
  -h, --help      show this help message and exit
  -i INPATH       Input table file. [required]. (default: None)
  -o OUTPATH      Output file, discard this parameter to print output to stdout. (default: None)
  -header HEADER  The selected row will be the header, discard this parameter if there is no header, 0 based. (default: None)
  -by BY          The same values in the selected columns will be merged, 0 based, use ',' to separate. [required]. (default: None)
  -c COLUMNS      Other columns selected will be shown in the output, discard this parameter to show all columns, 0 based, use ',' to separate. If an illegal parameter is set, no other columns will be appended to
                  the output table. (default: None)
  -m METHOD       Specify the operation that should be applied to -c. Valid operations: sum, min, max, mean, median, collapse, distinct, first, last, count, count_distinct. use ',' to separate. (default:
                  distinct)
  -sep SEP        Specify a custom delimiter to separate the input file. (default: )
  -delim DELIM    Specify a custom delimiter for the collapse operations. (default: ,)
  -count          Add a count column to the output table. (default: False)
```

在终端执行：

```shell
./merge_row.py -i $输入 -o $输出 -header $表头 -by $哪几列 -c $其它列 -m $统计方法 -sep $输入文件的分隔符 -delim $合并列的分隔符 -count
```

`-i`：输入文件，可以是文本格式文件或`xlsx`格式的excel表格。配合`-sep`指定分隔符，`-header`指定表头。

`-o`：输出文件，不指定`-o`就会把输出打印出来。

`-header`：表头。0表示第0列作为表头，没有表头则不指定该参数。

`-by`：按哪几列去重，`-by 0` 表示按第0列去重，`-by 0,1,2`表示按第0，1，2列去重，用英文逗号分开。

`-c`：除了`-by`指定的列，其它需要输出的列。`-c 4,5,6`输出4，5，6列，不指定-c则输出所有列。指定一个不合法的值则不会输出其它列，如`-c false`。

`-m`：对应`-c`中每一列的统计方式，`-m distinct,distinct,sum`表示对`-c 4,5,6`第4，5列去重然后合并，第6列计算和。单个值`-c distinct`表示对c中所有列都采用`distinct`。默认值`distinct`。选项有：`sum, min, max, mean, median, collapse, distinct, first, last，count, count_distinct`。`count`和`count_distinct`不统计NA。

`-sep`： 输入表格的分隔符，默认为`\t`，对于excel表格不需要指定。

`-delim`：对于-m中的distinct（去重合并）和collapse（直接合并），采用指定的分隔符连接。默认`,`。

`-count`：添加该参数，会在输出最后一列之后添加一列count，表示被合并的行数。

## 代码如下：

```python
#!/usr/bin/env python3
"""
Remove duplicated rows of the table by specified columns and keep the contents of other columns.
Author: liqiming@whu.edu.cn
"""
import sys
import argparse
import pandas as pd

def df_merge_row(df, by=None, columns=None, method="distinct", sep=",", count=False):
    if not columns:
        return df.drop_duplicates(subset=by, keep='first')

    def generate_content(x):
        data = {}
        for c, m in zip(columns, method):
            try:
                series = pd.to_numeric(x[c])
                if m == "mean":
                    data[c] = series.mean()
                elif m == 'medium':
                    data[c] = series.median()
            except ValueError:
                series = x[c]
            if m == 'distinct':
                data[c] = sep.join(map(str, series.unique()))
            elif m == 'collapse':
                data[c] = sep.join(map(str, series))
            elif m == 'max':
                data[c] = series.max()
            elif m == 'min':
                data[c] = series.min()
            elif m == 'sum':
                data[c] = series.sum()
            elif m == 'first':
                data[c] = series.to_list()[0]
            elif m == 'last':
                data[c] = series.to_list()[-1]
            elif m == 'count':
                data[c] = series.count()
            elif m == 'count_distinct':
                data[c] = pd.Series(series.unique()).count()
            else:
                if c not in data:
                    data[c] = sep.join(map(str, series.unique()))
        if count:
            data["count"] = len(x[columns[0]])
        return pd.Series(data)

    merge_df = df.groupby(by).apply(generate_content).reset_index()
    return merge_df

def main(inpath, outpath, header, by, columns=None, method="distinct", sep="\t", delim=",", count=False):
    if inpath.endswith(".xlsx"):
        df = pd.read_excel(inpath, header=header)
    else:
        df = pd.read_csv(inpath, header=header, delimiter=sep)
    by = by.split(",")
    method = method.split(",")
    if columns:
        by_name = [df.columns[int(i)] for i in by]
        columns = columns.split(",")
        if len(method) == 1:
            method = len(columns) * method
        assert len(columns) == len(method)
        try:
            column_name = [df.columns[int(i)] for i in columns if i not in by]
            output_name = [df.columns[int(i)] for i in sorted(by + columns)]
            if count:
                output_name.append("count")
        except Exception:
            column_name = None
            output_name = by_name
    else:
        by_name = [df.columns[int(i)] for i in by]
        column_name = [i for i in df.columns if i not in by_name]
        if len(method) == 1:
            method = len(column_name) * method
        assert len(column_name) == len(method)
        output_name = df.columns.to_list()
        if count:
            output_name.append("count")

    out_df = df_merge_row(df, by_name, column_name, method, delim, count)
    out_df = out_df[output_name]

    out_header = True if header is not None else False
    if outpath:
        if outpath.endswith(".csv"):
            out_df.to_csv(outpath, index=False, header=out_header, sep=",")
        elif outpath.endswith(".xlsx"):
            out_df.to_excel(outpath, index=False, header=out_header)
        else:
            out_df.to_csv(outpath, index=False, header=out_header, sep="\t")
    else:
        if out_header:
            print("\t".join(map(str, out_df.columns)))
        for _, row in out_df.iterrows():
            print("\t".join(map(str, dict(row).values())))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", dest="inpath",
                        type=str, required=True, help="Input table file. [required].")
    parser.add_argument("-o", dest="outpath", type=str,
                        help="Output file, discard this parameter to print output to stdout.")
    parser.add_argument("-header", dest="header", type=int,
                        default=None, help=("The selected row will be the header, "
                                            "discard this parameter if there is no header, 0 based."))
    parser.add_argument("-by", dest="by", type=str, required=True,
                        help="The same values in the selected columns will be merged, 0 based, use ',' to separate. [required].")
    parser.add_argument("-c", dest="columns", type=str, default=None,
                        help=("Other columns selected will be shown in the output, "
                              "discard this parameter to show all columns, 0 based, use ',' to separate. "
                              "If an illegal parameter is set, no other columns will be appended to the output table."))
    parser.add_argument("-m", dest="method", type=str, default="distinct",
                        help=("Specify the operation that should be applied to -c. "
                              "Valid operations: sum, min, max, mean, median, collapse, distinct, first, last, count, count_distinct. "
                              "use ',' to separate."))
    parser.add_argument("-sep", dest="sep", type=str, default="\t",
                        help="Specify a custom delimiter to separate the input file.")
    parser.add_argument("-delim", dest="delim", type=str, default=",",
                        help="Specify a custom delimiter for the collapse operations.")
    parser.add_argument("-count", dest="count", action="store_true",
                        help="Add a count column to the output table.")
    args = parser.parse_args()

    main(**args.__dict__)
```
