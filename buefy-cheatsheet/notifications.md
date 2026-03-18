# Notifications

## Dialog

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-primary</code> | Type (color) of the confirm button (and the icon if hasIcon) |
| `title` | String | — | — | Dialog title |
| `message` | String, Array<VNode> | — | — | Message text (can contain HTML). Dynamically rendering arbitrary HTML on your website can be very dangerous because it can easily lead to XSS vulnerabilities. Only use HTML interpolation on trusted content and never on user-provided content. |
| `hasIcon` | Boolean | — | <code>false</code> | Adds an icon on the left side depending on the type or icon |
| `icon` | String | — | — | Icon name if hasIcon, optional |
| `iconPack` | String | mdi, fa, fas, far, fad, fal | — | Icon pack to use if hasIcon, optional |
| `size` | String | is-small, is-medium, is-large | — | Dialog's size, optional |
| `animation` | String | — | <code>zoom-out</code> | Custom animation (transition name) |
| `confirmText` | String | — | <code>OK</code> | Text of the confirm button |
| `cancelText` | String | — | <code>Cancel</code> | Text of the cancel button |
| `canCancel` | Boolean, Array | escape, button, outside | <code>true</code> for Confirm/Prompt, <code>false</code> for Alert | Can close dialog by clicking cancel button, pressing escape or clicking outside |
| `inputAttrs` | Object | Any HTML5 input attribute | — | Prompt only: input's attributes |
| `onConfirm` | Function (value: String, dialog: VueInstance) | — | — | Callback function when the confirm button is clicked |
| `closeOnConfirm` | Boolean | true, false | <code>true</code> | Turning this prop into false allows to make async requests in onConfirm callback |
| `onCancel` | Function | — | — | Callback function when the dialog is canceled (cancel button is clicked / pressed escape / clicked outside) |
| `scroll` | String | clip, keep | <code>clip</code> | clip to remove the &lt;body&gt; scrollbar, keep to have a non scrollable scrollbar to avoid shifting background, but will set &lt;body&gt; to position fixed, might break some layouts |
| `container` | String | — | <code>body</code> | DOM element the dialog will be created on. Note that this also changes the position of the dialog from fixed to absolute. Meaning that the container should be fixed. Also note that this will override the defaultContainerElement if you specified it in your Buefy Constructor Options. See Constructor options for more details. |
| `focusOn` | String | confirm, cancel | <code>confirm</code> | Focus on confirm or cancel button (when dialog is not prompt) |
| `trap-focus` | Boolean | — | <code>true</code> | Trap focus inside the dialog. |
| `aria-role` | String | dialog, alertdialog | — | Role attribute to be passed to modal container for better accessibility. |
| `aria-modal` | Boolean | — | <code>false</code> | Improve accessiblity when enabled. |
| `v-model` | Boolean | — | <code>false</code> | Binding value for dialog visibility |
| `width` | String, Number | — | <code>960</code> | Width of the dialog |
| `full-screen` | Boolean | — | <code>false</code> | Display dialog as full screen |
| `auto-focus` | Boolean | — | <code>true</code> | Automatically focus dialog when opened |
| `custom-class` | String | — | — | Custom class to apply to the dialog |
| `custom-content-class` | String, Array, Object | — | — | Custom class to apply to the dialog content |
| `aria-label` | String | — | — | Accessibility label for the dialog |
| `close-button-aria-label` | String | — | — | Accessibility label for the close button |
| `destroy-on-hide` | Boolean | — | <code>true</code> | Destroy dialog component when hidden |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `confirm` | <code>value: String, dialog: VueInstance</code> | Triggers when the confirm button is clicked |
| `cancel` | <code>method: String</code> | Triggers when the dialog is canceled |
| `close` | — | Triggers when the dialog is closed |
| `update:modelValue` | <code>active: Boolean</code> | Triggers when the dialog visibility changes (v-model event) |
| `after-enter` | — | Triggers after the dialog enter transition completes |
| `after-leave` | — | Triggers after the dialog leave transition completes |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `confirm` | Trigger the confirm action (validates input if prompt dialog) | — | — |
| `close` | Close the dialog | — | — |
| `cancel` | Cancel the dialog | <code>method: String</code> | — |
| `startLoading` | Start the loading state for the confirm button | — | — |
| `cancelLoading` | Cancel the loading state for the confirm button | — | — |


## Snackbar

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-success</code> | Type (color) of the action button. Please notice that it is the name of the parent class also |
| `message` | String, Array<VNode> | — | — | Message text (can contain HTML). Dynamically rendering arbitrary HTML on your website can be very dangerous because it can easily lead to XSS vulnerabilities. Only use HTML interpolation on trusted content and never on user-provided content. |
| `position` | String | is-top-right, is-top, is-top-left, is-bottom-right, is-bottom, is-bottom-left | <code>is-bottom-right</code> | Which position the snackbar will appear |
| `duration` | Number | — | <code>3500</code> | Visibility duration in miliseconds |
| `queue` | Boolean | — | <code>true</code> | If should queue with others notices (snackbar/toast/notification) |
| `indefinite` | Boolean | — | <code>false</code> | Show the Snackbar indefinitely until it is dismissed |
| `pause-on-hover` | Boolean | — | <code>false</code> | Pause and show on hover until hover off (it works when indefinite is false) |
| `container` | String | — | <code>body</code> | DOM element the toast will be created on. Note that this also changes the position of the toast from fixed to absolute. Meaning that the container should be fixed. Also note that this will override the defaultContainerElement if you specified it in your Buefy Constructor Options. See Constructor options for more details. |
| `actionText` | String | — | <code>OK</code> | Snackbar's button text, set null for buttonless |
| `onAction` | Function | — | — | Callback function when the button is clicked |
| `cancelText` | String | — | — | Snackbar's cancel button text. Default is no cancel button |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `click` | — | Triggers when the snackbar is clicked |
| `close` | — | Triggers when the snackbar is closed |

### Slots
| Name | Description |
|------|-------------|
| `default` | Custom content to replace the message text |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `open` | Opens the snackbar | String, Object | Reference to the opened Snackbar |
| `close` | Close the snackbar | — | — |


## Toast

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | <code>is-dark</code> | Type (color) of the toast |
| `message` | String, Array<VNode> | — | — | Message text (can contain HTML). Dynamically rendering arbitrary HTML on your website can be very dangerous because it can easily lead to XSS vulnerabilities. Only use HTML interpolation on trusted content and never on user-provided content. |
| `position` | String | is-top-right, is-top, is-top-left, is-bottom-right, is-bottom, is-bottom-left | <code>is-top</code> | Which position the toast will appear |
| `duration` | Number | — | <code>2000</code> | Visibility duration in milliseconds |
| `queue` | Boolean | — | <code>true</code> | If should queue with others notices (snackbar/toast/notification) |
| `indefinite` | Boolean | — | <code>false</code> | Show indefinitely until it is dismissed programmatically |
| `pause-on-hover` | Boolean | — | <code>false</code> | Pause and show on hover until hover off (it works when indefinite is false) |
| `container` | String | — | <code>body</code> | DOM element the toast will be created on. Note that this also changes the position of the toast from fixed to absolute. Meaning that the container should be fixed. Also note that this will override the defaultContainerElement if you specified it in your Buefy Constructor Options. See Constructor options for more details. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `click` | — | Triggers when the toast is clicked |
| `close` | — | Triggers when the toast is closed |

### Slots
| Name | Description |
|------|-------------|
| `default` | Toast content (overrides the message prop) |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Close the toast | — | void |


## Notification

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Boolean | — | true | Active state - set on "true" to reopen after close |
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the notification, optional |
| `title` | String | — | — | Notification title |
| `size` | String | is-small, is-medium, is-large | — | Size of the notification, optional |
| `closable` | Boolean | — | <code>true</code> | Adds an 'X' button that closes the notification |
| `auto-close` | Boolean | — | <code>false</code> | Hide notification after duration |
| `duration` | Number | — | <code>2000</code> | Visibility duration in miliseconds |
| `progress-bar` | Boolean | — | <code>false</code> | remaining seconds before the alert will close (in seconds) |
| `animation` | String | — | <code>fade</code> | Custom animation (transition name) |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `has-icon` | Boolean | — | <code>false</code> | Adds an icon on the left side depending on the type (or the icon prop if defined) |
| `icon` | Boolean | — | — | Icon name to use with has-icon |
| `icon-size` | String | is-small, is-medium, is-large | Depends on <code>size</code> prop | Size of the icon, optional |
| `aria-close-label` | String | — | — | Label for the close button, to be read by accessibility screenreaders. |
| `message` | String, Array<VNode> | — | — | Message text (can contain HTML). Dynamically rendering arbitrary HTML on your website can be very dangerous because it can easily lead to XSS vulnerabilities. Only use HTML interpolation on trusted content and never on user-provided content. |
| `position` | String | is-top-right, is-top, is-top-left, is-bottom-right, is-bottom, is-bottom-left | <code>is-top-right</code> | Which position the notification will appear when opened programmatically |
| `queue` | Boolean | — | <code>true</code> | If should queue with others notices (snackbar/toast/notification) |
| `indefinite` | Boolean | — | <code>false</code> | Show the Notification indefinitely until it is dismissed when opened programmatically |
| `pause-on-hover` | Boolean | — | <code>false</code> | Pause and show on hover until hover off when opened programmatically, if indefinite is false. |
| `container` | String | — | <code>body</code> | DOM element the toast will be created on. Note that this also changes the position of the toast from fixed to absolute. Meaning that the container should be fixed. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the notification visibility changes |
| `close` | — | Triggers when user closes the notification |
| `click` | — | Triggers when user clicks the notification |

### Slots
| Name | Description |
|------|-------------|
| `default` | Main notification content |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Programmatically close the notification | — | — |


## Message

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `type` | String | is-white, is-black, is-light, is-dark, is-primary, is-info, is-success, is-warning, is-danger, and any other colors you've set in the $colors list on Sass | — | Type (color) of the message, optional |
| `v-model` | Boolean | — | <code>true</code> | Whether message is active or not |
| `message` | String | — | — | Message text content |
| `closable` | Boolean | — | <code>true</code> | Adds an 'X' button that closes the notification — works if has a title |
| `auto-close` | Boolean | — | <code>false</code> | Hide notification after duration |
| `duration` | Number | — | <code>2000</code> | Visibility duration in miliseconds |
| `progress-bar` | Boolean | — | <code>false</code> | remaining seconds before the alert will close (in seconds) |
| `icon-pack` | String | mdi, fa, fas, far, fad, fal | <code>mdi</code> | Icon pack to use |
| `has-icon` | Boolean | — | <code>false</code> | Adds an icon on the left side depending on the type (or the icon prop if defined) |
| `icon` | Boolean | — | — | Icon name to use with has-icon |
| `size` | String | is-small, is-medium, is-large | — | Size of the control, optional |
| `icon-size` | String | is-small, is-medium, is-large | <code>is-large</code> or <code>size</code> prop | Size of the icon, optional |
| `title` | String | — | — | Message title |
| `aria-close-label` | String | — | — | Label for the close button, to be read by accessibility screenreaders. |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `close` | — | Triggers when user closes the message |
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the message visibility changes |
| `click` | — | Triggers when the message is clicked |

### Slots
| Name | Description |
|------|-------------|
| `default` | Main message content |
| `header` | Message custom header |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Programmatically close the message | — | — |


## Modal

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Boolean | — | <code>false</code> | Whether modal is active or not |
| `component` | Object, Function | — | — | Component to be injected, used to open a component modal programmatically. Close modal within the component by emitting a 'close' event — this.$emit('close') |
| `programmatic` | Boolean | — | <code>false</code> | Indicates if the modal was created programmatically |
| `props` | Object | — | — | Props to be binded to the injected component |
| `events` | Object | — | — | Events to be binded to the injected component |
| `content` | String, Array<VNode> | — | — | HTML content Dynamically rendering arbitrary HTML on your website can be very dangerous because it can easily lead to XSS vulnerabilities. Only use HTML interpolation on trusted content and never on user-provided content. |
| `width` | Number, String | — | <code>960</code> | Width of the Modal |
| `full-screen` | Boolean | — | <code>false</code> | Display modal as full screen |
| `has-modal-card` | Boolean | — | <code>false</code> | If your modal content has a .modal-card as root, add this prop or the card might break on mobile |
| `animation` | String | — | <code>zoom-out</code> | Custom animation (transition name) |
| `can-cancel` | Boolean, Array | escape, x, outside | <code>['escape', 'x', 'outside']</code> | Can close Modal by clicking 'X', pressing escape or clicking outside |
| `on-cancel` | Function | — | — | Callback function to call after user canceled (clicked 'X' / pressed escape / clicked outside) |
| `scroll` | String | clip, keep | <code>clip</code> | clip to remove the &lt;body&gt; scrollbar, keep to have a non scrollable scrollbar to avoid shifting background, but will set &lt;body&gt; to position fixed, might break some layouts |
| `trap-focus` | Boolean | — | <code>true</code> | Trap focus inside the modal. |
| `auto-focus` | Boolean | — | <code>true</code> | Automatically focus modal when active. |
| `custom-class` | String | — | — | CSS classes to be applied on modal |
| `custom-content-class` | String, Array, Object | — | — | CSS classes to be applied on modal content |
| `destroy-on-hide` | Boolean | — | <code>true</code> | Destroy modal on hide |
| `aria-role` | String | dialog, alertdialog | — | Role attribute to be passed to modal container for better accessibility. |
| `aria-label` | String | — | — | Aria label attribute to be passed to modal container for better accessibility. |
| `aria-modal` | Boolean | — | <code>false</code> | Improve accessiblity when enabled. |
| `close-button-aria-label` | String | — | — | Aria label attribute to be passed to the close button for better accessibility. |
| `render-on-mounted` | Boolean | - | <code>false</code> | Create DOM for the modal content whether modal is active or not |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `close` | — | Triggers when user closed/canceled or called programmatically from the injected component |
| `after-enter` | — | Triggers when the modal transition after-enter hook is called. |
| `after-leave` | — | Triggers when the modal transition after-leave hook is called. |
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the modal visibility changes |
| `cancel` | <code>method: String</code> - The cancellation method (escape, x, outside) | Triggers when user cancels the modal (escape, x, or outside click) |

### Slots
| Name | Description |
|------|-------------|
| `default` | Modal content |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Programmatically close the modal | — | — |
| `cancel` | Programmatically cancel the modal with a specific method | <code>method: String</code> - The cancellation method (escape, x, outside) | — |


## Loading

### Props
| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| `v-model` | Boolean | — | <code>false</code> | Whether loading is active or not |
| `programmatic` | Boolean | — | <code>false</code> | Indicates if the loading was created programmatically |
| `container` | Object, Function, HTMLElement | — | <code>document.body</code> | DOM element where the loading component will be created on (for programmatic usage) |
| `animation` | String | — | <code>fade</code> | Custom animation (transition name) |
| `is-full-page` | Boolean | — | <code>true</code> | Loader will overlay the full page |
| `can-cancel` | Boolean | — | <code>false</code> | Can close Loading by pressing escape or clicking outside |
| `on-cancel` | Function | — | — | Callback function to call after user canceled (pressed escape / clicked outside) |

### Events
| Name | Parameters | Description |
|------|------------|-------------|
| `close` | — | Triggers when user closed/canceled or called programmatically from the injected component |
| `update:modelValue` | <code>value: Boolean</code> | Triggers when the loading state changes |
| `update:is-full-page` | <code>value: Boolean</code> | Triggers when the full-page state changes |

### Slots
| Name | Description |
|------|-------------|
| `default` | Loading icon |

### Methods
| Name | Description | Parameters | Return |
|------|-------------|------------|--------|
| `close` | Programmatically close the loading overlay | — | — |


