---
title: Histograms
topic: Examples
categories: Examples
icon: w98_bar_graph.png
---

# Histograms

Histograms show frequency distribution across bins. Use `Label = count` syntax.

## Syntax

```
::: histogram
title = Distribution
Bin 1 = 5
Bin 2 = 12
Bin 3 = 18
:::
```

## Example: Ore Deposit Sizes

::: histogram
title = Ore Deposit Sizes (tons)
10-20 = 3
20-30 = 7
30-40 = 14
40-50 = 22
50-60 = 18
60-70 = 11
70-80 = 6
80-90 = 2
:::

## Example: Machine Output Distribution

::: histogram
title = Hourly Output Distribution
0-20 = 2
20-40 = 5
40-60 = 11
60-80 = 16
80-100 = 13
100-120 = 8
120-140 = 4
140-160 = 1
:::

## Example: Component Failure Rates

::: histogram
title = Component Failures by Age (months)
0-6 = 1
6-12 = 3
12-18 = 7
18-24 = 15
24-30 = 22
30-36 = 19
36-42 = 10
42-48 = 5
:::
