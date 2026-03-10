module.exports = {
  settings: {
    // Preserve existing manual line breaks (semantic line breaks)
    wrap: false,
    bullet: '-',
    listItemIndent: 'one',
    fences: true,
    rule: '-',
    strong: '*',
    emphasis: '_'
  },
  plugins: [
    require('remark-gfm'),
    require('remark-frontmatter'),
    require('remark-preset-lint-recommended')
  ]
}
