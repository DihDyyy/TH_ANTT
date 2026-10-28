// CI_PAGES_URL is supplied by GitLab. SITE_URL can be set for another preview URL.
// example.invalid is an explicit placeholder, not a deployed website.
const pagesUrl = new URL(
  process.env.CI_PAGES_URL ||
    process.env.SITE_URL ||
    'https://example.invalid/lab06-devsecops/',
);
const baseUrl = pagesUrl.pathname.endsWith('/')
  ? pagesUrl.pathname
  : `${pagesUrl.pathname}/`;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Bài 6 — Bảo mật với DevSecOps',
  tagline: 'CI/CD Pipeline với Docusaurus và GitHub Pages',
  url: pagesUrl.origin,
  baseUrl,
  trailingSlash: true,
  onBrokenLinks: 'throw',
  i18n: {defaultLocale: 'vi', locales: ['vi']},
  presets: [
    [
      'classic',
      {
        docs: {sidebarPath: './sidebars.js'},
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      },
    ],
  ],
  themeConfig: {
    navbar: {
      title: 'DevSecOps',
      items: [
        {to: '/docs/lab06', label: 'Nội dung thực hành', position: 'left'},
      ],
    },
    footer: {
      style: 'dark',
      copyright: 'Copyright © 2026 DevSecOps Project. Built with Docusaurus.',
    },
  },
};

module.exports = config;
