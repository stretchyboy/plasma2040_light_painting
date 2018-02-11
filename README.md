# mote_light_painting
Using pimoroni motes to light paint bitmap images.

Inspired by 

* my son who has CP and is making a great job of light painting even without the tools I said I'd build for him
* the [Pixel Stick](http://thepixelstick.com/) which is around $350
*  the fact I have a full [Mote](https://shop.pimoroni.com/products/mote) kit that [Pimoroni](https://shop.pimoroni.com/) very kindly gave me for my 40th birthday and Motes are "Sticks of Pixels"

## Requirements

### Software

```bash
sudo pip install webcolors pillow pygubu mote gphoto2
```

### Hardware

So far being built for :-

* Raspberry Pi 3 but I'm running it on my Linux Mint Laptop
* Screen https://shop.pimoroni.com/collections/raspberry-pi/products/pitft-plus-480x320-3-5-tft-touchscreen-for-raspberry-pi-pi-2-and-model-a-b
* Mote https://shop.pimoroni.com/products/mote
* Canon EOS 1200D (optional) - Should work with most EOS models and most cameras gphoto2 can control. Nothing clever just triggering shutter release with the settings you have set on the camera.

### Other Hardware

* Wooden Stick
* Screws to attach Mote sticks to the stick
* USB Battery Pack
* Gaffer Tape (see [flow chart](https://c1.staticflickr.com/9/8160/7214525854_733237dd83_z.jpg))

## To Run

If you are going to attach a Camera by USB make sure you have a "LightPaintings" folder in the same folder as the mote_light_painting folder.

```bash
sudo python mote_light_painting.py
```
