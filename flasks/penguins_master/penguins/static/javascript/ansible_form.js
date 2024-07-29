'use strict';

const displayRoleSelection = document.querySelector(".role-selection")
const dropdown_value = document.getElementById('playbook').value;

// var subjectObject = {
  // "main": ["start", "stop", "restart", "list" ],
  // "agent": ["start", "stop", "restart", "check" ] ,
  // "server": ["clean", "force", "test", "off" ] ,
// }


function loadFile(filepath) {
  var result = null;
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open('GET', filepath, false);
  xmlhttp.send();
  if (xmlhttp.status === 200) {
    result = xmlhttp.responseText;
  };
  const data = JSON.parse(result)
  console.log(data)

  return data
}

let subjectObject = loadFile('/static/data.json')

window.onload = function() {
   var playbookSel = document.getElementById("playbook");
   var roleSel = document.getElementById("roles");
   var passwordPrompt = document.querySelector('.passwords')

   for (var x in subjectObject) {
     playbookSel.options[playbookSel.options.length] = new Option(x, x);
   }

   playbookSel.onchange = function() {
     console.log(playbookSel.value);
     var y = subjectObject[playbookSel.value]
     console.log(y)
     for (var i = 0; i < y.length; i++) {
       console.log(y[i])
       roleSel.options[roleSel.options.length] = new Option(y[i], y[i]);
     }

    roleSel.onchange = function() {
     if (passwordPrompt.classList.contains('hidden')) {
       passwordPrompt.classList.remove('hidden')
     } else {
       passwordPrompt.classList.add('hidden')
     }
    }
  }
}
