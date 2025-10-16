'use strict';
const fs = require('fs');

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

// 避免在源代码中表达 base64 文本，改为生成文件
hexo.extend.generator.register("travel-moe-svg", async function (locals) {
  function loadSvg(url) {
    return fetch(url).then(resp => resp.text());
  }
  const lightOption = {
    "labelColor": "282726",
  }
  const darkOption = {
    "labelColor": "FFFFFF",
  }
  const logoBase64 = fs.readFileSync("source/images/travel-moe-logo.png");
  const logoDataUri = `data:image/png;base64,${logoBase64.toString('base64')}`;
  function makeUrl(option) {
    const url = new URL("https://img.shields.io/badge/异次元之旅");
    url.pathname += "-" + option.labelColor;
    url.searchParams.set("logo", logoDataUri);
    return url.toString();
  }

  return [
    { path: "images/travel-moe-light.svg", data: await loadSvg(makeUrl(lightOption)) },
    { path: "images/travel-moe-dark.svg", data: await loadSvg(makeUrl(darkOption)) }
  ]
});