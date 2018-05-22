var SerialPort = require('serialport');

var VID = '16d0';
var PID = '08c4';
var ports = [];

SerialPort.list(function(err, results) {
  if (err) {
    throw err;
  }

  motes = results.filter(function(result) {
    return result.vendorId == VID && result.productId == PID;
  });

  ports = motes.map(function(result){
      return new SerialPort(result.comName);
  });

  ports.forEach(function(port, ind){
     configureMote(port, ind+1, 16, 0);
  });

  ports.forEach(function(port, ind){
    colourtheMote(port, 255,0,0 );
 });

});

var strToUint8Array = function(str){
  var command = Uint8Array.from(
      str.split("").map(function(cha){
        //console.log("cha", cha, "codePointAt", cha.codePointAt(0));
        return cha.codePointAt(0);
    })
  );
  return command;
}

var sendMessage = function(port, message){

  var buffer = Buffer.from(message.buffer);

  try{
  port.write(buffer, function(err) {
    if (err) {
      return console.log('Error on write: ', err.message);
    }
    console.log('message written');
  });

  // Open errors will be emitted as an error event
  port.on('error', function(err) {
    console.log('Error: ', err.message);
  });
} catch(err){

    console.log('Error: ', err.message);

}
}
var configureMote = function(port, channel, num_pixels, flags){
  var message = new Uint8Array(8);
  message.set(strToUint8Array("motec"), 0);
  var config = Uint8Array.of(channel, num_pixels, flags);
  message.set(config, 5);
  sendMessage(port, message);


};

var colourtheMote = function(port, r,g,b ){
  var numPixels = 16*4;
  var message = new Uint8Array(5+(numPixels*3));
  message.set(strToUint8Array("moteo"),0);
  for( var i=0; i< numPixels; i++){
    var pixel = Uint8Array.from([b,g,r]);
    message.set (pixel, 5+(3*i));
  }
  sendMessage(port, message);


  //self._channels[channel-1][index] = (r & 0xff, g & 0xff, b & 0xff, brightness)
/*for pixel in data:
          r, g, b, brightness = pixel
          r, g, b = [int(x * brightness * self.white_point[i]) for i, x in enumerate([r, g, b])]
          buf.append(b)
          buf.append(g)
          buf.append(r)
          */


}
