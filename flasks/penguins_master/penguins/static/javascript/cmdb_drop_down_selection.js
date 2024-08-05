function updatePlaceHolder() {
  var placeholder_1st_bit = "CMDB "
  var placeholder_last_bit = "/s"
  var standard_class = "control-group-small"
  var visibility_on_class = "visibility_on"
  var visibility_off_class = "visibility_off"
  var selected_search_option = document.getElementById('cmdb_search_by');
  var selected_index = selected_search_option.selectedIndex;
  var selected_value = selected_search_option.options[selected_index].value
  if (selected_value == "host_name" || selected_value == "ipaddress"){
    var display_placeholder = placeholder_1st_bit + selected_value + placeholder_last_bit
  }
  else {
    var display_placeholder = placeholder_1st_bit + selected_value
  }

  if (selected_value == "bu"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_on_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "cost_centre"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_on_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "company_code"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_on_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "role"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_on_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "host_type"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_on_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "architecture"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_on_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "osfamily"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_on_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "osversion"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_on_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }
  else if (selected_value == "managed" || selected_value == "config_manager"){
    var text_field_html_class = standard_class + " " + visibility_off_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_on_class
  }
  else {
    var text_field_html_class = standard_class + " " + visibility_on_class
    var bu_drop_down_html_class = standard_class + " " + visibility_off_class
    var cost_centre_drop_down_html_class = standard_class + " " + visibility_off_class
    var company_code_drop_down_html_class = standard_class + " " + visibility_off_class
    var role_drop_down_html_class = standard_class + " " + visibility_off_class
    var host_type_drop_down_html_class = standard_class + " " + visibility_off_class
    var architecture_drop_down_html_class = standard_class + " " + visibility_off_class
    var osfamily_drop_down_html_class = standard_class + " " + visibility_off_class
    var osversion_drop_down_html_class = standard_class + " " + visibility_off_class
    var managed_drop_down_html_class = standard_class + " " + visibility_off_class
  }

  document.getElementsByName('cmdb_search_field')[0].placeholder = display_placeholder;
  document.getElementById("text_area").className = text_field_html_class;
  document.getElementById("bu_drop_down").className = bu_drop_down_html_class;
  document.getElementById("cost_centre_drop_down").className = cost_centre_drop_down_html_class;
  document.getElementById("company_code_drop_down").className = company_code_drop_down_html_class;
  document.getElementById("role_drop_down").className = role_drop_down_html_class;
  document.getElementById("host_type_drop_down").className = host_type_drop_down_html_class;
  document.getElementById("architecture_drop_down").className = architecture_drop_down_html_class;
  document.getElementById("osfamily_drop_down").className = osfamily_drop_down_html_class;
  document.getElementById("osversion_drop_down").className = osversion_drop_down_html_class;
  document.getElementById("managed_drop_down").className = managed_drop_down_html_class;
	}
