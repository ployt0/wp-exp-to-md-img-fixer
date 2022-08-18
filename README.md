# WordPress Server Side Image Optimiser

Builds on the legendary [export to MD by lonekorean](https://github.com/lonekorean/wordpress-export-to-markdown).

I have problems with it scraping all my images from posts. The posts still contain the old links so work, so long as the old site is available. Also, though probably the fault of my export.xml, some of these "forgotten" links are to downscaled versions. This is fixed here too.

I need somebody to donate their site's export.xml. I'll get round to it later but I wrote this project on a borrowed laptop and I don't have access right now.

Integration tests can use an alpine and node.js on the export.xml. Like lonekorean's repo, a gif video would suffice if this is a hassle.

Please see the unit tests for how it works.

# Usage

```shell
python wp-exp-to-md-img-fixer/converted_md_corrector.py -m tests/si-tests/pages https://yoursite.co.uk/wp-content/uploads
```

Video goes here.

I've provided some sample pages using images on ibb. I hope GitHub can run it for me, but if not:

```shell
python wp-exp-to-md-img-fixer/converted_md_corrector.py -m tests/si-tests/pages https://i.ibb.co
```

