# WordPress Server Side Image Optimiser

![python-app workflow](https://github.com/ployt0/wp-exp-to-md-img-fixer/actions/workflows/python-app.yml/badge.svg)

Builds on the legendary [export to MD by lonekorean](https://github.com/lonekorean/wordpress-export-to-markdown).

I have problems with it scraping all my images from posts. The posts still contain the old links, so work, so long as the old site is available. Also, some of these "forgotten" links are to downscaled versions. This is fixed here too.

I don't want to install node.js so my node environment is started in one shell using:

```shell
docker run --name node1 -ti --rm node:18.7.0-alpine3.15 sh
```

Then I copy over `export.xml`

```shell
docker cp -a wordpress-export-to-markdown node1:/root/
docker cp ~/Downloads/export.xml node1:/root/wordpress-export-to-markdown/
```

Back to the container shell and I must replace links accessible from the host
with those accessible from the container:

```shell
cd ~/wordpress-export-to-markdown
sed -i "s/localhost:8541/172.17.0.1:8541/" /root/wordpress-export-to-markdown/export.xml
npm install
node index.js --wizard=false --input=export.xml --post-folders=false
```

Then I have the self-signed certificate error. So I did the unthinkable and read
the JS. It wasn't so hard to follow, I made a [PR](https://github.com/lonekorean/wordpress-export-to-markdown/pull/82) which probably fixes the
biggest issue this repo was fixing, missing images. Spoiler alert, they were
all my webp!

Please see the unit tests for more details.

# Usage

```shell
python wp-exp-to-md-img-fixer/converted_md_corrector.py -m tests/si-tests/pages https://yoursite.co.uk/wp-content/uploads
```


https://user-images.githubusercontent.com/25666053/185379174-e0daa3d4-0cfd-4f05-a27c-f3389b45a35c.mp4


I've provided some sample pages using images on ibb. GitHub can run it for me:

```shell
python wp-exp-to-md-img-fixer/converted_md_corrector.py -m tests/si-tests/pages https://i.ibb.co
```

Still working on showing what that proves, the video above is a better demo.

I have another demo in si-tests/output-links-fixed. All the links were transformed successfully by the node.js script. Because I added webp support to it. It *does* however demonstrate how scaled down images were sometimes provided. This is a WordPress issue, but we can still do something about it, which we do, here. I already copied the full sized images across too. The demo should show that the markdown is updated to use them, if there can be any doubts about the unit tests showing this.

I have provided my exported xml. It is configured:

Username: testrunner
Password: HBX_fsHwXRkj2
dontcare@dontemail.com

Obviously the image server isn't available anymore, but could be regenerated in the cloud if lonekorean doesn't merge my PR first.