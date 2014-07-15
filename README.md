# Web Platform Compatibility API

This is the start of a project to build an API to support
[Compatibility Tables](https://wiki.mozilla.org/MDN/Development/CompatibilityTables)
on
[Mozilla Developer Network](https://developer.mozilla.org).

* [api.md](api.md) - Draft API documentation.  Once we get 90% there, we'll
  start the code.
* [canonicalized-display.svg](canonicalized-display.svg) - One way to break
  up pages like the one for the
  [CSS display property](https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility),
  while preserving table order and other desirable features.  The
  [source](canonicalized-display.gv) is in Graphviz.
* [sample_mdn.py](sample_mdn.py) - Display a randomly picked Compatability
  Table from MDN, via the [WebPlatform.org](http://webplatform.org)
  [scrapped compatibility tables data](https://github.com/webplatform/compatibility-data)
