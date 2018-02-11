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

## Usage

If you are going to attach a Camera by USB make sure you have a "LightPaintings" folder in the same folder as the mote_light_painting folder.

```bash
sudo python mote_light_painting.py
```

* Choose a file (there is a nice default spectrum if you are just testing)
* The Graph shows your image as 64 pixels (the height of a full set of motes) over the draw time (so it will usually look stretched, don't worry its a graph) 
* We often end up needing to ignore pure white pixels, if you need them painting check the 'Paint White ?' box. At the moment you need to reload the file.
* Ticking 'Control Camera' will try to capture a photo from you USB / PTP camera via gphoto2 (there is no error checking here at the mo, so if it freezes start again).
* "Delay Time" is self explanatory
* "Draw Time" is how long it will take for your image to be drawn and will depend on the exposure time you are using
* "Repeats" set how many times the Delay/Draw cycle takes place. This should allow for nice light painted / stop motion effects
* The "Draw" button :-
  * Blanks the Graph
  * Waits for any delay, drawing the progress on the Graph
  * Starts the camera's shot if 'Control Camera' is selected 
  * Starts changing the lights. 
  * Move the lights across the field of view of the camera. The Graph will redraw to give you a clue how far along you are.
  * The Draw process "Repeats" until it should end
  * On the last repeat, if 'Control Camera' is selected the image should pop up in a photo viewer



