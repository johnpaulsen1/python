function htmlToElement(html) {
    var template = document.createElement('div');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.firstChild;
}

function createHtmlElement(key, value, user_vm_delete_date) {
    if (value.includes('_on')){
        // var created_element = htmlToElement('<input type="checkbox" name="'+key+'-'+value+'" id="'+key+'" value="'+key+'-'+value+'" checked/>')
        var created_element = htmlToElement('<input type="checkbox" name="'+key+'-'+value+'" id="'+key+'" checked/>')
        created_element.style.display = 'block';
    }
    else if (!value.includes('_on') && !value.includes('_off')){
        var created_element = htmlToElement('<input type="text" id="vm_delete_date_'+key+'" name="vm_delete_date_'+key+'" value="'+user_vm_delete_date+'"/>');
        created_element.style.display = 'block';
        created_element.style.width = '100px';
        created_element.style.height = '40px';
        created_element.style.color = '#bf2c2c';

        created_element.value = user_vm_delete_date
    }
    else if (value == 'physical_off'){
        // var created_element = htmlToElement('<p name="'+key+'-'+value+'" id="'+key+'_non-vm" value="'+key+'-'+value+'">non-vm</p>');
        var created_element = htmlToElement('<p name="'+key+'-'+value+'" id="'+key+'_non-vm">non-vm</p>');
        created_element.value = 'non-vm'
        created_element.style.display = 'none';
    }
    else {
        // var created_element = htmlToElement('<p name="'+key+'-'+value+'" id="'+key+'" value="'+key+'-'+value+'">this must be empty...</p>');
        var created_element = htmlToElement('<p name="'+key+'-'+value+'" id="'+key+'">this must be empty...</p>');
        created_element.style.display = 'none';
    }

    // alert('element name: \n' + created_element.name)

    var place_table_body = document.getElementById("table_body_"+key+"-"+value);
    place_table_body.appendChild(created_element);
}


Date.prototype.addDays = function() {
    var date = new Date(this.valueOf());
    if (date.getDay() == 5) {
        days_to_add = 3;
    }
    else if (date.getDay() == 6) {
        days_to_add = 2;
    }
    else {
        days_to_add = 1;
    }

    date.setDate(date.getDate() + days_to_add);
    return date;
}