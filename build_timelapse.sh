#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

PHOTO_DIR=$(pwd)
PHOTO_NAME="${PHOTO_DIR##*/}"

echo ${PHOTO_NAME}

RESIZED_DIR="$PHOTO_DIR/resized"

mkdir "$RESIZED_DIR"

mogrify -path resized -resize 1920x1080! *.JPG

cd "$RESIZED_DIR"

${SCRIPT_DIR}/timelapse-deflicker.pl

cd  "Deflickered"

count=$(find . -maxdepth 1 -type f -name '*' | wc -l)

if [ $count -lt 25 ] ; then
    convert -delay 100  -loop 0 *.JPG "${PHOTO_NAME}.gif"
fi

ffmpeg -r 25 -pattern_type glob -i '*.JPG' -c:v copy "${PHOTO_NAME}.avi"

ffmpeg -i "${PHOTO_NAME}.avi" -c:v libx264 -preset slow -crf 15 "${PHOTO_NAME}.mkv"

cp "${PHOTO_NAME}".*  "$PHOTO_DIR/../"
cd "$PHOTO_DIR/"



