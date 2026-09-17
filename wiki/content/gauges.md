---
title: Gauges
topic: Examples
categories: Examples
icon: w98_bar_graph.png
---

# Gauges

Gauges display a single value as a proportion of a maximum. Useful for dashboards and status indicators.

## Syntax

```
::: gauge
title = Status
value = 75
max = 100
label = percent
:::
```

## Example: Factory Metrics

::: gauge
title = Overall Efficiency
value = 87
max = 100
label = percent
:::

::: gauge
title = Furnace Temperature
value = 1240
max = 1500
label = degrees C
:::

## Example: Resource Levels

::: gauge
title = Coal Reserve
value = 65
max = 100
label = capacity
:::

::: gauge
title = Water Supply
value = 42
max = 100
label = capacity
:::

## Example: Machine Health

::: gauge
title = Drill Integrity
value = 93
max = 100
label = percent
:::

::: gauge
title = Conveyor Wear
value = 31
max = 100
label = percent
:::
