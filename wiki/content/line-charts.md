---
title: Line Charts
topic: Examples
icon: w98_bar_graph.png
---

# Line Charts

Line charts plot multiple data series over a sequence. Values are space-separated.

## Syntax

```
::: linechart
title = Time Series
Series A = 10 20 30 25 40
Series B = 5 15 25 35 30
:::
```

## Example: Production Over Time

::: linechart
title = Production Output (units/hr)
Drills = 100 120 140 130 160 155 170
Furnaces = 80 85 90 88 95 100 105
Assemblers = 40 50 60 65 70 75 80
:::

## Example: Resource Depletion

::: linechart
title = Resource Stockpile (tons)
Coal = 500 450 380 310 250 200 160
Iron = 300 290 275 260 240 220 200
:::

## Example: Power Consumption

::: linechart
title = Power Draw (kW) Over 12 Hours
Factory floor = 200 220 240 250 260 255 250 240 230 220 210 200
Research wing = 50 60 80 90 100 110 110 100 90 80 60 50
:::
