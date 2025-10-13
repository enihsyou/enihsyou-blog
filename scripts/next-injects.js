'use strict';

// add support to line range in gist.
// https://github.com/bvanderhoof/gist-embed
// move to each post which requires, to improve performance
// hexo.extend.filter.register('theme_inject', function(injects) {
//   injects.bodyEnd.raw(
//       'load-custom-gist-embed',
//       '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/gist-embed@1.0.4/dist/gist-embed.min.js"></script>', {},
//       { cache: true }
//   );
// });

// add host to config for head.njk
hexo.extend.filter.register("template_locals", function (locals) {
  locals.config.host = new URL(locals.config.url).host;
  return locals;
});
