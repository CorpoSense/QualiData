# Bulma Grid

## Overview
Bulma grid system for responsive layouts using `fixed-grid`, `grid`, and `cell` classes.

## Fixed Grid

### Container Classes
| Class | Description |
|-------|-------------|
| `.fixed-grid` | Fixed number of columns container |
| `.grid` | Inner grid container |

### Column Count Modifiers
| Class | Description |
|-------|-------------|
| `.has-1-cols` to `.has-12-cols` | Set fixed number of columns (1-12) |
| `.has-auto-count` | Auto-adjust columns per breakpoint |

### Responsive Column Count
| Breakpoint | Class Suffix | Example |
|------------|--------------|---------|
| Mobile | `-mobile` | `.has-4-cols-mobile` |
| Tablet | `-tablet` | `.has-4-cols-tablet` |
| Desktop | `-desktop` | `.has-4-cols-desktop` |
| Widescreen | `-widescreen` | `.has-4-cols-widescreen` |
| Full HD | `-fullhd` | `.has-4-cols-fullhd` |

### Auto Count Behavior
- 2 columns on mobile
- 4 columns on tablet
- 8 columns on desktop
- 12 columns on widescreen
- 16 columns on fullhd

## Grid Cells

### Cell Classes
| Class | Description |
|-------|-------------|
| `.cell` | Individual grid cell |

### Cell Modifiers
| Class | Description |
|-------|-------------|
| `.is-row` | Cell acts as a row |
| `.is-narrow` | Cell takes only necessary space |
| `.is-flexible` | Cell takes remaining space |

## Smart Grid

Smart grid automatically adjusts columns based on available space.

### Classes
| Class | Description |
|-------|-------------|
| `.is-auto` | Auto-width cells |
| `.is-minimal` | Minimal gap between cells |

---

*Note: For traditional column layouts, see columns.md*
