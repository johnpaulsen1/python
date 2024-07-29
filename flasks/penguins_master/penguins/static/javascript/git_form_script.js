'use strict';

let role = '';

const submitData = document.querySelector('.submit-form');

function getRole() {
  if (document.getElementById('nonprod').checked) {
    document.getElementById('prod').checked = false;
    role = 'nonprod';
  } else if (document.getElementById('prod').checked) {
    document.getElementById('nonprod').checked = false;
    role = 'prod';
  }
  return role;
}

submitData.addEventListener('click', function () {
  console.log();
  console.log(document.getElementById('change-number').value);
  console.log(document.getElementById('branch').value);
  console.log(`Selected role: ${role}`);
});
