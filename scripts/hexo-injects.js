'use strict';

// Host the umami script locally to avoid being blocked by ad blockers
// https://umami.is/docs/bypass-ad-blockers#hosting-the-tracker-script
// The rewrite function on EdgeOne is broken, so we have to do it ourselves
hexo.extend.generator.register("umami-script", async function (locals) {
  const scriptUrl = new URL(hexo.config.theme_config.umami.host_url);
  scriptUrl.pathname = "/script.js";
  const scriptResp = await fetch(scriptUrl.toString());
  const scriptText = await scriptResp.text();
  return {
    path: "umami.js",
    data: scriptText,
  };
});