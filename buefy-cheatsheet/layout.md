# Layout

## Sidebar

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Boolean | — | <code>false</code> | To control the behaviour of the sidebar programmatically (two-way binding) |
| `open` | Boolean | — | <code>false</code> | To control the behaviour of the sidebar programmatically, use the .sync modifier to make it two-way binding |
| `position` | String | fixed,static,absolute | <code>fixed</code> | Set display position of sidebar |
| `type` | String, Object | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the background, optional |
| `can-cancel` | Boolean, Array | escape, outside | <code>['escape', 'outside']</code> | Can close Sidebar pressing escape or clicking outside |
| `on-cancel` | Function | — | — | Callback function to call after user canceled (clicked 'X' / pressed escape / clicked outside) |
| `fullwidth` | Boolean | - | <code>false</code> | Show sidebar in fullwidth. A close button will be present for a fullwidth sidebar. |
| `fullheight` | Boolean | - | <code>false</code> | Show sidebar in fullheight. |
| `mobile` | String | fullwidth,reduce,hide | — | Custom layout on mobile |
| `right` | Boolean | — | <code>false</code> | Show the sidebar on right |
| `overlay` | Boolean | — | <code>false</code> | Show an overlay when sidebar is open |
| `expand-on-hover` | Boolean | — | <code>false</code> | Expand sidebar on hover when reduced or mobile is reduce |
| `expand-on-hover-fixed` | Boolean | — | <code>false</code> | Expand sidebar on hover with fixed position when reduced or mobile is reduce |
| `reduce` | Boolean | — | <code>false</code> | Show a small sidebar |
| `scroll` | String | clip, keep | <code>clip</code> | clip to remove the &lt;body&gt; scrollbar, keep to have a non scrollable scrollbar to avoid shifting background, but will set &lt;body&gt; to position fixed, might break some layouts |
| `delay` | Number | — | <code>0</code> | Sidebar delay before it open (number in ms) |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when sidebar is opened/closed |
| `close` | — | Triggers when user closed/canceled |

### Slots
| Name | Description |
|------|-------------|
| `default` | Content of sidebar |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Programmatically close the sidebar | — | — |
| `cancel` | Close the sidebar with a specific cancel method | <code>method: String, ...args</code> | — |


## Navbar

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `transparent` | Boolean | — | false | Remove any hover or active background from the navbar items |
| `fixed-top` | Boolean | — | <code>false</code> | Fixes the navbar to the top of the page |
| `fixed-bottom` | Boolean | — | <code>false</code> | Fixes the navbar to the bottom of the page |
| `v-model` | Boolean | — | <code>false</code> | To control the behaviour of the mobile menu programmatically |
| `centered` | Boolean | — | <code>false</code> | To center the navbar-start slot |
| `type` | String,  | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the background, optional |
| `wrapper-class` | String | — | — | To wrap the navbar content into an div with the provided class |
| `close-on-click` | Boolean | true, false | <code>true</code> | Control the behavior of the mobile menu by clicking on a link or outside the menu |
| `mobile-burger` | Boolean | true, false | <code>true</code> | Use to display or not the burger on mobile resolution. |
| `spaced` | Boolean | — | false | Sets Top and Bottom paddings with 1rem, Left and Right paddings with 2rem |
| `shadow` | Boolean | true, false | false | Add a shadow to navbar |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the mobile menu visibility changes (Vue 3 v-model event) |

### Slots
| Name | Description |
|------|-------------|
| `brand` | The slot for the brand logo |
| `burger` | The slot for the burger that triggers the menu toggle |
| `start` | Items that will appear on the left |
| `end` | Items that will appear on the right |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggleActive` | Toggle the mobile menu visibility | — | — |
| `closeMenu` | Close the mobile menu | — | — |

---

## Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `tag` | String, Object | a, router-link, div and it's html attributes like href, to, etc... | a | Sets the type of the component that have to render as navbar-item |
| `active` | Boolean | - | false | Item is active |

---

## Dropdown

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `label` | String | — | — | Dropdown label text |
| `tag` | String, Object | a, router-link, div and it's html attributes like href, to, etc... | a | Sets the type of the component that have to render as navbar-item |
| `hoverable` | Boolean | - | false | Dropdown will be triggered by hover instead of click |
| `active` | Boolean | - | false | Item is active |
| `right` | Boolean | - | false | Dropdown will be anchored to the right side |
| `arrowless` | Boolean | - | false | Show/hide arrow icon on dropdown |
| `boxed` | Boolean | - | false | Show a boxed version of the dropdown |
| `collapsible` | Boolean | — | false | Collapsible dropdown on mobile |
| `close-on-click` | Boolean | — | <code>true</code> | Close dropdown when clicking inside |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying tag. If true, they are applied to the root &lt;div&gt; element, which is compatible with Buefy for Vue 2. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `active-change` | <code>active: Boolean</code> | Triggers when dropdown is activated or deactivated (visibility of list) |

### Slots
| Name | Description |
|------|-------------|
| `default` | Menu item body |
| `label` | Dropdown menu custom label |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggleMenu` | Toggle the dropdown menu visibility | — | — |
| `showMenu` | Show the dropdown menu | — | — |
| `closeMenu` | Close the dropdown menu | — | — |


## Menu

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `accordion` | Boolean | — | true | Close automatically the previous selected menu list |
| `activable` | Boolean | — | true | Active automatically the clicked menu item |

### Slots
| Name | Description |
|------|-------------|
| `default` | Menu list elements |

---

## List

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `label` | String | — | — | Menu list label |
| `icon` | String | — | — | Icon name |
| `icon-pack` | String | — | <code>mdi</code> | Icon pack to use |
| `size` | String | is-small, is-medium, is-large | <code>is-small</code> | Icon size |

### Slots
| Name | Description |
|------|-------------|
| `default` | Menu item elements |
| `label` | Menu list custom label |

---

## Item

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `label` | String | — | — | Menu item label |
| `icon` | String | — | — | Icon name |
| `icon-pack` | String | — | <code>mdi</code> | Icon pack to use |
| `disabled` | Boolean | - | false | Item is disabled |
| `v-model` | Boolean | - | false | Item is active |
| `v-model:expanded` | Boolean | - | false | Item is expanded when default contains menu items |
| `animation` | String | — | <code>fade</code> | Custom animation (transition name) |
| `tag` | String, Object | a, router-link, nuxt-link or other nuxt alias | <code>a</code> | Button tag name |
| `aria-role` | String | menuitem | — | Role attribute to be passed to list item for better accessibility. Use menuitem only in situations where your menu item is really related to navigation. |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;li&gt; element or the underlying tag. If true, they are applied to the root &lt;li&gt; element, which is compatible with Buefy for Vue 2. |
| `size` | String | is-small, is-medium, is-large | <code>is-small</code> | Icon size |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the active state changes |
| `update:expanded` | <code>value: Boolean</code> | Triggers when the expanded state changes |

### Slots
| Name | Description |
|------|-------------|
| `default` | Menu item body |
| `label` | Menu list custom label |


