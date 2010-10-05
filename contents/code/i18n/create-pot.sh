#!/bin/sh

# Create template file
echo "Creating comicagg-plasmoid.pot file..."
xgettext --package-version="0.1" --no-wrap --copyright-holder="Jesús Fernández" --package-name="comicagg-plasmoid" --keyword=i18n --keyword=i18np:1,2 --keyword=translate:2 -o ./comicagg-plasmoid-new.pot ../*.py

# Fixing header (there must be a better way to do this)
echo "Fixing header information..."
sed 's/CHARSET/utf-8/' ./comicagg-plasmoid-new.pot > comicagg-plasmoid-new1.pot ; rm comicagg-plasmoid-new.pot
mv comicagg-plasmoid-new1.pot comicagg-plasmoid.pot

echo "Done."
