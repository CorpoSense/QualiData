# Bulma Elements

## Overview
Bulma elements are basic building blocks for your web interface.

## Block

### Main Classes

| Class | Description |
|-------|-------------|
| `block` | Spacer element |

### Examples

**block**:
```html
<div class="block">
  This text is within a <strong>block</strong>.
</div>
<div class="block">
  This text is within a <strong>second block</strong>. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean efficitur sit amet massa fringilla egestas. Nullam condimentum luctus turpis.
</div>
<div class="block">
  This text is within a <strong>third block</strong>. This block has no margin at the bottom.
</div>
```

**no_block**:
```html
<div>
  This text is <em>not</em> within a <strong>block</strong>.
</div>
<div>
  This text <em>isn't</em> within a <strong>block</strong> either. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean efficitur sit amet massa fringilla egestas. Nullam condimentum luctus turpis.
</div>
<div>
  This text is also <em>not</em> within a <strong>block</strong>.
</div>
```

## Box

### Main Classes

| Class | Description |
|-------|-------------|
| `box` | Container with padding and shadow |
| `button` | Interactive button element |
| `content` | Rich text content wrapper |
| `icon` | Icon container |
| `image` | Image container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-64x64` | Modifier class |
| `is-mobile` | Modifier class |
| `is-primary` | primary color variant |
| `is-small` | small size |

### Examples

**box**:
```html
<div class="box">I'm in a box.</div>
```

**box_form**:
```html
<form class="box">
  <div class="field">
    <label class="label">Email</label>
    <div class="control">
      <input class="input" type="email" placeholder="e.g. alex@example.com" />
    </div>
  </div>

  <div class="field">
    <label class="label">Password</label>
    <div class="control">
      <input class="input" type="password" placeholder="********" />
    </div>
  </div>

  <button class="button is-primary">Sign in</button>
</form>
```

**box_card**:
```html
<div class="box">
  <article class="media">
    <div class="media-left">
      <figure class="image is-64x64">
        <img src="{{site.url}}/assets/images/placeholders/128x128.png" alt="Image" />
      </figure>
    </div>
    <div class="media-content">
      <div class="content">
        <p>
          <strong>John Smith</strong> <small>@johnsmith</small>
          <small>31m</small>
          <br />
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean
          efficitur sit amet massa fringilla egestas. Nullam condimentum luctus
          turpis.
        </p>
      </d
```

## Button

### Main Classes

| Class | Description |
|-------|-------------|
| `button` | Interactive button element |
| `buttons` | Container for button groups |
| `icon` | Icon container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `are-medium` | medium size for buttons container |
| `are-small` | small size for buttons container |
| `has-addons` | Has addons property |
| `is-active` | active state |
| `is-black` | black color variant |
| `is-danger` | danger color variant |
| `is-dark` | dark color variant |
| `is-focused` | focused state |
| `is-fullwidth` | fullwidth state |
| `is-ghost` | ghost color variant |
| `is-grouped` | Modifier class |
| `is-hovered` | hovered state |
| `is-info` | info color variant |
| `is-inverted` | inverted state |
| `is-large` | large size |
| `is-light` | light color variant |
| `is-link` | link color variant |
| `is-loading` | loading state |
| `is-medium` | medium size |
| `is-normal` | normal size |
| `is-outlined` | outlined state |
| `is-primary` | primary color variant |
| `is-rounded` | rounded state |
| `is-small` | small size |
| `is-static` | static state |
| `is-success` | success color variant |
| `is-text` | text color variant |
| `is-warning` | warning color variant |
| `is-white` | white color variant |

### Examples

**button**:
```html
<button class="button">Button</button>
```

**button_tags**:
```html
<a class="button">Anchor</a>
<button class="button">Button</button>
<input class="button" type="submit" value="Submit input" />
<input class="button" type="reset" value="Reset input" />
```

**button_colors_a**:
```html
<button class="button is-white">White</button>
<button class="button is-light">Light</button>
<button class="button is-dark">Dark</button>
<button class="button is-black">Black</button>
<button class="button is-text">Text</button>
<button class="button is-ghost">Ghost</button>
```

**button_colors_b**:
```html
<div class="buttons">
  <button class="button is-primary">Primary</button>
  <button class="button is-link">Link</button>
</div>

<div class="buttons">
  <button class="button is-info">Info</button>
  <button class="button is-success">Success</button>
  <button class="button is-warning">Warning</button>
  <button class="button is-danger">Danger</button>
</div>
```

## Content

### Main Classes

| Class | Description |
|-------|-------------|
| `content` | Rich text content wrapper |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-large` | large size |
| `is-lower-alpha` | Modifier class |
| `is-lower-roman` | Modifier class |
| `is-medium` | medium size |
| `is-normal` | normal size |
| `is-small` | small size |
| `is-upper-alpha` | Modifier class |
| `is-upper-roman` | Modifier class |

### Examples

**content**:
```html
<div class="content">
  <h1>Hello World</h1>
  <p>
    Lorem ipsum<sup><a>[1]</a></sup> dolor sit amet, consectetur adipiscing
    elit. Nulla accumsan, metus ultrices eleifend gravida, nulla nunc varius
    lectus, nec rutrum justo nibh eu lectus. Ut vulputate semper dui. Fusce erat
    odio, sollicitudin vel erat vel, interdum mattis neque. Sub<sub>script</sub>
    works as well!
  </p>
  <h2>Second level</h2>
  <p>
    Curabitur accumsan turpis pharetra <strong>augue tincidunt</strong> blandit.
    Quisque condimentum maximus mi, sit amet commodo arcu rutrum id. Proin
    pretium urna vel c
```

**content_ol_html**:
```html
<div class="content">
  <ol type="1">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol type="A">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol type="a">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol type="I">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol type="i">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
</div>
```

**content_ol_css**:
```html
<div class="content">
  <ol class="is-lower-alpha">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol class="is-lower-roman">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol class="is-upper-alpha">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
  <ol class="is-upper-roman">
    <li>Coffee</li>
    <li>Tea</li>
    <li>Milk</li>
  </ol>
</div>
```

**small**:
```html
<div class="content is-small">
  <h1>Hello World</h1>
  <p>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla accumsan,
    metus ultrices eleifend gravida, nulla nunc varius lectus, nec rutrum justo
    nibh eu lectus. Ut vulputate semper dui. Fusce erat odio, sollicitudin vel
    erat vel, interdum mattis neque.
  </p>
  <h2>Second level</h2>
  <p>
    Curabitur accumsan turpis pharetra <strong>augue tincidunt</strong> blandit.
    Quisque condimentum maximus mi, sit amet commodo arcu rutrum id. Proin
    pretium urna vel cursus venenatis. Suspendisse potenti. Etiam mattis s
```

## Delete

### Main Classes

| Class | Description |
|-------|-------------|
| `block` | Spacer element |
| `delete` | Delete/close button |
| `notification` | Alert message box |
| `tag` | Small tag/label element |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-danger` | danger color variant |
| `is-info` | info color variant |
| `is-large` | large size |
| `is-medium` | medium size |
| `is-small` | small size |
| `is-success` | success color variant |

### Examples

**cross**:
```html
<button class="delete"></button>
```

**cross_sizes**:
```html
<button class="delete is-small"></button>
<button class="delete"></button>
<button class="delete is-medium"></button>
<button class="delete is-large"></button>
```

**cross_elements**:
```html
<div class="block">
  <span class="tag is-success">
    Hello World
    <button class="delete is-small"></button>
  </span>
</div>

<div class="notification is-danger">
  <button class="delete"></button>
  Lorem ipsum dolor sit amet, consectetur adipiscing elit lorem ipsum dolor sit
  amet, consectetur adipiscing elit
</div>

<article class="message is-info">
  <div class="message-header">
    Info
    <button class="delete"></button>
  </div>
  <div class="message-body">
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque risus
    mi, tempus quis placerat ut, porta nec 
```

## Icon

### Main Classes

| Class | Description |
|-------|-------------|
| `block` | Spacer element |
| `content` | Rich text content wrapper |
| `icon` | Icon container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-text-danger` | Has text-danger property |
| `has-text-info` | Has text-info property |
| `has-text-success` | Has text-success property |
| `has-text-warning` | Has text-warning property |

### Examples

**icon**:
```html
<span class="icon">
  <i class="fas fa-home"></i>
</span>
```

**icon_text**:
```html
<span class="icon-text">
  <span class="icon">
    <i class="fas fa-home"></i>
  </span>
  <span>Home</span>
</span>
```

**icon_text_train**:
```html
<span class="icon-text">
  <span class="icon">
    <i class="fas fa-train"></i>
  </span>
  <span>Paris</span>
  <span class="icon">
    <i class="fas fa-arrow-right"></i>
  </span>
  <span>Budapest</span>
  <span class="icon">
    <i class="fas fa-arrow-right"></i>
  </span>
  <span>Bucharest</span>
  <span class="icon">
    <i class="fas fa-arrow-right"></i>
  </span>
  <span>Istanbul</span>
  <span class="icon">
    <i class="fas fa-flag-checkered"></i>
  </span>
</span>
```

**icon_text_in_content**:
```html
<div class="content">
  <p>
    An invitation to
    <span class="icon-text">
      <span class="icon">
        <i class="fas fa-utensils"></i>
      </span>
      <span>dinner</span>
    </span>
    was soon afterwards dispatched; and already had Mrs. Bennet planned the
    courses that were to do credit to her housekeeping, when an answer arrived
    which deferred it all. Mr. Bingley was obliged to be in
    <span class="icon-text">
      <span class="icon">
        <i class="fas fa-city"></i>
      </span>
      <span>town</span>
    </span>
    the following day, and, consequently, unable
```

## Image

## Notification

## Progress Bar

## Table

### Main Classes

| Class | Description |
|-------|-------------|
| `table` | Data table |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-bordered` | Modifier class |
| `is-selected` | Modifier class |
| `is-striped` | Modifier class |

### Examples

**table**:
```html
<table class="table">
  <thead>
    <tr>
      <th><abbr title="Position">Pos</abbr></th>
      <th>Team</th>
      <th><abbr title="Played">Pld</abbr></th>
      <th><abbr title="Won">W</abbr></th>
      <th><abbr title="Drawn">D</abbr></th>
      <th><abbr title="Lost">L</abbr></th>
      <th><abbr title="Goals for">GF</abbr></th>
      <th><abbr title="Goals against">GA</abbr></th>
      <th><abbr title="Goal difference">GD</abbr></th>
      <th><abbr title="Points">Pts</abbr></th>
      <th>Qualification or relegation</th>
    </tr>
  </thead>
  <tfoot>
    <tr>
      <th><abbr title="Posi
```

**simple_scrollable_table**:
```html
<div class="table-container">
  <table class="table is-bordered is-striped">
    <tbody>
      {% for i in (1..5) %}
      <tr>
        {% for j in (1..100) %}
        <td>{{ j | times: i }}</td>
        {% endfor %}
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

## Tags

## Title and Subtitle

