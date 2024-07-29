function showUserMessage() {

  var standard_class = "info-splash control-group"
  var visibility_on_class = "visibility_on"
  // var visibility_off_class = "visibility_off"
  var info_splash_div_element = document.getElementById('info-splash-div');
  var info_splash_div_element_class = standard_class + " " + visibility_on_class
  
  var user_info_message_element = document.getElementById('user_info_message');
  var user_info_message_element_innerhtml = user_info_message_element.innerHTML;
  
  info_splash_div_element.className = info_splash_div_element_class;
  user_info_message_element.innerHTML = user_info_message_element_innerhtml;
	}
