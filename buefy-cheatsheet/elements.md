# Elements

## Button

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String, Object | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the control, optional |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of button, optional |
| `label` | String | — | — | Button label, optional when default slot |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the button |
| `rounded` | Boolean | — | <code>false</code> | Rounded style |
| `outlined` | Boolean | — | <code>false</code> | Outlined style |
| `focused` | Boolean | — | <code>false</code> | Focused style |
| `inverted` | Boolean | — | <code>false</code> | Inverted style |
| `hovered` | Boolean | — | <code>false</code> | Hovered style |
| `active` | Boolean | — | <code>false</code> | Active style |
| `selected` | Boolean | — | <code>false</code> | Selected style |
| `expanded` | Boolean | — | <code>false</code> | Button will be expanded (full-width) |
| `icon-left` | String | — | — | Icon name to show on the left |
| `icon-right` | String | — | — | Icon name to show on the right |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `native-type` | String | button, submit, reset | <code>button</code> | Button type, like native |
| `tag` | String, Object | button, a, input, router-link, nuxt-link or other nuxt alias | <code>button</code> | Button tag name |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `click` | <code>event: $event</code> | Triggers on click |
| `[any].native` | <code>event: $event</code> | Listen to any event using this syntax, e.g mousedown.native |


## Icon

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String, Object | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the icon, optional |
| `component` | String | — | Uses global config <code>defaultIconComponent</code> or <code>&lt;i&gt;</code> tag | Component to be used instead of default &lt;i&gt; tag. Useful for custom icon components like FontAwesome Vue components |
| `pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `icon` | String | — | — | Icon name |
| `size` | String | is-small, is-medium, is-large | — | Icon size, optional |
| `custom-size` | String | Depends on library: null (smallest), fa-lg, fa-2x, fa-3x, fa-4x, fa-5x, mdi-18px, mdi-24px, mdi-36px, mdi-48px | Depends on <code>size</code> prop | Overrides icon font size, optional |
| `custom-class` | String | — | — | Add class to icon font (&lt;i&gt; tag), optional. See here for MDI, here for FontAwesome 4 and here for FontAwesome 5 custom classes |


## Image

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `src` | String | — | — | The image url you want to display. You can use webp extension here. Do not forget to specify a fallback for browsers that do not support this format yet. |
| `alt` | String | — | — | The image alternate text, if it cannot be displayed. |
| `src-fallback` | String | — | — | The image url you want to display if the image specified using src fails to load. |
| `webp-fallback` | String | — | — | Fallback when using webp format. You can specify an extension only (.jpg, .jpeg, .png, .gif) if the filename is the same. You can use a full url if not. |
| `lazy` | Boolean | — | <code>true</code> | Use IntersectionObserver to display the image only when in viewport. |
| `responsive` | Boolean | — | <code>true</code> | The image will take 100% of the parent width. Use this with ratio to prevent page jump when images are loading. |
| `ratio` | String | 1by1, 5by4, 4by3, 3by2, 5by3, 16by9, 2by1, 3by1, 4by5, 3by4, 2by3, 3by5, 9by16, 1by2 1by3 or any string having this format {number}by{number} | — | The space will be reserved. Prevent page jump when images are loading when using responsive. |
| `placeholder` | String | — | — | The image that will be displayed before the src load. Useful if you want to use lqip technique. Will use webp-fallback if only an extension is given. |
| `srcset` | String | — | — | You can enter a valid srcset value (ex. "image1.webp 400w,image2.webp 800w"). Will use webp-fallback if only an extension is given. |
| `srcset-sizes` | Array<Number> | — | — | It will generate a srcset string using those sizes. |
| `srcset-formatter` | Function | — | <code>(src, size) => "${srcFilename}-${size}.${srcExt}"</code> | Function to format src according to a given size. |
| `rounded` | Boolean | — | <code>false</code> | Rounded image. |
| `custom-class` | String | — | — | Add custom css class to the img tag. |
| `caption-first` | Boolean | — | <code>false</code> | Controls the position of the caption. When true, caption is displayed before the image, when false, after the image. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `load` | <code>event: Event</code>, <code>src: String</code> | Triggers when the image is loaded. |
| `error` | <code>event: Event</code>, <code>src: String</code> | Triggers when the image fails to load. |

### Slots
| Name | Description |
|------|-------------|
| `placeholder` | This is to customize the placeholder waiting the image to load. |
| `caption` | Content for the image caption displayed as a figcaption element. Position controlled by the caption-first prop. |


## Tag

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the tag, optional |
| `close-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the cross button of tag, optional |
| `size` | String | is-medium, is-large | — | Size of the tag, optional |
| `rounded` | Boolean | — | <code>false</code> | Tag border rounded |
| `closable` | Boolean | — | <code>false</code> | Add close/delete button to the tag |
| `attached` | Boolean | — | <code>false</code> | Close/delete button style equal to attached tags |
| `ellipsis` | Boolean | — | <code>false</code> | Adds ellipsis to not overflow the text |
| `tabstop` | Boolean | — | <code>true</code> | If should stop when using tab key |
| `disabled` | Boolean | — | <code>false</code> | Disable delete button |
| `aria-close-label` | String | — | - | Accessibility label for the close button |
| `icon` | String | — | - | Adds an icon to the left of the tag. |
| `icon-pack` | String | mdi, fa, fas, far, fab, fad, fal | <code>mdi</code> | Icon pack to use |
| `icon-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the icon on the left side of tag, optional |
| `close-icon` | String | — | - | Replace times in close button with a customized icon. closable and attached props should be needed. |
| `close-icon-pack` | String | mdi, fa, fas, far, fab, fad, fal | <code>mdi</code> | Icon pack to use |
| `close-icon-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the close icon of tag, optional |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `close` | <code>event: Event</code> | Triggers when close/delete button is clicked or delete key is pressed |
| `click` | <code>event: Event</code> | Triggers when clicking the content of the tag |

### Slots
| Name | Description |
|------|-------------|
| `default` | Tag content |

---

## Taglist

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `attached` | Boolean | — | <code>false</code> | Tags inside are attached together |

### Slots
| Name | Description |
|------|-------------|
| `default` | Tags content |


## Progress

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String, Object | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-darkgrey</code> | Type (color) of the progress bar, optional |
| `size` | String | is-small, is-medium, is-large | — | Size of the progress bar, optional |
| `rounded` | Boolean | false, true | true | rounded style of the progress bar, optional |
| `value` | Number | — | — | The progress value, progress will be indeterminate if undefined. |
| `max` | Number | — | <code>100</code> | The maximum value for the progress bar. |
| `show-value` | Boolean | — | <code>false</code> | If the value should be displayed inside the progress bar. |
| `format` | String | raw, percent | <code>raw</code> | Which format should be used to display the value (if show-value is true). The value will be displayed as-is if using raw. The percent using value and max will be calculated and displayed if using percent |
| `precision` | Number | — | <code>2</code> | How many decimals should be displayed. |
| `keep-trailing-zeroes` | Boolean | — | <code>false</code> | Truncate or not the trailing zeroes |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |

### Slots
| Name | Description |
|------|-------------|
| `default` | This will be displayed inside the progress bar instead of the calculated value |
| `bar` | You can insert b-progress-bar components if you want to have multiple bars. |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `calculateValue` | Calculate and format the display value based on the current value, format, precision, and locale settings | <code>value: Number</code> | <code>String | undefined</code> |

---

## Bar

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | inherited from parent | Type (color) of the progress bar, optional |
| `value` | Number | — | — | The progress value. |
| `show-value` | Boolean | — | inherited from parent | If the value should be displayed inside the progress bar. |

### Slots
| Name | Description |
|------|-------------|
| `default` | This will be displayed inside the progress bar instead of the calculated value |


## Skeleton

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `active` | Boolean | — | <code>true</code> | Show or hide loader |
| `animated` | Boolean | — | <code>true</code> | Display a loading animation |
| `rounded` | Boolean | — | <code>true</code> | Rounded style |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of skeleton, optional |
| `width` | String, Number | — | <code>-</code> | Custom width |
| `height` | String, Number | — | <code>-</code> | Custom height |
| `circle` | Boolean | — | <code>false</code> | Show a circle shape |
| `count` | Number | — | <code>1</code> | Number of shapes to display |
| `position` | String | is-centered, is-right | — | Position of the skeleton, optional |


