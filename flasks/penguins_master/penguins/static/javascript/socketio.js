$(document).ready(function(){
  // declare variables
  var server_fqdn = document.domain
  var web_protocol = "https://"
  // var web_protocol = "http://"
  var server_port = location.port
  // $('#live_message').append('the admins are working on this... please be patient.');

  //connect to the socket server.
  var socket = io.connect(web_protocol + server_fqdn);
  // var socket = io.connect(web_protocol + server_fqdn + ':' + server_port);

  // receive message details from server
  socket.on('newmessage', function(msg) {
    console.log("Received message" + msg.message);
    user_message = '<p>' + msg.message + '</p>';

    $('#live_message').append(user_message);
  });
});
