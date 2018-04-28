#!/bin/bash
# Option strings
SHORT=nsfgakm:
LONG=norename,noresize,nodeflicker,gif,avi,mkv,mov:

# read the options
OPTS=$(getopt --options $SHORT --long $LONG --name "$0" -- "$@")

if [ $? != 0 ] ; then echo "Failed to parse options...exiting." >&2 ; exit 1 ; fi

eval set -- "$OPTS"

RENAME=true
RESIZE=true
DEFLICKER=true
GIF=false
AVI=true
MKV=false
MOV=false

# extract options and their arguments into variables.
while true ; do
  case "$1" in
  
    -g | --gif )
      GIF=true
      shift
      ;;
    -a | --avi )
      AVI=false
      shift 1
      ;;
    -k | --mkv )
      MKV=false
      shift 1
      ;;
    -m | --mov )
      MOV=false
      shift 1
      ;; 
    -n | --norename )
      RENAME=false
      shift
      ;;
    -s | --noresize )
      RESIZE=false
      shift 1
      ;;
    -f | --nodeflicker )
      DEFLICKER=false
      shift 1
      ;;
    -- )
      shift
      break
      ;;
    *)
      echo "Internal error!"
      exit 1
      ;;
  esac
done

echo "RENAME = $RENAME"
echo "RESIZE = $RESIZE"
echo "DEFLICKER = $DEFLICKER"
echo "GIF = $GIF"
echo "AVI = $AVI"
echo "MKV = $MKV"
echo "MOV = $MOV"


SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

PHOTO_DIR=$(pwd)
CURR_DIR=$PHOTO_DIR

PHOTO_NAME="${PHOTO_DIR##*/}"

echo ${PHOTO_NAME}

if $RENAME;
then
  echo "Renaming"
  CURR_DIR="$CURR_DIR/renamed"
  mkdir "$CURR_DIR"
  counter=1
  ls -1tr *.JPG | while read filename; do cp $filename "$CURR_DIR/$(printf %05d $counter)_$filename"; ((counter++)); done
  cd "$CURR_DIR"
fi

if $RESIZE;
then
  echo "Resizing"
  CURR_DIR="$CURR_DIR/resized"
  mkdir "$CURR_DIR"
  mogrify -path "$CURR_DIR" -resize 1920x1080! *.JPG
  cd "$CURR_DIR"
fi

if $DEFLICKER;
then
  echo "Deflickering"
  ${SCRIPT_DIR}/timelapse-deflicker.pl
  CURR_DIR="$CURR_DIR/Deflickered"
  cd "$CURR_DIR"
fi

count=$(find . -maxdepth 1 -type f -name '*' | wc -l)

if [ $count -lt 25 ] && $GIF ; then
    echo "Making GIF"
    convert -delay 100  -loop 0 *.JPG "${PHOTO_NAME}.gif"
fi

if $AVI;
then
  echo "Making AVI"
  ffmpeg -r 25 -pattern_type glob -i '*.JPG' -c:v copy "${PHOTO_NAME}.avi"
fi

if $MKV;
then
  echo "Making MKV"
  ffmpeg -i "${PHOTO_NAME}.avi" -c:v libx264 -preset slow -crf 15 "${PHOTO_NAME}.mkv"
fi

cp "${PHOTO_NAME}".*  "$PHOTO_DIR/../"
cd "$PHOTO_DIR/"



