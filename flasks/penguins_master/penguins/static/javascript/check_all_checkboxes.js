function toggle_checkbox(source) {

  var main_checkbox_key = source.value;

  // document.getElementsByName('testing1')[0].innerHTML = main_checkbox_key;

  // var checkboxes = document.getElementById(main_checkbox_key);
  var find_it = '[id^='+main_checkbox_key+']'
  var checkboxes = document.querySelectorAll(find_it);;
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = source.checked;
  }
}

function display_shit() {
  var main_checkbox = document.getElementById('all_checkbox');
  var main_checkbox_key = main_checkbox.value;
  document.getElementsByName('testing')[0].innerHTML = main_checkbox_key;
}
