# Form inputs

## Input

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | String, Number | — | — | Binding value |
| `lazy` | Boolean | — | <code>false</code> | Makes the binding lazy. Note: v-model.lazy won't work |
| `type` | String | Any native input type, and textarea | <code>text</code> | Input type, like native |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input, optional |
| `expanded` | Boolean | — | <code>false</code> | Makes input full width when inside a grouped or addon field |
| `password-reveal` | Boolean | — | <code>false</code> | Add the reveal password functionality |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `icon` | String | — | — | Icon name to be added |
| `icon-right` | String | — | — | Icon name to be added on the right side |
| `icon-clickable` | Boolean | — | <code>false</code> | Make the icon clickable |
| `icon-right-clickable` | Boolean | — | <code>false</code> | Make the icon right clickable |
| `icon-right-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger | — | Type (color) for the right icon |
| `rounded` | Boolean | — | <code>false</code> | Makes the input rounded |
| `autocomplete` | String | Any valid HTML5 autocomplete value | Uses global config <code>defaultInputAutocomplete</code> | Native HTML5 autocomplete attribute |
| `use-html5-validation` | Boolean | — | <code>true</code>. Can be changed via <code>defaultUseHtml5Validation</code> config option. | Enable HTML5 native validation |
| `locale` | String, Array | — | Uses global config <code>defaultLocale</code> | Accept a locale string to display date in certain language (month and days names). See Moment.js documentation for valid locales. This overrides the default locale assigned globally. |
| `status-icon` | Boolean | — | <code>true</code>. Can be changed via <code>defaultStatusIcon</code> config option. | Show status icon using field and variant prop |
| `maxlength` | String, Number | — | — | Same as native maxlength, plus character counter |
| `has-counter` | Boolean | — | <code>true</code> | Show character counter when maxlength prop is passed |
| `custom-class` | String | — | — | CSS classes to be applied on input |
| `validation-message` | String | — | — | The message which is shown when a validation error occurs |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;div&gt;, or either of &lt;input&gt; or &lt;textarea&gt; element. If true, they are applied to the root &lt;div&gt; element, which is compatible with Vue 2. |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: String|Number</code> | Triggers when the value is changed (Vue 3 v-model event) |
| `input` | <code>event: Event</code> | Native input event that bubbles up from the underlying input element |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `focus` | <code>event: $event</code> | Triggers when input has received focus |
| `blur` | <code>event: $event</code> | Triggers when input has lost focus |
| `icon-click` | <code>event: $event</code> | Triggers when the icon is clickable and have been clicked |
| `icon-right-click` | <code>event: $event</code> | Triggers when the right icon is clickable and have been clicked |
| `[any].native` | <code>event: $event</code> | Listen to any native event, e.g. click.native |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `checkHtml5Validity` | Check validation of HTML5 (add the message and type/color), also updates the isValid property | — | <code>isValid: Boolean</code> |
| `focus` | Set focus (internally uses the native .select() method) | — | — |


## Select

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Any | — | — | Binding value |
| `size` | String | is-small, is-medium, is-large | — | Size of the select, optional |
| `placeholder` | String | — | — | Text when nothing is selected |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the Select |
| `expanded` | Boolean | — | <code>false</code> | Select will be expanded (full-width) |
| `icon` | String | — | — | Icon name to be added |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `native-size` | Number | — | <code>4</code> | Same as native size |
| `multiple` | Boolean | — | <code>false</code> | Same as native multiple |
| `rounded` | Boolean | — | <code>false</code> | Makes the element rounded |
| `maxlength` | Number, String | — | — | Same as native maxlength, plus character counter |
| `use-html5-validation` | Boolean | — | <code>defaultUseHtml5Validation</code> config, <code>true</code> by default | Enable HTML5 native validation |
| `validation-message` | String | — | — | The message which is shown when a validation error occurs |
| `locale` | String, Array | — | <code>defaultLocale</code> config (which is <code>undefined</code> by default) | Locale to be used for form validation and date formatting |
| `status-icon` | Boolean | — | <code>defaultStatusIcon</code> config, <code>true</code> by default | Show status icon using field and variant prop |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether the class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying &lt;select&gt; element. If true, they are applied to the root &lt;div&gt; element, which is compatible with Buefy for Vue 2. |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Any</code> | Triggers when value is changed |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying select element |
| `focus` | <code>event: $event</code> | Triggers when input has received focus |
| `blur` | <code>event: $event</code> | Triggers when input has lost focus |
| `[any].native` | <code>event: $event</code> | Listen to any native event, e.g. click.native |

### Slots
| Name | Description |
|------|-------------|
| `default` | Option elements for the select |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `checkHtml5Validity` | Check validation of HTML5 (add the message and type/color), also updates the isValid property | — | <code>isValid: Boolean</code> |
| `focus` | Set focus | — | — |


## Autocomplete

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | String, Number | — | — | Binding value |
| `data` | Array<String>, Array<Number>, Array<Object> | — | — | Options / suggestions |
| `field` | String | — | <code>value</code> | Property of the object (if data is array of objects) to use as display text, and to keep track of selected option |
| `custom-formatter` | Function | — | — | Function to format an option to a string for display in the input as alternative to field prop) |
| `group-field` | String | — | — | Property of the object (if data is array of objects) to use as display text of group |
| `group-options` | String | — | — | Property of the object (if data is array of objects) to use as key to get items array of each group, optional |
| `clear-on-select` | Boolean | — | <code>false</code> | Clear input text on select |
| `open-on-focus` | Boolean | — | <code>false</code> | Open dropdown list on focus |
| `keep-first` | Boolean | — | <code>false</code> | The first option will always be pre-selected (easier to just hit enter or tab) |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input, optional |
| `expanded` | Boolean | — | <code>false</code> | Makes input full width when inside a grouped or addon field |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `rounded` | Boolean | — | <code>false</code> | Makes the input rounded |
| `icon` | String | — | — | Icon name to be added |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `confirm-keys` | Array | — | <code>["Tab", "Enter"]</code> | Array of keys (https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values) which will select an option when typing (default tab and enter) |
| `clearable` | Boolean | — | false | Add a button to clear the inputed text |
| `icon-right` | String | — | — | Icon name to be added on the right side |
| `icon-right-clickable` | Boolean | — | <code>false</code> | Makes the right icon clickable |
| `maxlength` | String, Number | — | — | Same as native maxlength, plus character counter |
| `check-infinite-scroll` | Boolean | — | <code>false</code> | Makes the component check if list reached scroll end and emit infinite-scroll event. |
| `keep-open` | Boolean | — | <code>false</code> | Keeps the dropdown open after selection |
| `max-height` | String, Number | — | <code>200px</code> | Max height of dropdown content |
| `dropdown-position` | String | top, bottom, auto | <code>auto</code> | Position of dropdown |
| `append-to-body` | Boolean | — | <code>false</code> | Append autocomplete content to body (prevents event bubbling) |
| `select-on-click-outside` | Boolean | — | <code>false</code> | Trigger the @select event for the first pre-selected option when clicking outside and keep-first is enabled |
| `selectable-header` | Boolean | — | <code>false</code> | Allows the header in the autocomplete to be selectable |
| `selectable-footer` | Boolean | — | <code>false</code> | Allows the footer in the autocomplete to be selectable |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying &lt;b-input&gt;. If true, they are applied to the root &lt;div&gt; element, which is compatible with Vue 2. |
| `type` | String | — | <code>text</code> | Input type |
| `autocomplete` | String | — | <code>off</code> | Native HTML5 autocomplete attribute |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: String|Number</code> | Triggers when the value is changed (Vue 3 v-model event) |
| `input` | <code>event: Event</code> | Native input event that bubbles up from the underlying input element |
| `select` | <code>option: String|Number|Object, event: $event</code> | Triggers when an option is selected or unset |
| `focus` | <code>event: $event</code> | Triggers when input has received focus |
| `blur` | <code>event: $event</code> | Triggers when input has lost focus |
| `typing` | <code>value: String</code> | Triggers when user is typing |
| `active` | <code>value: Boolean</code> | Triggers when dropdown is active |
| `[any].native` | <code>event: $event</code> | Listen to any native event, e.g. click.native |
| `infinite-scroll` | — | Triggers when .dropdown-list has reached scroll end |
| `select-header` | <code>event: $event</code> | Triggers when the header slot is selected |
| `select-footer` | <code>event: $event</code> | Triggers when the footer slot is selected |

### Slots
| Name | Description |
|------|-------------|
| `default` | — |
| `empty` | Show like an option if data array prop is empty |
| `header` | Show a custom header as first option |
| `footer` | Show a custom footer as last option |
| `group` | Control how the group header is output |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `checkHtml5Validity` | Check validation of HTML5 (add the message and type/color), also updates the isValid property | — | <code>isValid: Boolean</code> |
| `focus` | Set focus (internally uses the native .select() method) | — | — |
| `setSelected(selected: Any)` | Select an option by an object (same type of data property) | — | — |


## Checkbox

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Any | — | <code>false</code> | Binding value |
| `native-value` | Any | — | — | Same as native value |
| `indeterminate` | Boolean | — | — | Same as native indeterminate |
| `true-value` | Any | — | <code>true</code> | Overrides the returned value when it's checked |
| `false-value` | Any | — | <code>false</code> | Overrides the returned value when it's not checked |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `required` | Boolean | — | <code>false</code> | Same as native required |
| `name` | String | — | — | Same as native name |
| `size` | String | is-small, is-medium, is-large | — | Size of the control, optional |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the control, optional |
| `aria-labelledby` | String | — | — | Accessibility label to establish relationship between the checkbox and control label |
| `input-id` | String | — | — | String to set the inner input id |
| `autocomplete` | String | — | <code>on</code> | Native HTML5 autocomplete attribute |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the value of checkbox is changed (Vue 3 v-model event) |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `[any].native` | <code>event: $event</code> | Listen to any event using this syntax, e.g @click.native |

### Slots
| Name | Description |
|------|-------------|
| `default` | Label content for the checkbox |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `focus()` | Set focus on the checkbox input | — | — |

---

## Button

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Any | — | — | Binding value |
| `native-value` | Any | — | — | Same as native value |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the button when checked |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `required` | Boolean | — | <code>false</code> | Same as native required |
| `name` | String | — | — | Same as native name |
| `size` | String | is-small, is-medium, is-large | — | Size of the button, optional |
| `expanded` | Boolean | — | <code>false</code> | Checkbox button will be expanded (full-width) |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Any</code> | Triggers when the value of checkbox button is changed (Vue 3 v-model event) |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `[any].native` | <code>event: $event</code> | Listen to any event using this syntax, e.g @click.native |

### Slots
| Name | Description |
|------|-------------|
| `default` | Button content for the checkbox button |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `focus()` | Set focus on the checkbox button input | — | — |


## Radio

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Any | — | — | Binding value |
| `native-value` | Any | — | — | Same as native value |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `required` | Boolean | — | <code>false</code> | Same as native required |
| `name` | String | — | — | Same as native name |
| `size` | String | is-small, is-medium, is-large | — | Size of the control, optional |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the control, optional |
| `required` | Boolean | — | <code>false</code> | Same as native required |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Any</code> | Triggers when the value of radio is changed |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `[any].native` | <code>event: $event</code> | Listen to any event using this syntax, e.g click.native |

### Slots
| Name | Description |
|------|-------------|
| `default` | Radio label content |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `focus` | Set focus on the radio input element | — | — |

---

## Button

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Any | — | — | Binding value |
| `native-value` | Any | — | — | Same as native value |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the button when checked |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `name` | String | — | — | Same as native name |
| `size` | String | is-small, is-medium, is-large | — | Size of the button, optional |
| `expanded` | Boolean | — | <code>false</code> | Radio button will be expanded (full-width) |
| `required` | Boolean | — | <code>false</code> | Same as native required |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Any</code> | Triggers when the value of radio button is changed |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `[any].native` | <code>event: $event</code> | Listen to any event using this syntax, e.g click.native |

### Slots
| Name | Description |
|------|-------------|
| `default` | Radio button content |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `focus` | Set focus on the radio button input element | — | — |


## Switch

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the switch, optional |
| `passive-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the switch when switch is passive, optional |
| `v-model` | Any | — | <code>false</code> | Binding value |
| `native-value` | Any | — | — | Same as native value |
| `true-value` | Any | — | <code>true</code> | Overrides the returned value when it's checked |
| `false-value` | Any | — | <code>false</code> | Overrides the returned value when it's not checked |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `name` | String | — | — | Same as native name |
| `size` | String | is-small, is-medium, is-large | — | Size of the control, optional |
| `rounded` | Boolean | — | <code>true</code> | Rounded style |
| `outlined` | Boolean | — | <code>false</code> | Outlined style |
| `aria-labelledby` | String | — | — | Accessibility label to establish relationship between the switch and control label |
| `required` | Boolean | — | <code>false</code> | Same as native required |
| `left-label` | Boolean | — | <code>false</code> | Label is shown on the left side |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the value of the switch is changed |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `[any].native` | <code>event: $event</code> | Listen to any event using this syntax, e.g click.native |

### Slots
| Name | Description |
|------|-------------|
| `default` | Switch label |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `focus` | Focus the switch | — | void |


## Slider

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Number, Array | — | — | Binding value |
| `min` | Number | — | <code>0</code> | Minimum value |
| `max` | Number | — | <code>100</code> | Maximum value |
| `step` | Number | — | <code>1</code> | Step interval of ticks |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | is-primary | Type (color) of the slider, optional |
| `size` | String | is-small, is-medium, is-large | — | Thickness of the slider, optional |
| `ticks` | Boolean | — | <code>false</code> | Show tick marks |
| `tooltip` | Boolean | — | <code>false</code> | Show tooltip when thumb is being dragged |
| `indicator` | Boolean | — | <code>true</code> | Show v-model value inside thumb |
| `tooltip-type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>type</code> | The type (color) of the tooltip. Defaults to type |
| `rounded` | Boolean | — | <code>false</code> | Rounded thumb |
| `disabled` | Boolean | — | <code>false</code> | Disable the slider |
| `custom-formatter` | Function | — | — | Function to format the tooltip label for display |
| `format` | String | raw, percent | <code>raw</code> | Which format should be used to display the value. The value will be displayed as-is if using raw. The percent using value, min and max will be calculated and displayed if using percent |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |
| `aria-label` | String, Array | — | — | Accessibility label for the thumbs |
| `bigger-slider-focus` | Boolean | — | <code>false</code> | Increase the clickable area |
| `tooltip-always` | Boolean | — | <code>false</code> | Tooltip displays always |
| `lazy` | Boolean | — | <code>false</code> | Only emit modelValue on dragend, not during dragging |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Number|Array</code> | Triggers when value is changed |
| `change` | <code>value: Number|Array</code> | Triggers when value is changed after user interaction |
| `dragstart` | — | Triggers when thumb is pressed |
| `dragend` | — | Triggers when thumb is released |
| `dragging` | <code>value: Number|Array</code> | Triggers when thumb is being dragged |

### Slots
| Name | Description |
|------|-------------|
| `default` | Use SliderTick for custom ticks and labels |

---

## SliderTick

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `value` | Number | — | — | The value that the tick represents |

### Slots
| Name | Description |
|------|-------------|
| `default` | Label |


## Numberinput

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | String, Number | — | — | Binding value |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the control, optional |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input, optional |
| `expanded` | Boolean | — | <code>false</code> | Makes input full width when inside a grouped or addon field |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `editable` | Boolean | — | <code>true</code> | Editable input |
| `icon-pack` | String | mdi, fa, fas, far, fab, fad, fal | <code>mdi</code> | Icon pack to use |
| `min` | Number, String | — | — | Minimum allowed value |
| `max` | Number, String | — | — | Maximum allowed value |
| `step` | Number, String | — | 1 | Incremental number step |
| `min-step` | Number, String | — | Defaults to value of <code>step</code> | Minimum step-size allowed. Input value is validated to be integer multiple of min-step |
| `exponential` | Boolean, Number | Between 0 excluded and 10, setting to true is equivalent to passing true | false | The factor of incrementation on long press |
| `controls` | Boolean | — | <code>true</code> | Show controls (+/-) |
| `controls-rounded` | Boolean | — | <code>false</code> | Show rounded controls |
| `controls-position` | String | compact | — | Position of controls |
| `controls-alignment` | String | left, right, center | <code>center</code> | Alignment of controls |
| `aria-minus-label` | String | — | — | Accessibility label for the minus button. |
| `aria-plus-label` | String | — | — | Accessibility label for the plus button. |
| `long-press` | Boolean | — | <code>true</code> | Long press on the plus or minus button will increment/decrement the input value. |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `placeholder` | Number, String | — | — | Same as native placeholder |
| `autocomplete` | String | — | — | Same as native autocomplete |
| `rounded` | Boolean | — | <code>false</code> | Makes the element rounded |
| `maxlength` | Number, String | — | — | Same as native maxlength, plus character counter |
| `use-html5-validation` | Boolean | — | <code>defaultUseHtml5Validation</code> config, <code>true</code> by default | Enable HTML5 native validation |
| `validation-message` | String | — | — | The message which is shown when a validation error occurs |
| `locale` | String, Array | — | <code>defaultLocale</code> config (which is <code>undefined</code> by default) | Locale to be used for form validation and date formatting |
| `status-icon` | Boolean | — | <code>defaultStatusIcon</code> config, <code>true</code> by default | Show status icon using field and variant prop |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether the class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying &lt;b-input&gt; component. If true, they are applied to the root &lt;div&gt; element, which is compatible with Buefy for Vue 2. |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Number|null</code> | Triggers when value is changed |
| `input` | <code>value: String|Number</code> | Triggers when value is changed |
| `focus` | <code>event: $event</code> | Triggers when input has received focus |
| `blur` | <code>event: $event</code> | Triggers when input has lost focus |
| `[any].native` | <code>event: $event</code> | Listen to any native event, e.g. click.native |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `increment` | Programmatically increment the input value by the step amount | — | — |
| `decrement` | Programmatically decrement the input value by the step amount | — | — |
| `checkHtml5Validity` | Check validation of HTML5 (add the message and type/color), also updates the isValid property | — | <code>isValid: Boolean</code> |
| `focus` | Set focus (internally uses the native .select() method) | — | — |


## Datepicker

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Date | — | — | Binding value |
| `date-formatter` | Function | — | <code>(date) => new Intl.DateTimeFormat(locale, { timeZone: "UTC" }).format(date)</code> | Function to format date to a string for display in the input |
| `date-parser` | Function | — | Tries to parse the date using the locale specific format. Fallback to <code>Date.parse</code> | Function to parse string to a date for set a date from the input to the component |
| `date-creator` | Function | — | <code>() => new Date()</code> | Function used internally to create a new Date instance |
| `min-date` | Date | — | — | Earliest date available for selection |
| `max-date` | Date | — | — | Latest date available for selection |
| `events` | Array | — | — | Dates to display indicators |
| `indicators` | String | dots, bars | <code>dots</code> | Shape to use when showing event indicators |
| `focused-date` | Date | — | <code>new Date()</code> | Date that should be initially focused upon |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input and picker, optional |
| `inline` | Boolean | — | <code>false</code> | Datepicker is shown inline, input is removed |
| `editable` | Boolean | — | <code>false</code> | Enable input/typing. Note that you might have to set a custom date parser |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `icon` | String | — | — | Icon name to be added |
| `icon-right` | String | — | — | Icon name to be added on the right side |
| `icon-right-clickable` | Boolean | — | <code>false</code> | Make the right icon clickable |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `placeholder` | String | — | — | Input placeholder |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `horizontal-time-picker` | Boolean | — | <code>false</code> | Show time picker horizontal |
| `maxlength` | Number, String | — | — | Same as native maxlength, plus character counter |
| `use-html5-validation` | Boolean | — | <code>true</code> | Enable HTML5 native validation |
| `validation-message` | String | — | — | The message which is shown when a validation error occurs |
| `status-icon` | Boolean | — | <code>true</code> | Show status icon using field and variant prop |
| `icon-prev` | String | — | <code>chevron-left</code> | Icon to use for previous month |
| `icon-next` | String | — | <code>chevron-right</code> | Icon to use for next month |
| `unselectable-dates` | Array, Function | — | - | Array of unselectable dates, or a function to identify unselectable dates |
| `unselectable-days-of-week` | Array | 0 - 6 (Sunday is 0, Monday is 1, and so on) | - | Array of unselectable days of week |
| `selectable-dates` | Array, Function | — | - | Array of selectable dates, or a function to identify selectable dates |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |
| `month-names` | Array | — | <code>undefined</code>: default to browser locale. | Names of months to display in table header |
| `day-names` | Array | — | <code>undefined</code>: default to browser locale. | Names of days to display in table header |
| `first-day-of-week` | Number | 0 - 6 (Sunday is 0, Monday is 1, and so on) | <code>0</code> | First day of week to display in table header |
| `mobile-native` | Boolean | true, false | <code>true</code> | Enable native datepicker on mobile |
| `mobile-modal` | Boolean | true, false | <code>true</code> | Datepicker is shown into a modal on mobile |
| `position` | String | is-top-right, is-top-left, is-bottom-left | Bottom right | Optional, position of the datepicker relative to the input |
| `open-on-focus` | Boolean | — | <code>false</code> | Open datepicker on input focus |
| `type` | String | month | - | Type of picker |
| `years-range` | Array | - | <code>[-100, 3]</code> | Years range relative to selected year |
| `nearby-month-days` | Boolean | - | <code>true</code> | Show/Hide nearby month days (prev and next month) |
| `nearby-selectable-month-days` | Boolean | - | <code>false</code> | When nearby-month-days, it allows to select/unselect nearby month days |
| `show-week-number` | Boolean | - | <code>false</code> | Display week number |
| `week-number-clickable` | Boolean | - | <code>false</code> | Enable click on week number |
| `rules-for-first-week` | Number | - | <code>4</code> | Choose the rule to determinate the first week of Year, 4 for ISO or 1 for other |
| `range` | Boolean | — | <code>false</code> | Flag to allow choosing a range of date |
| `multiple` | Boolean | — | <code>false</code> | Flag to allow choosing multiple dates |
| `focusable` | Boolean | — | <code>true</code> | Datepicker container can be focused |
| `trap-focus` | Boolean | — | <code>true</code> | Trap focus inside the datepicker. |
| `close-on-click` | Boolean | - | <code>true</code> | Choose whether the Datepicker should close after selecting a date |
| `append-to-body` | Boolean | — | <code>false</code> | Append datepicker calendar to body (prevents event bubbling) |
| `aria-next-label` | String | — | — | Accessibility label for the next month button. |
| `aria-previous-label` | String | — | — | Accessibility label for the previous month button. |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying &lt;b-input&gt; component. If true, they are applied to the root &lt;div&gt; element, which is compatible with Buefy for Vue 2. |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Date | Date[] | null</code> | Triggers when the value of datepicker is changed |
| `active-change` | <code>active: Boolean</code> | Triggers when the datepicker visibility (active state) changes |
| `focus` | <code>event: Event</code> | Triggers when input receives focus |
| `blur` | <code>event: Event</code> | Triggers when input loses focus |
| `icon-right-click` | <code>event: $event</code> | Triggers when the right icon is clickable and has been clicked |
| `change-month` | <code>month: Number(0-11)</code> | Triggers when calendar month is changed |
| `change-year` | <code>year: Number</code> | Triggers when calendar year is changed |
| `range-start` | <code>date: Date</code> | Triggers when user starts selecting a date range (Only when range prop is set) |
| `range-end` | <code>date: Date</code> | Triggers when user ends selecting a date range (Only when range prop is set) |
| `week-number-click` | <code>week: Number</code> | Triggers when user click on week number (Only when show-week-number and week-number-clickable props are set) |

### Slots
| Name | Description |
|------|-------------|
| `default` | Footer |
| `header` | Header |
| `trigger` | Trigger |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggle` | Toggle activation (picker visibility) | — | — |
| `focus` | Set focus on the input element | — | — |
| `checkHtml5Validity` | Check HTML5 validation, set isValid property. If validation fails, send 'is-danger' type, and error message to parent if it's a Field | — | — |
| `togglePicker` | Toggle datepicker visibility with explicit active state | <code>active: Boolean</code> | — |


## Datetimepicker

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Date | — | — | Binding value |
| `datetime-formatter` | Function | — | <code>(time) => new Intl.DateTimeFormat(locale).format(time)</code> | Function to format datetime (Date type) to a string for displaying in the input |
| `datetime-parser` | Function | — | Tries to parse the time using the locale specific format. Fallback to <code>HH:mm</code> or <code>HH:mm AM/PM</code> | Function to parse string to a datetime (Date type) for setting the component's datetime from the input |
| `datetime-creator` | Function | — | <code>(date) => date</code> | Function used internally to create a new Date instance from a given date |
| `placeholder` | String | — | — | Input placeholder |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `rules-for-first-week` | Number | — | <code>4</code> | Choose the rule to determine the first week of year, 4 for ISO or 1 for other |
| `tz-offset` | Number | — | <code>0</code> | Timezone offset in minutes |
| `expanded` | Boolean | — | <code>false</code> | Makes input full width when inside a grouped or addon field |
| `rounded` | Boolean | — | <code>false</code> | Makes the input rounded |
| `maxlength` | Number, String | — | — | Same as native maxlength, plus character counter |
| `use-html5-validation` | Boolean | — | <code>true</code> | Enable HTML5 native validation |
| `validation-message` | String | — | — | The message which is shown when a validation error occurs |
| `status-icon` | Boolean | — | <code>true</code> | Show status icon using field and variant prop |
| `min-datetime` | Date | — | — | Earliest datetime available for selection |
| `max-datetime` | Date | — | — | Latest datetime available for selection |
| `first-day-of-week` | Number | 0 - 6 (Sunday is 0, Monday is 1, and so on) | <code>0</code> | First day of week to display in table header |
| `nearby-month-days` | Boolean | - | <code>true</code> | Show/Hide nearby month days (prev and next month) |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input and picker, optional |
| `inline` | Boolean | — | <code>false</code> | Datimepicker is shown inline, input is removed |
| `editable` | Boolean | — | <code>false</code> | Enable input/typing. Note that you might have to set a custom time parser |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `icon` | String | — | — | Icon name to be added |
| `icon-right` | String | — | — | Icon name to be added on the right side |
| `icon-right-clickable` | Boolean | — | <code>false</code> | Make the right icon clickable |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `mobile-native` | Boolean | — | <code>true</code> | Enable native datetimepicker on mobile |
| `position` | String | is-top-right, is-top-left, is-bottom-left | Bottom right | Optional, position of the timepicker relative to the input |
| `open-on-focus` | Boolean | — | <code>false</code> | Open timepicker on input focus |
| `datepicker` | Object | — | — | Any datepicker props |
| `timepicker` | Object | — | — | Any timepicker props |
| `focusable` | Boolean | — | <code>true</code> | Datetimepicker container can be focused |
| `horizontal-time-picker` | Boolean | — | <code>false</code> | Changes the time picker layout to a horizontal position |
| `append-to-body` | Boolean | — | <code>false</code> | Append datetimepicker calendar to body (prevents event bubbling) |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Date | null</code> | Triggers when the datetime value changes |
| `active-change` | <code>active: Boolean</code> | Triggers when the datetimepicker visibility (active state) changes |
| `focus` | <code>event: Event</code> | Triggers when input receives focus |
| `blur` | <code>event: Event</code> | Triggers when input loses focus |
| `icon-right-click` | <code>event: $event</code> | Triggers when the right icon is clickable and has been clicked |
| `change-month` | <code>month: Number(0-11)</code> | Triggers when calendar month is changed |
| `change-year` | <code>year: Number</code> | Triggers when calendar year is changed |

### Slots
| Name | Description |
|------|-------------|
| `left` | Left side of footer |
| `right` | Right side of footer |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggle` | Toggle activation (picker visibility) | — | — |
| `focus` | Set focus on the input element | — | — |
| `checkHtml5Validity` | Check HTML5 validation, set isValid property. If validation fails, send 'is-danger' type, and error message to parent if it's a Field | — | — |


## Timepicker

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Date | — | — | Binding value |
| `hour-format` | String | 12 or 24 | <code>undefined</code>: default to browser locale. | Hour format for input and display |
| `increment-hours` | Number | — | <code>1</code> | Step hours for select component |
| `increment-minutes` | Number | — | <code>1</code> | Step minutes for select component |
| `increment-seconds` | Number | — | <code>1</code> | Step seconds for select component |
| `time-formatter` | Function | — | <code>(time) => new Intl.DateTimeFormat(locale).format(time)</code> | Function to format time (Date type) to a string for display in the input |
| `time-parser` | Function | — | Tries to parse the time using the locale specific format. Fallback to <code>HH:mm</code> or <code>HH:mm AM/PM</code> | Function to parse string to a time (Date type) for set a time from the input to the component |
| `min-time` | Date | — | — | Earliest time available for selection |
| `max-time` | Date | — | — | Latest time available for selection |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input and picker, optional |
| `inline` | Boolean | — | <code>false</code> | Timepicker is shown inline, input is removed |
| `editable` | Boolean | — | <code>false</code> | Enable input/typing. Note that you might have to set a custom time parser |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `icon` | String | — | — | Icon name to be added |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `unselectable-times` | Array | — | - | Array of unselectable times (Date object) |
| `mobile-native` | Boolean | — | <code>true</code> | Enable native timepicker on mobile |
| `mobile-modal` | Boolean | true, false | <code>true</code> | Timepicker is shown into a modal on mobile |
| `position` | String | is-top-right, is-top-left, is-bottom-left | Bottom right | Optional, position of the timepicker relative to the input |
| `open-on-focus` | Boolean | — | <code>false</code> | Open timepicker on input focus |
| `enable-seconds` | Boolean | - | <code>false</code> | Show seconds picker |
| `default-minutes` | Number | - | - | Default value when hours change |
| `default-seconds` | Number | - | - | Default value when hours or minutes change |
| `time-creator` | Function | — | <code>() => new Date()</code> | Function used internally to create a new Date instance |
| `focusable` | Boolean | — | <code>true</code> | Timepicker container can be focused |
| `append-to-body` | Boolean | — | <code>false</code> | Append timepicker calendar to body (prevents event bubbling) |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |
| `reset-on-meridian-change` | Boolean | — | <code>false</code> | Reset timepicker values on meridian change |
| `tz-offset` | Number | — | <code>0</code> | Timezone offset in minutes |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying input component. If true, they are applied to the root &lt;div&gt; element, which is compatible with Vue 2. |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Date</code> | Triggers when the time is changed |

### Slots
| Name | Description |
|------|-------------|
| `default` | Footer |
| `trigger` | Trigger |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Close dropdown | — | void |
| `toggle` | Toggle the dropdown open/closed | <code>active?: Boolean</code> | void |


## Clockpicker

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Date | — | — | Binding value |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the button when checked |
| `hour-format` | String | 12 or 24 | <code>undefined</code>: default to browser locale. | Hour format for input and display |
| `increment-minutes` | Number | — | <code>5</code> | Unit for increment minutes |
| `picker-size` | Number | — | <code>290</code> | Size of the clock face |
| `placeholder` | String | — | — | Input placeholder |
| `expanded` | Boolean | — | <code>false</code> | Makes input full width when inside a grouped or addon field |
| `rounded` | Boolean | — | <code>false</code> | Makes the input rounded |
| `maxlength` | Number, String | — | — | Same as native maxlength, plus character counter |
| `use-html5-validation` | Boolean | — | <code>true</code> | Enable HTML5 native validation |
| `validation-message` | String | — | — | The message which is shown when a validation error occurs |
| `status-icon` | Boolean | — | <code>true</code> | Show status icon using field and variant prop |
| `time-creator` | Function | — | <code>() => new Date()</code> | Function used internally to create a new Date instance |
| `increment-hours` | Number | — | <code>1</code> | Hour interval for increment |
| `increment-seconds` | Number | — | <code>1</code> | Second interval for increment |
| `enable-seconds` | Boolean | — | <code>false</code> | Enable seconds selection |
| `default-minutes` | Number | — | — | Default minutes to set when selecting an hour |
| `default-seconds` | Number | — | — | Default seconds to set when selecting a minute |
| `focusable` | Boolean | — | <code>true</code> | Clockpicker container can be focused |
| `tz-offset` | Number | — | <code>0</code> | Timezone offset |
| `reset-on-meridian-change` | Boolean | — | <code>false</code> | Reset time selection when meridian (AM/PM) changes |
| `time-formatter` | Function | — | <code>(time) => new Intl.DateTimeFormat(locale).format(time)</code> | Function to format time (Date type) to a string for display in the input |
| `time-parser` | Function | — | Tries to parse the time using the locale specific format. Fallback to <code>HH:mm</code> or <code>HH:mm AM/PM</code> | Function to parse string to a time (Date type) for set a time from the input to the component |
| `min-time` | Date | — | — | Earliest time available for selection |
| `max-time` | Date | — | — | Latest time available for selection |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input, optional |
| `inline` | Boolean | — | <code>false</code> | Clockpicker is shown inline, input is removed |
| `editable` | Boolean | — | <code>false</code> | Enable input/typing. Note that you might have to set a custom time parser |
| `disabled` | Boolean | — | <code>false</code> | Disables the input field and/or picker |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the input |
| `icon` | String | — | — | Icon name to be added |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `unselectable-times` | Array | — | - | Array of unselectable times (Date object) |
| `mobile-native` | Boolean | true, false | <code>true</code> | Enable native timepicker on mobile |
| `mobile-modal` | Boolean | true, false | <code>true</code> | Clockpicker is shown into a modal on mobile |
| `position` | String | is-top-right, is-top-left, is-bottom-left | <code>Bottom Right</code> | Optional, position of the timepicker relative to the input |
| `auto-switch` | Boolean | true, false | <code>true</code> | Automatically switches between hour and minutes selection after click |
| `open-on-focus` | Boolean | — | <code>false</code> | Open clockpicker on input focus |
| `hours-label` | String | — | <code>Hours</code> | Label to show on hour button |
| `minutes-label` | String | — | <code>Min</code> | Label to show on minutes button |
| `append-to-body` | Boolean | — | <code>false</code> | Append clockpicker calendar to body (prevents event bubbling) |
| `locale` | String, Array of String | — | <code>undefined</code>: default to browser locale. | Accept a string with a BCP 47 language tag, or an array of such strings. See Unicode BCP 47 locale identifier |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via <code>defaultCompatFallthrough</code> config option. | Whether class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying input component. If true, they are applied to the root &lt;div&gt; element, which is compatible with Vue 2. |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Date | null</code> | Triggers when the time value changes |
| `focus` | <code>event: Event</code> | Triggers when input receives focus |
| `blur` | <code>event: Event</code> | Triggers when input loses focus |

### Slots
| Name | Description |
|------|-------------|
| `default` | Footer |
| `trigger` | Trigger |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `toggle` | Toggle clockpicker visibility | <code>active: Boolean</code> | — |
| `close` | Close dropdown | — | — |
| `focus` | Set focus on the input element | — | — |
| `checkHtml5Validity` | Check HTML5 validation, set isValid property. If validation fails, send 'is-danger' type, and error message to parent if it's a Field | — | — |


## Colorpicker

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Object (Color) | — | — | Binding value |
| `representation` | String | triangle, square | <code>"triangle"</code> | Representation of Saturation & Lightness values |
| `alpha` | Boolean | — | <code>false</code> | Allow color with transparency |
| `color-formatter` | Function | — | <code>(color) => color.toString('hex')</code> | Function to format color to a string for display in the button |
| `color-parser` | Function | — | <code>(color) => Color.parse(color)</code> | Function to parse value to a color |
| `size` | String | is-small, is-medium, is-large | — | Vertical size of input and picker, optional |
| `inline` | Boolean | — | <code>false</code> | Colorpicker is shown inline, button is removed |
| `position` | String | is-top-right, is-top-left, is-bottom-left | Bottom right | Optional, position of the colorpicker relative to the button |
| `open-on-focus` | Boolean | — | <code>false</code> | Open colorpicker on button focus |
| `focusable` | Boolean | — | <code>true</code> | Colorpicker container can be focused |
| `trap-focus` | Boolean | — | <code>true</code> | Trap focus inside the colorpicker. |
| `close-on-click` | Boolean | - | <code>true</code> | Choose whether the Colorpicker should close after selecting a color |
| `append-to-body` | Boolean | — | <code>false</code> | Append colorpicker dropdown to body (prevents event bubbling) |
| `mobile-native` | Boolean | — | <code>false</code> | Use native mobile color picker |
| `disabled` | Boolean | — | <code>false</code> | Disable the colorpicker |
| `horizontal-color-picker` | Boolean | — | <code>false</code> | Horizontal layout for the color picker |
| `expanded` | Boolean | — | <code>false</code> | Expand the trigger button (full-width) |
| `mobile-modal` | Boolean | — | From config | Use modal on mobile devices |
| `rounded` | Boolean | — | <code>false</code> | Make the trigger button rounded |
| `loading` | Boolean | — | <code>false</code> | Add loading state to the trigger button |
| `icon` | String | — | — | Icon name for the trigger button |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `maxlength` | String, Number | — | — | Same as native maxlength, plus character counter |
| `use-html5-validation` | Boolean | — | From config | Enable HTML5 validation |
| `validation-message` | String | — | — | Custom validation message |
| `locale` | String, Array | — | From config | Locale for validation messages |
| `status-icon` | Boolean | — | From config | Show status icon for validation |
| `Any native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Color</code> | Triggers when the value of colorpicker is changed (Vue 3 v-model event) |
| `active-change` | <code>active: Boolean</code> | Triggers when the colorpicker opens or closes |
| `focus` | <code>event: $event</code> | Triggers when colorpicker receives focus |
| `blur` | <code>event: $event</code> | Triggers when colorpicker loses focus |

### Slots
| Name | Description |
|------|-------------|
| `trigger` | Custom trigger button |
| `header` | Header content in the colorpicker dropdown |
| `footer` | Footer content in the colorpicker dropdown (default slot) |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `focus()` | Set focus on the colorpicker | — | — |
| `checkHtml5Validity()` | Check HTML5 validation, returns validation state | — | <code>Boolean</code> |
| `togglePicker(active: Boolean)` | Toggle colorpicker visibility | — | — |


## Taginput

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Array<String>, Array<Number>, Array<Object> | — | — | Binding value |
| `maxlength` | String, Number | — | — | Limits the length of each tag, plus character counter |
| `maxtags` | String, Number | — | — | Limits the number of tags, plus tag counter |
| `has-counter` | Boolean | — | <code>true</code> | Show counter when maxlength or maxtags props are passed |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-light</code> | Type (color) of the tags, optional |
| `closeType` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | - | Type (color) of the close icon, optional |
| `size` | String | is-small, is-medium, is-large | — | Tag and input size, optional |
| `rounded` | Boolean | — | <code>false</code> | Makes the tags rounded, optional |
| `attached` | Boolean | — | <code>false</code> | Makes the tags attached instead of having an appended delete button, optional |
| `ellipsis` | Boolean | — | <code>false</code> | Adds ellipsis on tags to not overflow the text. Title is then added to the tag with full text |
| `closable` | Boolean | — | <code>true</code> | Add close/delete button to the tag |
| `aria-close-label` | String | — | - | Accessibility label for the close button |
| `field` | String | — | <code>value</code> | Property of the object (if data is array of objects) to use as display text |
| `autocomplete` | Boolean | — | <code>false</code> | Add autocomplete feature (if true, any Autocomplete props may be used too) |
| `group-field` | String | — | — | Property of the object (if data is array of objects) to use as display text of group |
| `group-options` | String | — | — | Property of the object (if data is array of objects) to use as key to get items array of each group, optional |
| `allow-new` | Boolean | — | <code>false</code> | When autocomplete, it allow to add new tags |
| `open-on-focus` | Boolean | — | <code>false</code> | Opens a dropdown with choices when the input field is focused |
| `keep-open` | Boolean | — | <code>true</code> | Keep the dropdown list open after selecting |
| `keep-first` | Boolean | — | <code>false</code> | Keep the first option selected |
| `native-autocomplete` | String | — | — | Same as native autocomplete options to use in HTML5 validation |
| `remove-on-keys` | Array | — | <code>["Backspace"]</code> | Allow removing last tag when pressing given keys, if input is empty |
| `confirm-keys` | Array | — | <code>[",", "Tab", "Enter"]</code> | Array of keys (https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values) which will add a tag when typing (default comma, tab and enter) |
| `on-paste-separators` | Array | — | <code>[',']</code> | Array of chars used to split when pasting a new string |
| `before-adding` | Function | — | <code>(tagToAdd) => true</code> | Function to validate the value of the tag before adding |
| `allow-duplicates` | Boolean | — | <code>false</code> | Allows adding the same tag multiple times |
| `create-tag` | Function | — | <code>(tagToAdd) => tagToAdd</code> | Function to create tag item to push into v-model (tags) |
| `readonly` | Boolean | — | <code>false</code> | Disable input/typing |
| `check-infinite-scroll` | Boolean | — | <code>false</code> | Makes the autocomplete component check if list reached scroll end and emit infinite-scroll event. |
| `append-to-body` | Boolean | — | <code>false</code> | Append autocomplete content to body (prevents event bubbling) |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether the class, style, and id attributes are applied to the root &lt;div&gt; element or the underlying &lt;b-autocomplete&gt; component. If true, they are applied to the root &lt;div&gt; element, which is compatible with Buefy for Vue 2. |
| `Any other native attribute` | — | — | — | — |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Array</code> | Triggers when tags are added/removed |
| `typing` | <code>value: String</code> | User started typing a tag |
| `add` | <code>value: String|Object</code> | Triggers when a tag has been added |
| `remove` | <code>value: String|Object</code> | Triggers when a tag has been removed |
| `infinite-scroll` | — | Triggers when the autocomplete .dropdown-list has reached scroll end |

### Slots
| Name | Description |
|------|-------------|
| `default` | — |
| `empty` | Show like an option if data array prop is empty |
| `header` | Show a custom header as first option |
| `footer` | Show a custom footer as last option |
| `tag` | For customizing content in tag item. |
| `selected` | For customizing content of selected item. |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `addTag` | Add a tag programmatically | <code>tag?: String|Object</code> | void |
| `removeTag` | Remove tag at specific index | <code>index: Number, event?: Event</code> | String|Object |
| `removeLastTag` | Remove the last tag | — | void |


## Upload

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | File, Array<File> | — | [] | Binding value |
| `drag-drop` | Boolean | — | <code>false</code> | Accepts drag & drop and change its style |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the drag area when hovered |
| `disabled` | Boolean | — | <code>false</code> | Same as native disabled |
| `name` | String | — | - | Same as native name |
| `required` | Boolean | — | <code>false</code> | Same as native required |
| `accept` | String | — | - | Same as native accept |
| `loading` | Boolean | — | <code>false</code> | Add the loading state to the drag & drop area |
| `multiple` | Boolean | — | <code>false</code> | Same as native, also push new item to v-model instead of replacing |
| `native` | Boolean | — | <code>false</code> | Replace last chosen files every time (like native file input element) |
| `expanded` | Boolean | — | <code>false</code> | Upload will be expanded (full-width) |
| `rounded` | Boolean | — | <code>false</code> | Upload will be rounded |
| `compat-fallthrough` | Boolean | - | <code>true</code>. Can be changed via the <code>defaultCompatFallthrough</code> config option. | Whether the class, style, and id attributes are applied to the root &lt;label&gt; element or the underlying &lt;input&gt; element. If true, they are applied to the root &lt;label&gt; element, which is compatible with Buefy for Vue 2. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: File</code> or <code>File[]</code> | Triggers when the file list is changed |
| `change` | <code>event: Event</code> | Native change event that bubbles up from the underlying input element |
| `invalid` | — | Triggers when a file is rejected due to type validation |

### Slots
| Name | Description |
|------|-------------|
| `default` | Upload button/content area |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `checkHtml5Validity` | Check validation of HTML5 (add the message and type/color), also updates the isValid property | — | <code>isValid: Boolean</code> |


