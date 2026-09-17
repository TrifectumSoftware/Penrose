---
title: Colored Tables
topic: Examples
categories: Examples
icon: w98_bar_graph.png
---

# Colored Tables

Tables support colored rows using a comment directive placed before each row.

## Syntax

Place a `<!-- rowclass:colorname -->` comment before the row you want to color:

```
<!-- rowclass:blue -->
| Resource | Amount |
| -------- | ------ |
| Coal | 100 |
<!-- rowclass:green -->
| Iron | 75 |
<!-- rowclass:red -->
| Copper | 50 |
```

## Available Colors

blue, red, green, yellow, orange, purple, cyan, grey

## Example: Resource Inventory

| Resource | Stock | Capacity | Status |
| -------- | ----- | -------- | ------ |
<!-- rowclass:green -->
| Coal | 2400 | 3000 | Good |
<!-- rowclass:blue -->
| Iron ore | 1800 | 3000 | Good |
<!-- rowclass:yellow -->
| Copper ore | 900 | 3000 | Low |
<!-- rowclass:red -->
| Stone | 200 | 3000 | Critical |

## Example: Production Status

| Machine | Output/hr | Efficiency | Status |
| ------- | --------- | ---------- | ------ |
<!-- rowclass:green -->
| Drill #1 | 120 units | 98% | Running |
<!-- rowclass:blue -->
| Drill #2 | 115 units | 94% | Running |
<!-- rowclass:orange -->
| Furnace A | 80 units | 72% | Low fuel |
<!-- rowclass:red -->
| Furnace B | 0 units | 0% | Offline |

## Example: Color Reference

| Color | Class | Use Case |
| ----- | ----- | -------- |
<!-- rowclass:blue -->
| Blue | `blue` | Information, neutral data |
<!-- rowclass:green -->
| Green | `green` | Success, good status |
<!-- rowclass:yellow -->
| Yellow | `yellow` | Warning, low values |
<!-- rowclass:red -->
| Red | `red` | Error, critical alerts |
<!-- rowclass:orange -->
| Orange | `orange` | Caution, moderate concern |
<!-- rowclass:purple -->
| Purple | `purple` | Special, highlighted items |
<!-- rowclass:cyan -->
| Cyan | `cyan` | Alternative neutral |
<!-- rowclass:grey -->
| Grey | `grey` | Inactive, disabled |
