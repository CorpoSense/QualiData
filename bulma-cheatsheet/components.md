# Bulma Components

## Overview
Bulma components are pre-styled UI elements with more complex structures.

## Breadcrumb

### Main Classes

| Class | Description |
|-------|-------------|
| `breadcrumb` | Breadcrumb trail |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-bullet-separator` | Has bullet-separator property |
| `has-succeeds-separator` | Has succeeds-separator property |
| `is-active` | active state |
| `is-large` | large size |
| `is-right` | Modifier class |
| `is-small` | small size |

### Examples

**breadcrumb**:
```html
<nav class="breadcrumb" aria-label="breadcrumbs">
  <ul>
    <li><a href="#">Bulma</a></li>
    <li><a href="#">Documentation</a></li>
    <li><a href="#">Components</a></li>
    <li class="is-active"><a href="#" aria-current="page">Breadcrumb</a></li>
  </ul>
</nav>
```

**breadcrumb_right**:
```html
<nav class="breadcrumb is-right" aria-label="breadcrumbs">
  <ul>
    <li><a href="#">Bulma</a></li>
    <li><a href="#">Documentation</a></li>
    <li><a href="#">Components</a></li>
    <li class="is-active"><a href="#" aria-current="page">Breadcrumb</a></li>
  </ul>
</nav>
```

**breadcrumb_small**:
```html
<nav class="breadcrumb is-small" aria-label="breadcrumbs">
  <ul>
    <li><a href="#">Bulma</a></li>
    <li><a href="#">Documentation</a></li>
    <li><a href="#">Components</a></li>
    <li class="is-active"><a href="#" aria-current="page">Breadcrumb</a></li>
  </ul>
</nav>
```

## Card

### Main Classes

| Class | Description |
|-------|-------------|
| `card` | Content card container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-4` | Modifier class |
| `is-48x48` | Modifier class |
| `is-4by3` | Modifier class |
| `is-6` | Modifier class |

### Examples

**card**:
```html
<div class="card">
  <div class="card-image">
    <figure class="image is-4by3">
      <img
        src="{{site.url}}/assets/images/placeholders/1280x960.png"
        alt="Placeholder image"
      />
    </figure>
  </div>
  <div class="card-content">
    <div class="media">
      <div class="media-left">
        <figure class="image is-48x48">
          <img
            src="{{site.url}}/assets/images/placeholders/96x96.png"
            alt="Placeholder image"
          />
        </figure>
   
```

**card_header**:
```html
<div class="card">
  <header class="card-header">
    <p class="card-header-title">Component</p>
    <button class="card-header-icon" aria-label="more options">
      <span class="icon">
        <i class="fas fa-angle-down" aria-hidden="true"></i>
      </span>
    </button>
  </header>
  <div class="card-content">
    <div class="content">
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec
      iaculis mauris.
      <a href="#">@bulmaio</a>. <a href="#">#css</a> <a hr
```

**card_title**:
```html
<div class="card">
  <div class="card-content">
    <p class="title">
      “There are two hard things in computer science: cache invalidation, naming
      things, and off-by-one errors.”
    </p>
    <p class="subtitle">Jeff Atwood</p>
  </div>
  <footer class="card-footer">
    <p class="card-footer-item">
      <span>
        View on
        <a href="https://twitter.com/codinghorror/status/506010907021828096"
          >Twitter</a
        >
      </span>
    </p>
    <p class="card-footer-it
```

## Dropdown

### Main Classes

| Class | Description |
|-------|-------------|
| `dropdown` | Dropdown menu |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-active` | active state |
| `is-small` | small size |
| `is-up` | Modifier class |

### Examples

**dropdown**:
```html
<div class="dropdown is-active">
  <div class="dropdown-trigger">
    <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
      <span>Dropdown button</span>
      <span class="icon is-small">
        <i class="fas fa-angle-down" aria-hidden="true"></i>
      </span>
    </button>
  </div>
  <div class="dropdown-menu" id="dropdown-menu" role="menu">
    <div class="dropdown-content">
      <a href="#" class="dropdown-item"> Dropdown item </a>
      <a class="dropdown-item">
```

**dropdown_click**:
```html
<div class="dropdown">
  <div class="dropdown-trigger">
    <button class="button" aria-haspopup="true" aria-controls="dropdown-menu3">
      <span>Click me</span>
      <span class="icon is-small">
        <i class="fas fa-angle-down" aria-hidden="true"></i>
      </span>
    </button>
  </div>
  <div class="dropdown-menu" id="dropdown-menu3" role="menu">
    <div class="dropdown-content">
      <a href="#" class="dropdown-item"> Overview </a>
      <a href="#" class="dropdown-item"> Modifiers 
```

**dropdown_left**:
```html
<div class="dropdown is-active">
  <div class="dropdown-trigger">
    <button class="button" aria-haspopup="true" aria-controls="dropdown-menu5">
      <span>Left aligned</span>
      <span class="icon is-small">
        <i class="fas fa-angle-down" aria-hidden="true"></i>
      </span>
    </button>
  </div>
  <div class="dropdown-menu" id="dropdown-menu5" role="menu">
    <div class="dropdown-content">
      <div class="dropdown-item">
        <p>The dropdown is <strong>left-aligned</strong> b
```

## null

## null

## Menu

### Main Classes

| Class | Description |
|-------|-------------|
| `menu` | Navigation menu |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-active` | active state |

### Examples

**menu**:
```html
<aside class="menu">
  <p class="menu-label">General</p>
  <ul class="menu-list">
    <li><a>Dashboard</a></li>
    <li><a>Customers</a></li>
  </ul>
  <p class="menu-label">Administration</p>
  <ul class="menu-list">
    <li><a>Team Settings</a></li>
    <li>
      <a class="is-active">Manage Your Team</a>
      <ul>
        <li><a>Members</a></li>
        <li><a>Plugins</a></li>
        <li><a>Add a member</a></li>
      </ul>
    </li>
    <li><a>Invitations</a></li>
    <li><a>Cloud Storage 
```

## Message

### Main Classes

| Class | Description |
|-------|-------------|
| `message` | Colored message box |

### Examples

**message**:
```html
<article class="message">
  <div class="message-header">
    <p>Hello World</p>
    <button class="delete" aria-label="delete"></button>
  </div>
  <div class="message-body">
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    <strong>Pellentesque risus mi</strong>, tempus quis placerat ut, porta nec
    nulla. Vestibulum rhoncus ac ex sit amet fringilla. Nullam gravida purus
    diam, et dictum <a>felis venenatis</a> efficitur. Aenean ac
    <em>eleifend lacus</em>, in mollis lectu
```

**message_body**:
```html
<article class="message">
  <div class="message-body">
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    <strong>Pellentesque risus mi</strong>, tempus quis placerat ut, porta nec
    nulla. Vestibulum rhoncus ac ex sit amet fringilla. Nullam gravida purus
    diam, et dictum <a>felis venenatis</a> efficitur. Aenean ac
    <em>eleifend lacus</em>, in mollis lectus. Donec sodales, arcu et
    sollicitudin porttitor, tortor urna tempor ligula, id porttitor mi magna a
    neque. Done
```

## Modal

## null

### Main Classes

| Class | Description |
|-------|-------------|
| `nav` | Navigation wrapper (deprecated, use navbar) |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-shadow` | Has shadow property |
| `is-16x16` | Modifier class |
| `is-active` | active state |
| `is-grouped` | Modifier class |
| `is-hidden-mobile` | Modifier class |
| `is-hidden-tablet` | Modifier class |
| `is-primary` | primary color variant |
| `is-tab` | Modifier class |

### Examples

**nav**:
```html
<nav class="nav">
      <div class="nav-left">
        <a class="nav-item">
          <img src="{{ site.url }}/assets/images/bulma-logo.png" alt="Bulma logo" />
        </a>
      </div>

      <div class="nav-center">
        <a class="nav-item">
          <span class="icon">
            <i class="fab fa-github"></i>
          </span>
        </a>
        <a class="nav-item">
          <span class="icon">
            <i class="fab fa-twitter"></i>
          </span>
        </a>
      </div>

  
```

**nav_tabs**:
```html
<nav class="nav has-shadow">
    <div class="container">
      <div class="nav-left">
        <a class="nav-item">
          <img src="{{ site.url }}/assets/images/bulma-logo.png" alt="Bulma logo" />
        </a>
        <a class="nav-item is-tab is-hidden-mobile is-active">Home</a>
        <a class="nav-item is-tab is-hidden-mobile">Features</a>
        <a class="nav-item is-tab is-hidden-mobile">Pricing</a>
        <a class="nav-item is-tab is-hidden-mobile">About</a>
      </div>
      <span 
```

## Navbar

### Main Classes

| Class | Description |
|-------|-------------|
| `message` | Colored message box |
| `navbar` | Navigation bar |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-dropdown` | Has dropdown property |
| `has-dropdown-up` | Has dropdown-up property |
| `is-4` | Modifier class |
| `is-active` | active state |
| `is-arrowless` | Modifier class |
| `is-boxed` | Modifier class |
| `is-grouped` | Modifier class |
| `is-hoverable` | Modifier class |
| `is-info` | info color variant |
| `is-light` | light color variant |
| `is-one-quarter` | Modifier class |
| `is-paddingless` | Modifier class |
| `is-primary` | primary color variant |
| `is-right` | Modifier class |
| `is-selected` | Modifier class |
| `is-success` | success color variant |
| `is-transparent` | Modifier class |

### Examples

**navbar_basic**:
```html
<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="{{ site.url }}">
      {% include svg/bulma-logo.html %}
    </a>

    <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>

  <div id="
```

**navbar**:
```html
{% include docs/examples/navbar.html id="Default" %}
```

**navbar_brand**:
```html
<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
    <!-- navbar items, navbar burger... -->
  </div>
</nav>
```

## Pagination

### Main Classes

| Class | Description |
|-------|-------------|
| `pagination` | Page navigation |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-centered` | Modifier class |
| `is-current` | Modifier class |
| `is-disabled` | Modifier class |
| `is-large` | large size |
| `is-medium` | medium size |
| `is-right` | Modifier class |
| `is-rounded` | rounded state |
| `is-small` | small size |

### Examples

**pagination**:
```html
<nav class="pagination" role="navigation" aria-label="pagination">
  <a href="#" class="pagination-previous">Previous</a>
  <a href="#" class="pagination-next">Next page</a>
  <ul class="pagination-list">
    <li>
      <a href="#" class="pagination-link" aria-label="Goto page 1">1</a>
    </li>
    <li>
      <span class="pagination-ellipsis">&hellip;</span>
    </li>
    <li>
      <a href="#" class="pagination-link" aria-label="Goto page 45">45</a>
    </li>
    <li>
      <a
        class="p
```

**pagination_options**:
```html
<nav class="pagination" role="navigation" aria-label="pagination">
  <a class="pagination-previous is-disabled" title="This is the first page"
    >Previous</a
  >
  <a href="#" class="pagination-next">Next page</a>
  <ul class="pagination-list">
    <li>
      <a
        class="pagination-link is-current"
        aria-label="Page 1"
        aria-current="page"
        >1</a
      >
    </li>
    <li>
      <a href="#" class="pagination-link" aria-label="Goto page 2">2</a>
    </li>
    <li>
   
```

**pagination_centered**:
```html
<nav class="pagination is-centered" role="navigation" aria-label="pagination">
  <a href="#" class="pagination-previous">Previous</a>
  <a href="#" class="pagination-next">Next page</a>
  <ul class="pagination-list">
    <li><a href="#" class="pagination-link" aria-label="Goto page 1">1</a></li>
    <li><span class="pagination-ellipsis">&hellip;</span></li>
    <li><a href="#" class="pagination-link" aria-label="Goto page 45">45</a></li>
    <li>
      <a
        class="pagination-link is-curren
```

## Panel

### Main Classes

| Class | Description |
|-------|-------------|
| `panel` | Panel container |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `has-icons-left` | Has icons-left property |
| `is-active` | active state |
| `is-fullwidth` | fullwidth state |
| `is-left` | Modifier class |
| `is-link` | link color variant |
| `is-outlined` | outlined state |

### Examples

**panel**:
```html
<nav class="panel">
  <p class="panel-heading">Repositories</p>
  <div class="panel-block">
    <p class="control has-icons-left">
      <input class="input" type="text" placeholder="Search" />
      <span class="icon is-left">
        <i class="fas fa-search" aria-hidden="true"></i>
      </span>
    </p>
  </div>
  <p class="panel-tabs">
    <a class="is-active">All</a>
    <a>Public</a>
    <a>Private</a>
    <a>Sources</a>
    <a>Forks</a>
  </p>
  <a class="panel-block is-active">
    <span
```

## Tabs

### Main Classes

| Class | Description |
|-------|-------------|
| `tabs` | Tab navigation |

### Modifier Classes

| Class | Description |
|-------|-------------|
| `is-active` | active state |
| `is-fullwidth` | fullwidth state |
| `is-large` | large size |
| `is-right` | Modifier class |
| `is-small` | small size |
| `is-toggle` | Modifier class |

### Examples

**tabs**:
```html
<div class="tabs">
  <ul>
    <li class="is-active"><a>Pictures</a></li>
    <li><a>Music</a></li>
    <li><a>Videos</a></li>
    <li><a>Documents</a></li>
  </ul>
</div>
```

**tabs_right**:
```html
<div class="tabs is-right">
  <ul>
    <li class="is-active"><a>Pictures</a></li>
    <li><a>Music</a></li>
    <li><a>Videos</a></li>
    <li><a>Documents</a></li>
  </ul>
</div>
```

**tabs_small**:
```html
<div class="tabs is-small">
  <ul>
    <li class="is-active"><a>Pictures</a></li>
    <li><a>Music</a></li>
    <li><a>Videos</a></li>
    <li><a>Documents</a></li>
  </ul>
</div>
```

