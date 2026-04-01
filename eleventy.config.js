export default function(eleventyConfig) {
  // Bilder: aus assets/img/ direkt nach _site/img/ kopieren (kein Symlink)
  eleventyConfig.addPassthroughCopy({ "assets/img": "img" });
  // CSS durchreichen
  eleventyConfig.addPassthroughCopy("src/css");

  // CSS-Änderungen live reloaden
  eleventyConfig.addWatchTarget("src/css/");

  // Copyright-Jahr Shortcode
  eleventyConfig.addShortcode("year", () => `${new Date().getFullYear()}`);
};

export const config = {
  dir: {
    input: "src",
    includes: "_includes",
    data: "_data",
    output: "_site"
  }
};
