#!/bin/sh

# BRITISH ENGLISH: Merge new translations
# echo "Merging new British English translations..."
# cd en_GB
# msgmerge ./comicagg-plasmoid.po ../comicagg-plasmoid.pot -o comicagg-plasmoid-new.po
# cd ..

# SPANISH: Merge new translations
echo "Merging new Spanish translations..."
cd es
msgmerge ./comicagg-plasmoid.po ../comicagg-plasmoid.pot -o comicagg-plasmoid-new.po
cd ..
