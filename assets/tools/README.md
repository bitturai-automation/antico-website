# Antico website — folder structure

```
index.html                  <- home page (the only page outside assets/)
robots.txt  sitemap.xml     <- must stay in the root for search engines
assets/
  pages/
    about.html  contact.html  blog.html  privacy-policy.html  terms-conditions.html
    applications/           index.html (landing page), chemical-processing, pharmaceutical, petrochemical,
                            fertilizer, specialty-chemicals, process-manufacturing
    products/
      index.html            all-products listing
      <product-id>.html     43 product showcase pages (generated)
  css/  js/  images/  catalogue/
  favicon.ico  favicon.png  site.webmanifest
  tools/                    build scripts (not part of the live site)
```

## Editing product pages
Product pages are generated from `js/products-data.js` + `tools/product_copy.py`.
After changing either file, run from anywhere:

    python3 assets/tools/build_products.py
    python3 assets/tools/seo.py https://your-domain.com   # re-adds SEO tags + sitemap

Never edit `assets/pages/products/<id>.html` by hand, as the next build overwrites it.
Header/footer for generated pages come from `tools/template-about.html`.

## Links
Inside `assets/`, pages in `pages/` use `../`, pages in `pages/products/` and `pages/applications/` use `../../`.
Links to the home page need one more `../` (it sits above `assets/`).
Shared JS finds the assets root through `window.SITE_ROOT` (`assets/` on the home page, `../` or `../../` on inner pages).
`tools/layout.py` holds the URL map.
