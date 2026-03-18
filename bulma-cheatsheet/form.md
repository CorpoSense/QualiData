# Bulma Form

## Overview
Bulma form elements for user input.

## Checkbox

### Main Classes

| Class | Description |
|-------|-------------|
| `checkbox` | Checkbox input |

### Examples

**checkbox**:
```html
<label class="checkbox">
  <input type="checkbox" />
  Remember me
</label>
```

**checkbox_disabled**:
```html
<label class="checkbox" disabled>
  <input type="checkbox" disabled />
  Save my preferences
</label>
```

## File upload

## Form controls

### Main Classes

| Class | Description |
|-------|-------------|
| `button` | Submit/reset button |
| `checkbox` | Checkbox input |
| `control` | Input control wrapper |
| `field` | Form field wrapper |
| `help` | Form help text |
| `input` | Text input field |
| `label` | Form label |
| `radio` | Radio button input |
| `select` | Dropdown select |
| `textarea` | Multi-line text input |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-addons` | Has addons property |
| `has-addons-centered` | Has addons-centered property |
| `has-addons-right` | Has addons-right property |
| `has-icons-left` | Has icons-left property |
| `has-icons-right` | Has icons-right property |
| `is-danger` | danger color variant |
| `is-expanded` | Modifier class |
| `is-fullwidth` | fullwidth state |
| `is-grouped` | Modifier class |
| `is-grouped-centered` | Modifier class |
| `is-grouped-multiline` | Modifier class |
| `is-grouped-right` | Modifier class |
| `is-horizontal` | Modifier class |
| `is-info` | info color variant |
| `is-large` | large size |
| `is-left` | Modifier class |
| `is-light` | light color variant |
| `is-medium` | medium size |
| `is-narrow` | Modifier class |
| `is-normal` | normal size |
| `is-primary` | primary color variant |
| `is-right` | Modifier class |
| `is-small` | small size |
| `is-static` | static state |
| `is-success` | success color variant |

### Examples

**control**:
```html
<div class="control">
  <input class="input" type="text" placeholder="Text input">
</div>
```

**field**:
```html
<div class="field">
  <label class="label">Label</label>
  <div class="control">
    <input class="input" type="text" placeholder="Text input">
  </div>
  <p class="help">This is a help text</p>
</div>
```

**fields**:
```html
<div class="field">
  <label class="label">Name</label>
  <div class="control">
    <input class="input" type="text" placeholder="e.g Alex Smith">
  </div>
</div>

<div class="field">
  <label class="label">Email</label>
  <div class="control">
    <input class="input" type="email" placeholder="e.g. alexsmith@gmail.com">
  </div>
</div>
```

## Input

### Main Classes

| Class | Description |
|-------|-------------|
| `control` | Input control wrapper |
| `field` | Form field wrapper |
| `input` | Text input field |
| `label` | Form label |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-icons-left` | Has icons-left property |
| `has-icons-right` | Has icons-right property |
| `is-focused` | focused state |
| `is-horizontal` | Modifier class |
| `is-hovered` | hovered state |
| `is-large` | large size |
| `is-left` | Modifier class |
| `is-loading` | loading state |
| `is-medium` | medium size |
| `is-normal` | normal size |
| `is-right` | Modifier class |
| `is-rounded` | rounded state |
| `is-small` | small size |
| `is-static` | static state |

### Examples

**input**:
```html
<input class="input" type="text" placeholder="Text input" />
```

**rounded**:
```html
<input class="input is-rounded" type="text" placeholder="Rounded input" />
```

**normal**:
```html
<div class="control">
  <input class="input" type="text" placeholder="Normal input" />
</div>
```

## Radio button

### Main Classes

| Class | Description |
|-------|-------------|
| `control` | Input control wrapper |
| `radio` | Radio button input |

### Examples

**radio**:
```html
<div class="control">
  <label class="radio">
    <input type="radio" name="answer" />
    Yes
  </label>
  <label class="radio">
    <input type="radio" name="answer" />
    No
  </label>
</div>
```

**radio_disabled**:
```html
<div class="control">
  <label class="radio">
    <input type="radio" name="rsvp" />
    Going
  </label>
  <label class="radio">
    <input type="radio" name="rsvp" />
    Not going
  </label>
  <label class="radio" disabled>
    <input type="radio" name="rsvp" disabled />
    Maybe
  </label>
</div>
```

## Select

### Main Classes

| Class | Description |
|-------|-------------|
| `control` | Input control wrapper |
| `select` | Dropdown select |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-icons-left` | Has icons-left property |
| `is-disabled` | Modifier class |
| `is-focused` | focused state |
| `is-hovered` | hovered state |
| `is-large` | large size |
| `is-left` | Modifier class |
| `is-loading` | loading state |
| `is-medium` | medium size |
| `is-multiple` | Modifier class |
| `is-rounded` | rounded state |
| `is-small` | small size |

### Examples

**select**:
```html
<div class="select">
  <select>
    <option>Select dropdown</option>
    <option>With options</option>
  </select>
</div>
```

**select_multiple**:
```html
<div class="select is-multiple">
  <select multiple size="8">
    <option value="Argentina">Argentina</option>
    <option value="Bolivia">Bolivia</option>
    <option value="Brazil">Brazil</option>
    <option value="Chile">Chile</option>
    <option value="Colombia">Colombia</option>
    <option value="Ecuador">Ecuador</option>
    <option value="Guyana">Guyana</option>
    <option value="Paraguay">Paraguay</option>
    <option value="Peru">Peru</option>
    <option value="Suriname">Suriname</
```

**rounded**:
```html
<div class="select is-rounded">
  <select>
    <option>Rounded dropdown</option>
    <option>With options</option>
  </select>
</div>
```

## Textarea

### Main Classes

| Class | Description |
|-------|-------------|
| `control` | Input control wrapper |
| `field` | Form field wrapper |
| `textarea` | Multi-line text input |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-fixed-size` | Has fixed-size property |
| `is-danger` | danger color variant |
| `is-focused` | focused state |
| `is-hovered` | hovered state |
| `is-info` | info color variant |
| `is-large` | large size |
| `is-loading` | loading state |
| `is-medium` | medium size |
| `is-primary` | primary color variant |
| `is-small` | small size |
| `is-success` | success color variant |
| `is-warning` | warning color variant |

### Examples

**textarea**:
```html
<textarea class="textarea" placeholder="e.g. Hello world"></textarea>
```

**textarea_rows**:
```html
<textarea
  class="textarea"
  placeholder="10 lines of textarea"
  rows="10"
></textarea>
```

**colors**:
```html
<div class="field">
  <div class="control">
    <textarea
      class="textarea is-primary"
      placeholder="Primary textarea"
    ></textarea>
  </div>
</div>
<div class="field">
  <div class="control">
    <textarea class="textarea is-info" placeholder="Info textarea"></textarea>
  </div>
</div>
<div class="field">
  <div class="control">
    <textarea
      class="textarea is-success"
      placeholder="Success textarea"
    ></textarea>
  </div>
</div>
<div class="field">
  <div class="con
```

