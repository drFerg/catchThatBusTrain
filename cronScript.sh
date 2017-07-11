#!/bin/sh

cd "$(dirname "$0")"



date

echo "------ python get data from metoffice"
python ~/projects/kindleDisplay/server/kindleDisplay.py

echo "------ convert to png"
rsvg-convert --background-color=white  ~/projects/kindleDisplay/server/kindleOutput.svg -o ~/projects/kindleDisplay/server/kindleOutput.png

echo "------ shrink png"
pngcrush -q -c 0 ~/projects/kindleDisplay/server/kindleOutput.png ~/projects/kindleDisplay/server/kindleOutputShrunk.png

echo "------ copy to webserver"
#cp -f ~/projects/kindleDisplay/server/kindleOutputShrunk.png /var/www/html/weather-script-output.png
