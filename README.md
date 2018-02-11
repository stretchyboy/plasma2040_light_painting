# mote_light_painting
Using pimoroni motes to light paint bitmap images.

## Requirements

```bash
sudo pip install webcolors pillow pygubu mote gphoto2
```

## Hardware

So far being built for
* Raspberry Pi 3 but I'm running it on my Linux Mint Laptop
* Screen https://shop.pimoroni.com/collections/raspberry-pi/products/pitft-plus-480x320-3-5-tft-touchscreen-for-raspberry-pi-pi-2-and-model-a-b
* Mote https://shop.pimoroni.com/products/mote
* Canon EOS 1200D - Should work with most EOS models and most cameras gphoto2 can control. Nothing clever just triggering shutter release with the settings you have set on the camera.

### Other Hardware

* Wooden Stick
* Screws to attach Mote sticks to the stick
* USB Battery Pack

## To Run

If you are going to attach a Camera make sure you have a "LightPaintings" folder in the same folder as the mote_light_painting folder.

```bash
sudo python mote_light_painting.py
```
