function updatePlaceHolder() {
  var placeholder_1st_bit = "Decomm "
  var placeholder_last_bit = "/s"
  var standard_class = "control-group-small"
  var visibility_on_class = "visibility_on"
  var visibility_off_class = "visibility_off"
  var selected_search_option = document.getElementById('decomm_search_by');
  var selected_index = selected_search_option.selectedIndex;
  var selected_value = selected_search_option.options[selected_index].value
  if (selected_value == "Hostname"){
    var display_placeholder = placeholder_1st_bit + selected_value + placeholder_last_bit
  }
  else {
    var display_placeholder = placeholder_1st_bit + selected_value
  }

  if (selected_value == "Date"){
    var date_field_html_class = standard_class + " " + visibility_on_class
    var text_field_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "All"){
    var date_field_html_class = standard_class + " " + visibility_off_class
    var text_field_html_class = standard_class + " " + visibility_off_class
  }
  else {
    var date_field_html_class = standard_class + " " + visibility_off_class
    var text_field_html_class = standard_class + " " + visibility_on_class
  }

  document.getElementsByName('decomm_search_field')[0].placeholder = display_placeholder;
  document.getElementById("text_area").className = text_field_html_class;
  document.getElementById("date_field").className = date_field_html_class;
	}
