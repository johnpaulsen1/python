function updatePlaceHolder() {
  var placeholder_1st_bit = "VM "
  var placeholder_last_bit = "/s"
  var selected_search_option = document.getElementById('vm_search_by');
  var selected_index = selected_search_option.selectedIndex;
  var selected_value = selected_search_option.options[selected_index].value
  var display_placeholder = placeholder_1st_bit + selected_value + placeholder_last_bit
  document.getElementsByName('vm_search_field')[0].placeholder = display_placeholder;
	}
