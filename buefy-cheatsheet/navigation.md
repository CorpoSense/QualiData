# Navigation

## Pagination

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `total` | Number, String | — | — | Total count of items |
| `per-page` | Number | — | <code>20</code> | Items count for each page |
| `range-before` | Number | — | <code>1</code> | Number of pagination items to show before current page |
| `range-after` | Number | — | <code>1</code> | Items to paginatation items to show after current page |
| `v-model` | Number, String | — | <code>1</code> | Current page number (two-way binding) |
| `current` | Number | — | <code>1</code> | Current page number, use the .sync modifier to make it two-way binding |
| `order` | String | is-centered, is-right | — | Buttons order, optional |
| `size` | String | is-small, is-medium, is-large | — | Pagination size, optional |
| `simple` | Boolean | — | <code>false</code> | Simpler style |
| `rounded` | Boolean | — | <code>false</code> | Rounded button styles |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `icon-prev` | String | — | <code>chevron-left</code> | Icon to use for previous button |
| `icon-next` | String | — | <code>chevron-right</code> | Icon to use for next button |
| `aria-next-label` | String | — | — | Accessibility label for the next page link. |
| `aria-previous-label` | String | — | — | Accessibility label for the previous page link. |
| `aria-page-label` | String | — | — | Accessibility label for the page link. If passed, this text will be prepended to the number of the page. |
| `aria-current-label` | String | — | — | Accessibility label for the current page link. If passed, this text will be prepended to the current page. |
| `page-input` | Boolean | — | false | Include page number input. |
| `page-input-position` | String | is-input-right, is-input-left | — | Page input position. |
| `debounce-page-input` | Number | — | — | Sets the page input debounce time (in milliseconds) |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Number</code> | Triggers when the current page is changed |
| `change` | <code>value: Number</code> | Triggers when the current page is changed |

### Slots
| Name | Description |
|------|-------------|
| `default` | This is to customize numbered pagination buttons with the Button subcomponent. |
| `next` | This is to customize the next pagination button with the Button subcomponent. |
| `previous` | This is to customize the previous pagination button with the Button subcomponent. |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `prev` | Go to the previous page | <code>event?: Event</code> | — |
| `next` | Go to the next page | <code>event?: Event</code> | — |
| `first` | Go to the first page | <code>event?: Event</code> | — |
| `last` | Go to the last page | <code>event?: Event</code> | — |
| `changePage` | Go to a specific page number | <code>num: Number, event?: Event</code> | — |

---

## Button

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `page` | Object | — | — | The prop page need to be passed upon the component (:page="props.page"). |
| `tag` | String, Object | a, button, input, router-link, nuxt-link or other nuxt alias | <code>a</code> | Button tag name |

### Slots
| Name | Description |
|------|-------------|
| `default` | Required, pagination button content |


## Breadcrumb

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `align` | String | is-left, is-centered, is-right | <code>is-right</code> | Breadcrumb alignment. |
| `separator` | String | has-arrow-separator, has-bullet-separator, has-dot-separator, has-succeeds-separator | — | Symbol that separates the breadcrumb items. |
| `size` | String | is-small, is-medium, is-large | <code>is-medium</code> | The breadcrumb size |

### Slots
| Name | Description |
|------|-------------|
| `default` | Breadcrumb items |

---

## Breadcrumb Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `tag` | String, Object | router-link, a | <code>a</code> | a, router-link and it's html attributes like href, to, etc... |
| `active` | Boolean | false, true | <code>false</code> | is the current breadcrumb is actually the current page. |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;li&gt; element or the underlying tag. If true, they are applied to the root &lt;li&gt; element, which is compatible with Vue 2. |

### Slots
| Name | Description |
|------|-------------|
| `default` | Breadcrumb item content |


## Tabs

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | String, Number, Null | — | <code>undefined</code> | Binding value, tab index. Passing undefined will show the first tab, null will show no tab |
| `expanded` | Boolean | — | <code>false</code> | Make tab full width |
| `animated` | Boolean | — | <code>true</code> | Tabs have slide animation |
| `animateInitially` | Boolean | — | <code>undefined</code> | Apply animation on the initial render |
| `animation` | String | — | <code>slide-next</code> <code>slide-prev</code> | Custom animation (transition name) |
| `type` | String | is-boxed, is-toggle | — | Type/Style of the tab, optional |
| `size` | String | is-small, is-medium, is-large | — | Size of the tab, optional |
| `position` | String | is-centered, is-right | — | Position of the tab, optional |
| `vertical` | Boolean | — | <code>false</code> | Display the tabs vertically. The content will be placed at right. |
| `destroy-on-hide` | Boolean | — | <code>false</code> | Destroy tabitem on hide |
| `multiline` | Boolean | — | <code>false</code> | Tabs will be multilined |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: String|Number</code> | Triggers when tab is changed |

### Slots
| Name | Description |
|------|-------------|
| `default` | Tab items |
| `start` | Content before the tabs |
| `end` | Content after the tabs |

---

## Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `label` | String | — | — | Tab label |
| `value` | String | — | Vnode uid | Tab identifier |
| `icon` | String | — | — | Icon name |
| `icon-pack` | String | — | <code>mdi</code> | Icon pack to use |
| `disabled` | Boolean | - | false | Item is disabled |
| `visible` | Boolean | - | true | Item is visible |
| `headerClass` | String, Array, Object | - | - | The classes to add to the tab header |
| `order` | Number | - | - | Order of the tab. Tabs sorts the tabs in ascending order of this value. By default, the order is determined according to when tabs are mounted in sequence. You have to give an explicit value if you want to keep the ordering when the number of tabs in Tabs may vary. |

### Slots
| Name | Description |
|------|-------------|
| `default` | Tab item body |
| `header` | Tab item custom header |


## Steps

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Number, String | — | <code>undefined</code> | Binding value, step index. Passing undefined will show the first step |
| `animated` | Boolean | — | <code>true</code> | Steps have slide animation |
| `animateInitially` | Boolean | — | <code>undefined</code> | Apply animation on the initial render |
| `animation` | String | — | <code>slide-next</code> <code>slide-prev</code> | Custom animation (transition name) |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Default Type/Style for the steps, optional |
| `size` | String | is-small, is-medium, is-large | — | Size of the step, optional |
| `destroy-on-hide` | Boolean | — | <code>false</code> | Destroy stepitem on hide |
| `icon-pack` | String | — | <code>mdi</code> | Icon pack to use for the navigation |
| `icon-prev` | String | — | <code>chevron-left</code> | Icon to use for navigation button |
| `icon-next` | String | — | <code>chevron-right</code> | Icon to use for navigation button |
| `has-navigation` | Boolean | — | <code>true</code> | Next and previous buttons below the component. You can use this property if you want to use your own custom navigation items. |
| `vertical` | Boolean | — | <code>false</code> | Display the steps vertically |
| `position` | String | is-right | — | Position of the vertical step, optional |
| `label-position` | String | bottom, right, left | <code>bottom</code> | Position of the marker label, optional |
| `rounded` | Boolean | — | <code>true</code> | Rounded step markers |
| `mobile-mode` | String | minimalist: Only the active Step is displayed, compact: Step label is displayed only for the active, null: Will keep the same behavior as desktop | <code>minimalist</code> | How Steps will be displayed for mobile user |
| `aria-next-label` | String | — | — | Accessibility label for the next navigation button |
| `aria-previous-label` | String | — | — | Accessibility label for the previous navigation button |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: String|Number</code> | Triggers when active step is changed |

### Slots
| Name | Description |
|------|-------------|
| `default` | Step body where step-item can be included |
| `navigation` | Used to customize navigation button |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `prev` | Go to previous step | — | void |
| `next` | Go to next step | — | void |

---

## Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `step` | String | Number | — | — | Step marker content (when there is no icon) |
| `label` | String | — | — | Step label |
| `value` | String | — | Vnode uid | Step identifier |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Default Type/Style for the step, optional. This will override parent type. Could be used to set a completed step to is-success for example |
| `icon` | String | — | — | Icon name |
| `icon-pack` | String | — | <code>mdi</code> | Icon pack to use |
| `clickable` | Boolean | — | — | Item can be used directly to navigate. If undefined, previous steps are clickable while the others are not. |
| `visible` | Boolean | - | true | Item is visible |
| `headerClass` | String, Array, Object | - | - | The classes to add to the step label container |
| `order` | Number | - | - | The order of the step. Steps sorts the steps in ascending order of this value. By default, the order is determined according to when steps are mounted in sequence. You have to give an explicit value if you want to keep the ordering when the number of steps in Steps may vary. |

### Slots
| Name | Description |
|------|-------------|
| `default` | Step item body |


