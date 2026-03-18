# Bulma Columns

## Overview
Bulma's column system is powered by Flexbox to create flexible multi-column layouts.

## Basic Usage

```html
<div class="columns">
  <div class="column">First column</div>
  <div class="column">Second column</div>
  <div class="column">Third column</div>
  <div class="column">Fourth column</div>
</div>
```

## Column Classes

### Container
| Class | Description |
|-------|-------------|
| `.columns` | Columns container (flexbox) |
| `.columns.is-mobile` | Force mobile view |

### Column
| Class | Description |
|-------|-------------|
| `.column` | Column item |
| `.is-narrow` | Column takes only necessary width |
| `.is-flexible` | Column takes remaining space |
| `.is-full` | Full width column |
| `.is-four-fifths` | 80% width |
| `.is-three-quarters` | 75% width |
| `.is-two-thirds` | ~66% width |
| `.is-three-fifths` | 60% width |
| `.is-half` | 50% width |
| `.is-two-fifths` | 40% width |
| `.is-one-third` | ~33% width |
| `.is-one-quarter` | 25% width |
| `.is-one-fifth` | 20% width |

### Column Sizes (1-12)
| Class | Description |
|-------|-------------|
| `.is-1` to `.is-12` | Specific column size |

## Column Gaps

| Class | Gap Size |
|-------|----------|
| `.columns.is-gapless` | No gap |
| `.columns.is-gapless` | No gap between columns |
| `.columns.is-vcentered` | Vertically centered |
| `.columns.is-multiline` | Allow wrapping |
| `.columns.is-centered` | Centered columns |

### Gap Sizes
| Class | Description |
|-------|-------------|
| `.columns.is-gap-0` | 0rem |
| `.columns.is-gap-1` | 0.25rem |
| `.columns.is-gap-2` | 0.5rem |
| `.columns.is-gap-3` | 0.75rem |
| `.columns.is-gap-4` | 1rem |
| `.columns.is-gap-5` | 1.5rem |
| `.columns.is-gap-6` | 2rem |
| `.columns.is-gap-7` | 3rem |
| `.columns.is-gap-8` | 4rem |

## Responsiveness

### Vertical by Default
Mobile columns stack vertically by default.

### Column Offsets
| Class | Description |
|-------|-------------|
| `.is-offset-1` to `.is-offset-12` | Offset by that many columns |

## Nesting

```html
<div class="columns">
  <div class="column">
    <div class="columns">
      <div class="column">Nested 1</div>
      <div class="column">Nested 2</div>
    </div>
  </div>
  <div class="column"></div>
</div>
```
