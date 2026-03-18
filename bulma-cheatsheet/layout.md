# Bulma Layout

## Overview
Bulma layout components for page structure.

## Container

### Main Classes

| Class | Description |
|-------|-------------|
| `container` | Centered content container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-max-tablet` | Modifier class |
| `is-max-widescreen` | Modifier class |
| `is-primary` | primary color variant |
| `is-widescreen` | Modifier class |

### Examples

**container**:
```html
<div class="container">
  <div class="notification is-primary">
    This container is <strong>centered</strong> on desktop and larger viewports.
  </div>
</div>
```

**container_widescreen**:
```html
<div class="container is-widescreen">
  <div class="notification is-primary">
    This container is <strong>fullwidth</strong> <em>until</em> the
    <code>$widescreen</code> breakpoint.
  </div>
</div>
```

## Footer

### Main Classes

| Class | Description |
|-------|-------------|
| `footer` | Page footer |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-text-centered` | Has text-centered property |

### Examples

**footer**:
```html
<footer class="footer">
  <div class="content has-text-centered">
    <p>
      <strong>Bulma</strong> by <a href="https://jgthms.com">Jeremy Thomas</a>.
      The source code is licensed
      <a href="https://opensource.org/license/mit">MIT</a>. The
      website content is licensed
      <a href="https://creativecommons.org/licenses/by-nc-sa/4.0//"
        >CC BY NC SA 4.0</a
      >.
    </p>
  </div>
</footer>
```

## Hero

### Main Classes

| Class | Description |
|-------|-------------|
| `hero` | Hero banner section |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-danger` | danger color variant |
| `is-fullheight` | Modifier class |
| `is-fullheight-with-navbar` | Modifier class |
| `is-halfheight` | Modifier class |
| `is-link` | link color variant |
| `is-success` | success color variant |

### Examples

**hero**:
```html
<section class="hero">
  <div class="hero-body">
    <p class="title">Hero title</p>
    <p class="subtitle">Hero subtitle</p>
  </div>
</section>
```

**halfheight**:
```html
<section class="hero is-success is-halfheight">
  <div class="hero-body">
    <div class="">
      <p class="title">Half height hero</p>
      <p class="subtitle">Half height subtitle</p>
    </div>
  </div>
</section>
```

## Level

### Main Classes

| Class | Description |
|-------|-------------|
| `level` | Horizontal content grouping |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-addons` | Has addons property |
| `has-text-centered` | Has text-centered property |
| `is-5` | Modifier class |
| `is-info` | info color variant |
| `is-mobile` | Modifier class |
| `is-success` | success color variant |

### Examples

**nav**:
```html
<!-- Main container -->
<nav class="level">
  <!-- Left side -->
  <div class="level-left">
    <div class="level-item">
      <p class="subtitle is-5"><strong>123</strong> posts</p>
    </div>
    <div class="level-item">
      <div class="field has-addons">
        <p class="control">
          <input class="input" type="text" placeholder="Find a post" />
        </p>
        <p class="control">
          <button class="button">Search</button>
        </p>
      </div>
    </div>
  </div>

  <
```

**nav_centered**:
```html
<nav class="level">
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Tweets</p>
      <p class="title">3,456</p>
    </div>
  </div>
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Following</p>
      <p class="title">123</p>
    </div>
  </div>
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">Followers</p>
      <p class="title">456K</p>
    </div>
  </div>
  <div class="level-item has-text-centered">

```

## Media Object

### Main Classes

| Class | Description |
|-------|-------------|
| `level` | Horizontal content grouping |
| `media` | Media object container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-48x48` | Modifier class |
| `is-64x64` | Modifier class |
| `is-info` | info color variant |
| `is-mobile` | Modifier class |
| `is-small` | small size |

### Examples

**media**:
```html
<article class="media">
  <figure class="media-left">
    <p class="image is-64x64">
      <img src="{{site.url}}/assets/images/placeholders/128x128.png" />
    </p>
  </figure>
  <div class="media-content">
    <div class="content">
      <p>
        <strong>John Smith</strong> <small>@johnsmith</small> <small>31m</small>
        <br />
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin ornare
        magna eros, eu pellentesque tortor vestibulum ut. Maecenas non massa
     
```

**media_bis**:
```html
<article class="media">
  <figure class="media-left">
    <p class="image is-64x64">
      <img src="{{site.url}}/assets/images/placeholders/128x128.png" />
    </p>
  </figure>
  <div class="media-content">
    <div class="field">
      <p class="control">
        <textarea class="textarea" placeholder="Add a comment..."></textarea>
      </p>
    </div>
    <nav class="level">
      <div class="level-left">
        <div class="level-item">
          <a class="button is-info">Submit</a>
       
```

## Section

### Main Classes

| Class | Description |
|-------|-------------|
| `section` | Page section |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-large` | large size |
| `is-medium` | medium size |

### Examples

**section**:
```html
<section class="section">
  <h1 class="title">Section</h1>
  <h2 class="subtitle">
    A simple container to divide your page into <strong>sections</strong>, like
    the one you're currently reading.
  </h2>
</section>
```

**section_medium**:
```html
<section class="section is-medium">
  <h1 class="title">Medium section</h1>
  <h2 class="subtitle">
    A simple container to divide your page into <strong>sections</strong>, like
    the one you're currently reading.
  </h2>
</section>
```

