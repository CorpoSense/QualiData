# Data display

## Table

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `data` | Array<Object> | — | — | Table data |
| `columns` | Array<Object> (same as TableColumns props) | — | — | Table columns |
| `default-sort` | String, Array | — | order: <code>default-sort-direction</code> prop | Sets the default sort column and order — e.g. ['first_name', 'desc'] |
| `default-sort-direction` | String | asc, desc | <code>asc</code> | Sets the default sort column direction on the first click |
| `sort-icon` | String | - | <code>arrow-up</code> | Sets the header sorting icon |
| `sort-icon-size` | String | is-small, , is-medium, is-large | <code>is-small</code> | Sets the size of the sorting icon |
| `bordered` | Boolean | — | <code>false</code> | Border to all cells |
| `striped` | Boolean | — | <code>false</code> | Whether table is striped |
| `narrowed` | Boolean | — | <code>false</code> | Makes the cells narrower |
| `selected` | Object | — | — | Set which row is selected, use the .sync modifier to make it two-way binding |
| `focusable` | Boolean | — | <code>false</code> | Table can be focused and user can navigate with keyboard arrows (require selected.sync) and rows are highlighted when hovering |
| `hoverable` | Boolean | — | <code>false</code> | Rows are highlighted when hovering |
| `checkable` | Boolean | — | <code>false</code> | Rows can be checked (multiple), checked rows will have a .is-checked class if you want to style |
| `checkbox-position` | String | left or right | <code>left</code> | Position of the checkbox (if checkable is true) |
| `sticky-checkbox` | Boolean | — | <code>false</code> | Make the checkbox column sticky when checkable |
| `checked-rows` | Array<Object> | — | — | Set which rows are checked, use the .sync modifier to make it two-way binding |
| `header-checkable` | Boolean | — | <code>true</code> | Show check/uncheck all checkbox in table header when checkable |
| `checkbox-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | is-primary | Type (color) of the checkbox when checkable, optional |
| `mobile-cards` | Boolean | — | <code>true</code> | Rows appears as cards on mobile (collapse rows) |
| `backend-sorting` | Boolean | — | <code>false</code> | Columns won't be sorted with Javascript, use with sort event to sort in your backend |
| `backend-pagination` | Boolean | — | <code>false</code> | Rows won't be paginated with Javascript, use with page-change event to paginate in your backend |
| `total` | Number | — | <code>0</code> | Total number of table data if backend-pagination is enabled |
| `current-page` | Number | — | <code>1</code> | Current page of table data (if paginated) |
| `loading` | Boolean | — | <code>false</code> | Loading state |
| `paginated` | Boolean | — | <code>false</code> | Adds pagination to the table |
| `pagination-simple` | Boolean | — | <code>false</code> | Simple pagination (if paginated) |
| `pagination-rounded` | Boolean | — | <code>false</code> | Rounded pagination (if paginated) |
| `pagination-order` | String | is-centered, is-right | — | Buttons order, optional |
| `pagination-size` | String | is-small, is-medium, is-large | — | Pagination size (if paginated) |
| `pagination-position` | String | bottom, top, both | <code>bottom</code> | Pagination position (if paginated) |
| `per-page` | Number | — | <code>20</code> | How many rows per page (if paginated) |
| `page-input` | Boolean | — | false | Include page number input. |
| `page-input-position` | String | is-input-right, is-input-left | — | Page input position. |
| `debounce-page-input` | Number | — | — | Sets the page input debounce time (in milliseconds) |
| `sort-multiple` | Boolean | — | <code>false</code> | Adds multiple column sorting |
| `sort-multiple-data` | Object | [{field, order}] | <code>[]</code> | Used in combination with backend-sorting |
| `sort-multiple-key` | String | null, shiftKey, altKey, ctrlKey | <code>null</code> | Adds a key which will be required for multi column sorting to work. Will always be enabled if null is selected (default). Requires sort-multiple |
| `row-class` | Function (row: Object, index: Number) | — | — | Add a class to row (&lt;tr&gt; element) based on the return |
| `detailed` | Boolean | — | <code>false</code> | Allow row details (check scoped slots documentation) |
| `custom-detail-row` | Boolean | — | <code>false</code> | Allow a custom detail row |
| `show-detail-icon` | Boolean | — | <code>true</code> | Allow chevron icon and column to be visible |
| `detail-icon` | String | — | <code>chevron-right</code> | Icon name |
| `opened-detailed` | Array | — | <code>[]</code> | Allow pre-defined opened details. Ideal to open details via vue-router. (A unique key is required; check detail-key prop) |
| `has-detailed-visible` | Function (row: Object) | — | <code>true</code> | Controls the visibility of the trigger that toggles the detailed rows. |
| `detail-key` | String | — | — | Use a unique key of your data Object when use detailed or opened detailed. (id recommended) |
| `detail-transition` | String | — | — | Transition name to use when toggling row details. |
| `custom-is-checked` | Function (a: Object, b: Object) | — | — | Custom method to verify if row is checked, works when is checkable. Useful for backend pagination |
| `is-row-checkable` | Function (row: Object) | — | true | Custom method to verify if a row is checkable, works when is checkable. |
| `is-row-selectable` | Function (row: Object) | — | true | Custom method to verify if a row is selectable, works when is selected. |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `mobile-sort-placeholder` | String | — | — | Text when nothing is selected |
| `custom-row-key` | String | - | - | Use a unique key of your data Object for each row. Useful if your data prop has dynamic indices. (id recommended) |
| `draggable` | Boolean | — | <code>false</code> | Allows rows to be draggable |
| `draggable-column` | Boolean | — | <code>false</code> | Allows columns to be draggable |
| `backend-filtering` | Boolean | — | <code>false</code> | Columns won't be filtered with Javascript, use with searchable prop to the columns to filter in your backend |
| `sticky-header` | Boolean | — | <code>false</code> | Show a sticky table header |
| `scrollable` | Boolean | — | <code>false</code> | Add a horizontal scrollbar when table is too wide |
| `height` | Number, String | — | — | Table fixed height in pixels |
| `filters-event` | String | — | — | Add a native event to filter |
| `card-layout` | Boolean | — | <code>false</code> | Rows appears as cards (collapse rows) |
| `show-header` | Boolean | — | <code>true</code> | Show table column header |
| `aria-next-label` | String | — | — | Accessibility label for the next page link (if paginated) |
| `aria-previous-label` | String | — | — | Accessibility label for the previous page link (if paginated) |
| `aria-page-label` | String | — | — | Accessibility label for the page link. If passed, this text will be prepended to the number of the page (if paginated) |
| `aria-current-label` | String | — | — | Accessibility label for the current page link. If passed, this text will be prepended to the current page (if paginated) |
| `debounce-search` | Number | — | — | Sets the filtering debounce time (in milliseconds) |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether the class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying pagination components. If true, they are applied to the root &lt;div&gt; element, which is compatible with Buefy for Vue 2. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `click` | <code>row: Object</code> | Triggers when a row is clicked |
| `dblclick` | <code>row: Object</code> | Triggers when a row is double clicked |
| `cellclick` | <code>row: Object</code>, <code>column: Vue Object</code>, <code>rowIndex: Number</code>, <code>columnIndex: Number</code>, | Triggers when a cell is clicked |
| `sort` | <code>field: String</code>, <code>order: String</code> | Triggers when a sortable column is clicked |
| `sorting-priority-removed` | <code>field: String</code> | Triggers when a multiselect sortable column remove button has been clicked |
| `select` | <code>row: Object</code>, <code>oldRow: Object</code> | Triggers when a row is selected |
| `check` | <code>checkedList: Array</code>, <code>row: Object</code> | Triggers when the checkbox in a row is clicked and/or when the header checkbox is clicked |
| `check-all` | <code>checkedList: Array</code> | Triggers when the header checkbox is clicked |
| `page-change` | <code>page: Number</code> | Triggers when pagination page is changed |
| `details-open` | <code>row: Object</code> | Triggers when details is opened |
| `details-close` | <code>row: Object</code> | Triggers when details is closed |
| `contextmenu` | <code>row: Object</code>, <code>contextMenuNativeEvent: Event</code> | Triggers when right-click on a row |
| `dragstart` | <code> row: Object </code>, <code> dragEvent: Event </code>, <code> index: Number </code> | Triggers when starting to drag a row |
| `dragend` | <code> row: Object </code>, <code> dragEvent: Event </code>, <code> index: Number </code> | Triggers when ending to drag a row |
| `drop` | <code> row: Object </code>, <code> drop: Event </code>, <code> index: Number </code> | Triggers when dropping on a row |
| `dragover` | <code> row: Object </code>, <code> dragover: Event </code>, <code> index: Number </code> | Triggers when dragging over a row |
| `dragleave` | <code> row: Object </code>, <code> dragover: Event </code>, <code> index: Number </code> | Triggers after dragging over a row |
| `columndragstart` | <code> column: Object </code>, <code> dragEvent: Event </code>, <code> index: Number </code> | Triggers when starting to drag a column |
| `columndragend` | <code> column: Object </code>, <code> dragEvent: Event </code>, <code> index: Number </code> | Triggers when ending to drag a column |
| `columndrop` | <code> column: Object </code>, <code> drop: Event </code>, <code> index: Number </code> | Triggers when dropping on a column |
| `columndragover` | <code> column: Object </code>, <code> dragover: Event </code>, <code> index: Number </code> | Triggers when dragging over a column |
| `columndragleave` | <code> column: Object </code>, <code> dragover: Event </code>, <code> index: Number </code> | Triggers after dragging over a column |
| `mouseenter` | <code> row: Object </code>, <code> event: Event </code> | Triggers when mouse enters a row |
| `mouseleave` | <code> row: Object </code> | Triggers when mouse leaves a row |
| `filters-change` | <code> filter: Object </code> | Triggers when filter change |
| `update:checkedRows` | <code>checkedRows: Array</code> | Triggers when checked rows are updated (Vue 3 v-model for checkedRows) |
| `update:currentPage` | <code>page: Number</code> | Triggers when current page is updated (Vue 3 v-model for currentPage) |
| `update:openedDetailed` | <code>rows: Array</code> | Triggers when opened detailed rows are updated (Vue 3 v-model for openedDetailed) |
| `update:selected` | <code>row: Object</code> | Triggers when selected row is updated (Vue 3 v-model for selected) |
| `filters-event-[filters-event]` | <code> event: Event </code>, <code> filter: Object </code> | Triggers filters-event event from filter (it works only with Vue 2.6.x) |

### Slots
| Name | Description |
|------|-------------|
| `default` | Required, table body and header |
| `header` | Table custom header |
| `subheading` | Table subheading |
| `detail` | Row detail (collapsible) |
| `empty` | Replaces table body when data array prop is empty |
| `footer` | Table custom footer |
| `bottom-left` | Custom bottom-left (opposite side of bottom pagination) |
| `top-left` | Custom top-left (opposite side of top pagination) |
| `pagination` | Table custom pagination |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `initSort` | Sort using default-sort prop parameters | — | — |
| `focus` | Focus table element if is focusable | — | — |
| `toggleDetails` | Toggle row detail if table is detailed | <code>row: Object</code> | — |
| `openDetailRow` | Open row detail if table is detailed | <code>row: Object</code> | — |
| `closeDetailRow` | Close row detail if table is detailed | <code>row: Object</code> | — |
| `resetMultiSorting` | Resets the multi column sorting | — | — |

---

## Column

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `label` | String | — | — | Column header text, also used to identify column if custom-key prop is missing |
| `custom-key` | String, Number | — | <code>this.label</code> | Unique identifier, use when label is missing or there are duplicate label names |
| `field` | String | — | — | Property of the object the column is attributed, used for sorting |
| `meta` | Any | — | — | Meta prop to add anything, useful when creating custom headers |
| `width` | Number, String | — | — | Column fixed width in any unit, or pixels when none is provided |
| `numeric` | Boolean | — | <code>false</code> | Align the cell content to the right, sort icon on left |
| `centered` | Boolean | — | <code>false</code> | Align the cell content to the center |
| `sortable` | Boolean | — | <code>false</code> | Whether the column can be sorted |
| `visible` | Boolean | — | <code>true</code> | Whether the column is visible |
| `custom-sort` | Function (a: Object, b: Object, isAsc: Boolean) | — | — | Custom sort method, works when column is sortable |
| `searchable` | Boolean | — | <code>false</code> | Add a input below the header to filter data |
| `custom-search` | Function (a: Object, input: String) | — | — | Custom search method, works when column is searchable |
| `subheading` | String, Number | — | — | Column subheading text |
| `sticky` | Boolean | — | <code>false</code> | Show a sticky column |
| `header-selectable` | Boolean | — | <code>false</code> | Whether the header text is selectable, works when column is sortable. |
| `header-class` | String | — | - | CSS classes to be applied on header |
| `cell-class` | String | — | - | CSS classes to be applied on cell |
| `th-attrs` | Function | — | - | Adds native attributes to th :th-attrs="(column)" => ({})" |
| `td-attrs` | Function: <code>(row, column) => Record&lt;string, any&gt;</code> | — | - | Adds native attributes to td. Do not specify an inline arrow function to this prop. Otherwise, you will face infinite updates. |

### Slots
| Name | Description |
|------|-------------|
| `default` | Required, table column body |
| `header` | Table column custom header |
| `subheading` | Table column custom subheading |
| `searchable` | This is to customize the search input when searchable. |


## Carousel

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Number | — | <code>0</code> | Binding value |
| `animated` | String | fade, slide | <code>slide</code> | Transition effect |
| `interval` | Number | — | <code>3500</code> | Interval of the autoplay, in milliseconds |
| `has-drag` | Boolean | — | <code>true</code> | Toggle touch dragging, when touch not detected. Auto switch mouse dragging |
| `autoplay` | Boolean | — | <code>true</code> | Whether to automatically loop the slides |
| `pause-hover` | Boolean | — | <code>true</code> | Pause carousel when autoplay and mouse enter |
| `pause-info` | Boolean | — | <code>true</code> | Show information about pause when autoplay and pause-hover |
| `pause-info-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-white</code> | Type (color) of the pause-info, optional |
| `pause-text` | String | — | <code>Pause</code> | Text when pause |
| `arrow` | Boolean | — | <code>true</code> | Display the "next" and "prev" action |
| `arrow-hover` | Boolean | — | <code>true</code> | Display the "next" and "prev" action when hover, but hidden on mobile |
| `repeat` | Boolean | — | <code>true</code> | Controls whether the carousel loops around at the start and end |
| `icon-pack` | String | mdi, fa, fas, far, fab, fad, fal | <code>mdi</code> | Icon pack to use |
| `icon-size` | String | is-small, is-medium, is-large | <code>—</code> | Arrow icon size, optional |
| `icon-prev` | String | — | <code>chevron-left</code> | Icon to use for previous arrow |
| `icon-next` | String | — | <code>chevron-right</code> | Icon to use for next arrow |
| `indicator` | Boolean | — | <code>true</code> | Display the indicator for jumping to specific item |
| `indicator-background` | Boolean | — | <code>false</code> | Adds background to indicator |
| `indicator-custom` | Boolean | — | <code>false</code> | Use when there are more than 6 images so that the indicator is not too small |
| `indicator-custom-size` | String | is-small, is-medium | <code>is-small</code> | Image size of the indicator when the indicator-custom is used |
| `indicator-inside` | Boolean | — | <code>true</code> | Display the indicator inside the carousel |
| `indicator-mode` | String | click, hover | <code>click</code> | Trigger for action indicator |
| `indicator-position` | String | is-bottom, is-top | <code>is-bottom</code> | Position indicator only when indicator-inside |
| `indicator-style` | String | is-boxes, is-dots, is-lines | <code>is-dots</code> | Style for indicator of carousel |
| `overlay` | Boolean | — | <code>false</code> | Switch like a gallery |
| `progress` | Boolean | — | <code>false</code> | Display the progress item of carousel |
| `progress-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the progress, optional |
| `with-carousel-list` | Boolean | — | <code>false</code> | Use when indicator custom with b-carousel-list |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `change` | <code>value: Boolean</code>, <code>value: String</code> | Triggers when carousel item value is changed |
| `input` | <code>value: Boolean</code>, <code>value: String</code> | Triggers when indicator-mode value is changed |
| `click` | — | Non-native click event, will trigger only when clicking an element that should normally not be clickable/focusable |

### Slots
| Name | Description |
|------|-------------|
| `indicators` | Custom indicators |
| `list` | Custom indicators when with-carousel-list |
| `overlay` | Custom other when overlay |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `next()` | Move to next slide | — | — |
| `prev()` | Move to previous slide | — | — |
| `changeActive(index: Number)` | Change to specific slide by index | — | — |

---

## Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `order` | Number | - | - | Order of the item. Carousel sorts the items in ascending order of this value. By default, the order is determined according to when items are mounted in sequence. You have to give an explicit value if you want to keep the ordering when the number of items in Carousel may vary. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `click` | — | Non-native click event, will trigger only on an element that should normally not be clickable/focusable |

---

## List

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Number | — | <code>0</code> | Binding value |
| `scroll-value` | Number | — | <code>0</code> | Initial scroll position value |
| `data` | Array | — | — | Carousel-list data (any b-image prop can be used) |
| `has-drag` | Boolean | — | <code>true</code> | Toggle touch dragging, when touch not detected. Auto switch mouse dragging |
| `has-grayscale` | Boolean | — | <code>false</code> | Give a grayscale effect to img |
| `has-opacity` | Boolean | — | <code>false</code> | Give an opacity effect to img |
| `repeat` | Boolean | — | <code>false</code> | Returns carousel to start when active item matches length of data |
| `items-to-show` | Number | — | <code>4</code> | Count of items to be showed per view (supports a decimal). |
| `items-to-list` | Number | 1-5 | <code>1</code> | Count of items to list when using navigation buttons |
| `as-indicator` | Boolean | — | <code>false</code> | Switch mode to indicator for carousel |
| `breakpoints` | Object | — | <code>{}</code> | Responsive breakpoint settings for different screen sizes |
| `arrow` | Boolean | — | <code>true</code> | Display the "next" or "prev" action when first or last item |
| `arrow-hover` | Boolean | — | <code>true</code> | Display arrow action when hovered. Hidden on mobile |
| `icon-pack` | String | mdi, fa, fas, far, fab, fad, fal | <code>mdi</code> | Icon pack to use |
| `icon-size` | String | is-small, is-medium, is-large | <code>—</code> | Arrow icon size, optional |
| `icon-prev` | String | — | <code>chevron-left</code> | Icon to use for previous arrow |
| `icon-next` | String | — | <code>chevron-right</code> | Icon to use for next arrow |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `switch` | <code>value: Boolean</code>, <code>value: Number</code>, <code>value: String</code> | Triggers when value is changed |
| `updated:scroll` | <code>index: Number</code> | Triggers when scroll position changes |

### Slots
| Name | Description |
|------|-------------|
| `item` | Custom item |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `next()` | Move to next items | — | — |
| `prev()` | Move to previous items | — | — |
| `switchTo(index: Number)` | Switch to specific index | — | — |
| `refresh()` | Refresh the carousel layout | — | — |


## Collapse

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Boolean | — | <code>true</code> | Whether collapse is open or not |
| `animation` | String | — | <code>fade</code> | Custom animation (transition name) |
| `aria-id` | String | — | — | Id for the container div. Should be used with aria-controls on trigger for better accessibility. |
| `position` | String | is-top, is-bottom | <code>is-top</code> | Trigger position |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the collapse state changes (v-model event) |
| `open` | — | Triggers when user opened |
| `close` | — | Triggers when user closed |

### Slots
| Name | Description |
|------|-------------|
| `default` | Content to show/hide |
| `trigger` | Trigger content |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggle` | Toggle activation | — | — |


## Dropdown

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Any | — | <code>null</code> | Binding value |
| `triggers` | Array | click,hover,contextmenu,focus | <code>['click']</code> | Dropdown will be triggered by any events |
| `position` | String | is-top-right, is-top-left, is-bottom-left | Bottom right | Optional, position of the dropdown relative to the trigger |
| `disabled` | Boolean | — | <code>false</code> | Disables dropdown |
| `animation` | String | — | <code>fade</code> | Custom animation (transition name) |
| `inline` | Boolean | — | <code>false</code> | Dropdown content (items) are shown inline, trigger is removed |
| `mobile-modal` | Boolean | — | <code>true</code> | Dropdown content (items) are shown into a modal on mobile |
| `expanded` | Boolean | — | <code>false</code> | Dropdown will be expanded (full-width) |
| `aria-role` | String | list, menu, dialog | — | Role attribute to be passed to list container for better accessibility. Use menu only in situations where your dropdown is related to navigation menus. |
| `multiple` | Boolean | — | <code>false</code> | Allows multiple selections |
| `trap-focus` | Boolean | — | <code>true</code> | Trap focus inside the dropdown. |
| `can-close` | Boolean, Array | escape, outside | <code>true</code> | Can close dropdown by pressing escape or by clicking outside |
| `close-on-click` | Boolean | — | <code>true</code> | Close dropdown when content is clicked |
| `append-to-body` | Boolean | — | <code>false</code> | Append dropdown content to body (prevents event bubbling) |
| `append-to-body-copy-parent` | Boolean | — | <code>false</code> | Copy parent classes when appending to body |
| `scrollable` | Boolean | — | <code>false</code> | Dropdown content will be scrollable |
| `max-height` | String, Number | — | <code>200px</code> | Max height of dropdown content |
| `trigger-tabindex` | Number | - | <code>0</code> | Set the tabindex attribute on the dropdown trigger div (-1 to prevent selection via tab key) |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Any | Any[]</code> | Triggers when the selected value changes (v-model event) |
| `change` | <code>value: String</code> | Triggers when an item is selected |
| `active-change` | <code>active: Boolean</code> | Triggers when dropdown is activated or deactivated (visibility of list) |

### Slots
| Name | Description |
|------|-------------|
| `default` | — |
| `trigger` | Trigger content for the dropdown |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggle` | Toggle activation (dropdown list visibility) | — | — |

---

## Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `value` | Any | — | <code>null</code> | The value that will be returned on events and v-model |
| `separator` | Boolean | — | <code>false</code> | Set the item to be a separator |
| `disabled` | Boolean | — | <code>false</code> | Item is disabled |
| `focusable` | Boolean | — | <code>true</code> | Item can be focused |
| `custom` | Boolean | — | <code>false</code> | Item is not a clickable item |
| `has-link` | Boolean | — | <code>false</code> | Use it if your item is an anchor tag or router-link |
| `paddingless` | Boolean | — | <code>false</code> | Remove padding |
| `aria-role` | String | listitem, menuitem | — | Role attribute to be passed to list item for better accessibility. Use menuitem only in situations where your dropdown is related to navigation menus. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `click` | — | Triggers when the item is clicked |

### Slots
| Name | Description |
|------|-------------|
| `default` | — |


## Rate

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Number | — | <code>0</code> | Binding value |
| `max` | Number | — | <code>5</code> | Max rating score |
| `icon` | String | — | <code>star</code> | to specify the icon |
| `icon-pack` | String | mdi, fa, fas, far, fab, fad, fal | <code>mdi</code> | Icon pack to use |
| `size` | String | is-small, is-medium, is-large | — | Include show-text, show-score and custom-text, optional |
| `rtl` | Boolean | — | <code>false</code> | Change text direction show-text, show-score and custom-text to left |
| `spaced` | Boolean | — | <code>false</code> | Added spacing for icons |
| `disabled` | Boolean | — | <code>false</code> | Read only, if true Support decimal value |
| `show-score` | Boolean | — | <code>false</code> | Display value |
| `show-text` | Boolean | — | <code>false</code> | Display texts template. show-score and show-text cannot be true at the same time |
| `custom-text` | String | — | — | Display custom text like a total points or total reviews, and this only for show-score |
| `texts` | Array | — | — | Texts template only for show-text, like on e-commerce |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Number</code> | Triggers when rate value is changed |
| `change` | <code>value: Number</code> | Triggers when rate value is changed |


## Field

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String, Object | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the field and help message, also adds a matching icon, optional. Used by Input, Select and Autocomplete |
| `label` | String | — | — | Field label |
| `label-for` | String | — | — | Same as native for set on the label |
| `custom-class` | String | — | — | CSS classes to be applied on field label |
| `message` | String, Object, Array<String>, Array<Object> | — | — | Help message text |
| `grouped` | Boolean | — | <code>false</code> | Direct child components/elements of Field will be grouped horizontally (see which ones at the top of the page). Do not mix with horizontal because there is an issue that the validation error cannot be reset once it is set if combined with horizontal. |
| `group-multiline` | Boolean | — | <code>false</code> | Allow controls to fill up multiple lines, making it responsive |
| `position` | String | is-centered, is-right | — | Which position should the addons appear, optional |
| `addons` | Boolean | — | <code>true</code> | Field automatically attach controls together |
| `expanded` | Boolean | — | <code>false</code> | Makes the field take up the full width available |
| `horizontal` | Boolean | — | <code>false</code> | Group label and control on the same line for horizontal forms. Do not mix with grouped because there is an issue that the validation error cannot be reset once it is set if combined with grouped. |
| `label-position` | String | inside, on-border | - | Position of label |

### Slots
| Name | Description |
|------|-------------|
| `default` | Main content area where form controls are placed |
| `label` | Custom label |
| `message` | Custom message |


