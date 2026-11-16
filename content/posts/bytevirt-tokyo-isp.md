---
title: "ByteVirt 东京 ISP 小鸡：一台对得起价格的落地机"
date: 2026-11-16
categories: ["终端与环境"]
tags: ["VPS", "评测"]
description: "25 刀一季，512M 内存，IIJ 的原生 IP。两家检测站一家说住宅一家说机房，机房是真的。没有中国优化，电信访问倒还稳，当落地机正合适。"
cover: /assets/img/bg4.jpg
---

昨天在 ByteVirt 买了一台东京的 ISP VPS，型号 VPS-512-KVM-ISP-JP。用了一天，把配置、IP 检测结果和实际用法记一下。纯个人向，只测了我自己关心的那几项。

## 配置和价格

![ByteVirt 的 VPS-512-KVM-ISP-JP 套餐页：25 美元每季，1 核、512 MB 内存、15 GB SSD、每月 500 GB 流量 300 Mbps](/assets/img/posts/bytevirt-tokyo-isp/plan.webp#small "套餐页。底下两行小字比上面的配置更值得看。")

| 项目 | 规格 |
| --- | --- |
| 价格 | 25 美元 / 季 |
| CPU | 1 核（Fair Share） |
| 内存 | 512 MB |
| 硬盘 | 15 GB SSD |
| 流量 | 500 GB / 月，300 Mbps |
| IP | 1 个 IPv4 |
| 机房 | 东京 |
| 快照 / 备份 | 3 个 / 1 个 |

折下来一个月八美元多。单看配置不便宜，同样的钱能买到内存大好几倍的机器。这台的钱是花在 IP 上的。

套餐页底下有两行小字：

- 流量用完以后限速到 1 Mbps。
- 80、443、3389 端口可能被封。

第二条的意思是别指望拿它在标准端口上建站。我不建站，所以无所谓。

## IP：两家检测站打架

IP 在 AS2497，也就是 IIJ（Internet Initiative Japan）的段。分别在 IPPure 和 ip.net.coffee 上查了一遍。

![IPPure 的检测结果：AS2497 IIJ，各家地理库都定位在日本，原生 IP，住宅 IP，IPPure 系数 2% 极度纯净，Cloudflare 系数 32% 中性](/assets/img/posts/bytevirt-tokyo-isp/ippure.webp#small "IPPure：原生、住宅、极度纯净。")

![ip.net.coffee 的检测结果：评分 75 良好，日本原生 IP，标记为机房 IP，运营商类型 Hosting，人类流量 18%，未检测到 VPN、代理、Tor](/assets/img/posts/bytevirt-tokyo-isp/netcoffee.webp#small "ip.net.coffee：原生，但是机房。")

两家一致的部分：

- 日本原生 IP，几家地理库都定位在日本。
- 没有滥用记录，没被标成 VPN、代理或者 Tor。
- Cloudflare 系数 32%，中性。

不一致的部分：

| | IPPure | ip.net.coffee |
| --- | --- | --- |
| IP 属性 | 住宅 IP | 机房 IP（Hosting） |
| 人机流量 | 人类 78.69% | 人类 18.0% |
| 综合 | 2%，极度纯净 | 75 分，良好 |

**机房是真的，第二家说得对。** ip.net.coffee 的服务商一栏写的是一家云服务公司，不是 IIJ 自己。这是运营商的地址段租给了云厂商，叫 ISP IP 没问题，但它不是家宽。IPPure 给出住宅，大概是因为 IIJ 本身是运营商。

人机流量比两家差得太远，我两边都不太信。

结论是：原生、干净，但属性上是机房。一般的风控够用，查得细的服务还是认得出来。冲着"住宅 IP"买的话会失望。

## 带宽和线路

标称 300 Mbps，实测下载平均 240 Mbps，给得挺足。

线路没有中国优化。不过我测下来电信访问还是稳的。反正我是拿它当落地机，前面那一段不靠它，有没有优化都无所谓。

要留神的是流量。240 Mbps 跑满，不到五个小时就能把 500 GB 用完，之后就是 1 Mbps。

## 我怎么用的

只跑了一个轻量服务，开了 BBR。装完还剩 250 MB 左右的内存，512 MB 跑这一个服务很宽裕。

![客户端里的当前节点卡片：节点名南极洲，延迟 66 ms](/assets/img/posts/bytevirt-tokyo-isp/antarctica.webp#small "当前节点：南极洲，66 ms。企鹅那边应该是已经用上量子通信了。")

再多的东西就别往上堆了，这个内存也堆不动。

## 值不值

对得起它的价格，也就到这儿。

- 好的地方：IIJ 原生段，记录干净，带宽给足，内存够跑一个落地服务。
- 一般的地方：配置按价格算偏贵，流量只有 500 GB，机房属性摆在那儿。
- 要知道的坑：80/443/3389 可能被封，超流量限速到 1 Mbps，没有中国优化。

想要一个干净的日本原生 IP 做落地，不建站、流量用得不多，这台合适。想要真家宽，或者想直连又要线路好，那就不是它。
