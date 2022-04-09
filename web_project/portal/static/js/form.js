const formFieldsDict = {
    "customer_name": "Customer Name",
    "vlan_number": "VLAN",
    "access_device-name": "Switch",
    "access_access-port": "Port to Customer",
    "access_uplink-port": "Port to Router",
    "aggregation_device-name": "Router",
    "aggregation_ipv4-address": "IPv4 Address",
    "aggregation_cidr-mask": "Netmask",
    "aggregation_access-interface": "Port to Switch"
}

let ipAddrAndMask = {}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Validate Form at Submit Event Raise Confirmation Modal
function validateForm(event){    
    let customerInput = document.querySelector('input[name="customer_name"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    let ipv4AddressInput = document.querySelector('select[name="aggregation_ipv4-address"]')
    
    let accessPortSelect = document.querySelector('select[name="access_access-port"]')
    let uplinkPortSelect = document.querySelector('select[name="access_uplink-port"]')
    let aggregationPortSelect = document.querySelector('select[name="aggregation_access-interface"]')

    let accessDeviceSelect = document.querySelector('select[name="access_device-name"]')
    let aggregationDeviceSelect = document.querySelector('select[name="aggregation_device-name"]')
    // console.log(aggregationDeviceSelect)
    // debugger;
    let aggregationCIDRMask = document.querySelector('input[name="aggregation_cidr-mask"]')
    console.log(aggregationCIDRMask)

    customerInput.classList.remove('form-error')
    vlanInput.classList.remove('form-error') 
    accessPortSelect.classList.remove('form-error')
    uplinkPortSelect.classList.remove('form-error')
    ipv4AddressInput.classList.remove('form-error')
    aggregationPortSelect.classList.remove('form-error')  
    
    accessDeviceSelect.classList.remove('form-error')
    aggregationDeviceSelect.classList.remove('form-error')
    // debugger;
    aggregationCIDRMask.classList.remove('form-error')

    


    let formValid = true
    if (customerInput.value == '') {
        customerInput.classList.add('form-error')
        formValid = false
    }
    if (vlanInput.value == '') {
        vlanInput.classList.add('form-error')
        formValid = false
    }
    if (isNaN(parseInt(vlanInput.value))){        
        vlanInput.classList.add('form-error')
        formValid = false
    }

    if (accessPortSelect.value == '') {
        accessPortSelect.classList.add('form-error')
        formValid = false
    }
    if (uplinkPortSelect.value == '') {
        uplinkPortSelect.classList.add('form-error')
        formValid = false
    }
    if (ipv4AddressInput.value == '') {
        ipv4AddressInput.classList.add('form-error')
        formValid = false
    }
    if (aggregationPortSelect.value == '') {
        aggregationPortSelect.classList.add('form-error')
        formValid = false
    }
    if (accessDeviceSelect.value == '') {
        accessDeviceSelect.classList.add('form-error')
        formValid = false
    }
    if (aggregationDeviceSelect.value == '') {
        aggregationDeviceSelect.classList.add('form-error')
        formValid = false
    }
    // debugger;
    if (aggregationCIDRMask.value == '') {
        aggregationCIDRMask.classList.add('form-error')
        formValid = false
    }

    if (formValid == false) {
        event.preventDefault(); 
       
    } else {        
        event.preventDefault();
        renderModal();        
    }
}

// Render Confirmation Modal
function renderModal() {
    let confirmationTable = document.querySelector('#confirmation-table')
    confirmationTable.innerHTML = '';
    let formElement = document.querySelector('#dia-form');
    
    let formData = new FormData(formElement)
    let tableHTML = ''
    // debugger;
    for (var [key, value] of formData.entries()) {
        translatedKey = formFieldsDict[key]
        if (!(key.includes('csrf'))) {
            tableHTML = tableHTML + `<tr>\n <td>${translatedKey}</td>\n<td>${value}</td>\n</tr>`
        }         
      }

    confirmationTable.innerHTML = tableHTML;
    // debugger;
    let confirmationModal = new bootstrap.Modal(document.querySelector('#confirmationModal'));
    confirmationModal.toggle();

    
}


// Submit Form after confirmation
let confirmationModalSubmit = document.querySelector('#confirmation-modal-submit');
confirmationModalSubmit.addEventListener('click', () => {
    
    let confirmationModalSubmit = document.querySelector('#confirmation-modal-submit').disabled = true;
    let confirmationModalCancel = document.querySelector('#confirmation-modal-cancel').disabled = true;
    debugger;
    let form = document.querySelector('#dia-form');
    form.submit();
})

// Clear Button
let clearButton = document.querySelector('#clear-form-button');
clearButton.addEventListener('click', () => {
    let form = document.querySelector('#dia-form');
    form.reset();

    let customerInput = document.querySelector('input[name="customer_name"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    let checkBox = document.querySelector('input[name="reserve_ip"]')
    document.querySelectorAll('select[name="aggregation_ipv4-address"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="aggregation_access-interface"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="access_access-port"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="access_uplink-port"] option').forEach(o => o.remove())
    // let ipAddressInput = document.querySelector('input[name="aggregation_ipv4-address"]')
    // ipAddressInput.setAttribute('value', '')
    checkBox.removeAttribute('disabled', 'disabled')
    customerInput.removeAttribute('readonly', 'readonly')
    vlanInput.removeAttribute('readonly', 'readonly')
    
})

// Query IPv4 Address
function queryIpv4Address(){  
    let ipv4Spinner = document.querySelector('#ipv4-spinner');
    ipv4Spinner.className = 'spinner-border'
    let customerInput = document.querySelector('input[name="customer_name"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    let body = {"customer-name": customerInput.value, "vlan-number": vlanInput.value}
    document.querySelector('select[name="aggregation_ipv4-address"]').disabled = false;
    return fetch('/api/v1/query-ipv4-address/', {        
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json'
          },
        credentials: "same-origin"
    }).then (response => {
        
        return response.json().then(data => {
            // let ipAddressInput = document.querySelector('input[name="aggregation_ipv4-address"]')
            // ipAddressInput.setAttribute('value', data['ipv4-address'])
            ipAddrAndMask = data;
            // let ip = data['ipv4-address'];
            let ipAddressInput = document.querySelector('select[name="aggregation_ipv4-address"]');
            // for (let i = 0; i < ipAddrAndMask.length; i++){
            //     const singleIP = document.createElement('option');
            //     singleIP.innerHTML = ipAddrAndMask[i][0];
            //     ipAddressInput.add(singleIP);
            // }
            
            for (let key in ipAddrAndMask){
                const singleIP = document.createElement('option');
                singleIP.innerHTML = key;
                ipAddressInput.add(singleIP);
            }

            let ipv4Spinner = document.querySelector('#ipv4-spinner');
            ipv4Spinner.className = 'spinner-border d-none'
        })        
    })        
}

// Update the subnet mask according to the ipAddress user selected
document.addEventListener('DOMContentLoaded', function(){
    let CIDRMask = document.querySelector('input[name="aggregation_cidr-mask"]')
    let IPv4Addr = document.querySelector('select[name="aggregation_ipv4-address"]')
    IPv4Addr.onchange = function(){
        const selectedIP = IPv4Addr.options[IPv4Addr.selectedIndex].text
        console.log(ipAddrAndMask[selectedIP])
        CIDRMask.value = ipAddrAndMask[selectedIP]
    }
})

// Detect Reserv IP Address Button
let checkBox = document.querySelector('input[name="reserve_ip"]')
checkBox.addEventListener('change', () => {
    let customerInput = document.querySelector('input[name="customer_name"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    customerInput.classList.remove('form-error')
    vlanInput.classList.remove('form-error') 
    if (customerInput.value == '') {        
        checkBox.checked = false
        customerInput.classList.add('form-error')        
    } 
    if (isNaN(parseInt(vlanInput.value))){
        checkBox.checked = false
        vlanInput.classList.add('form-error')
    }
    
    if (vlanInput.value == '') {        
        checkBox.checked = false
        vlanInput.classList.add('form-error')        
    } 
    if (checkBox.checked) {
        checkBox.setAttribute('disabled', 'disabled')
        customerInput.setAttribute('readonly', 'readonly')
        vlanInput.setAttribute('readonly', 'readonly')
        queryIpv4Address()
    } 
})

// Render Access Ports
let accessDeviceSelect = document.querySelector('select[name="access_device-name"]')
accessDeviceSelect.addEventListener('change', () => {

    let accessPortSpinner = document.querySelector('#access-port-spinner')
    let uplinkPortSpinner = document.querySelector('#uplink-port-spinner')
    accessPortSpinner.classList.remove('d-none')
    uplinkPortSpinner.classList.remove('d-none')

    let accessPortSelect = document.querySelector('select[name="access_access-port"]')
    let uplinkPortSelect = document.querySelector('select[name="access_uplink-port"]')        
    accessPortSelect.innerHTML = '';
    uplinkPortSelect.innerHTML = '';

    let accessDevice = accessDeviceSelect.value        
    body = {"device": accessDevice}
    fetch('/api/v1/get-access-interfaces/', {        
        method: 'POST',        
        body: JSON.stringify(body),
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json'
          },
        credentials: "same-origin"
    }).then (response => {        
        return response.json().then(data => {
            accessPortSpinner.classList.add('d-none')
            uplinkPortSpinner.classList.add('d-none')
            let accessPortsHTML = '';            
            for (let i = 0; i < data['access-ports'].length; i++ ) {
                let port = data['access-ports'][i];
                accessPortsHTML = accessPortsHTML + `<option value="${port}" >${port}</option>\n`;
            }
            accessPortSelect.innerHTML = accessPortsHTML

            let uplinkPortsHTML = '';
            for (let i = 0; i < data['uplink-ports'].length; i++ ) {
                let port = data['uplink-ports'][i];
                uplinkPortsHTML = uplinkPortsHTML + `<option value="${port}" >${port}</option>\n`;
            }
            uplinkPortSelect.innerHTML = uplinkPortsHTML
            
        })        
    })
});
// Render Aggregation Ports
let aggregationDeviceSelect = document.querySelector('select[name="aggregation_device-name"]')
aggregationDeviceSelect.addEventListener('change', () => {
    let aggregationPortSpinner = document.querySelector('#aggregation-port-spinner')
    aggregationPortSpinner.classList.remove('d-none')
    let aggregationPortSelect = document.querySelector('select[name="aggregation_access-interface"]')
    aggregationPortSelect.innerHTML = '';

    let aggregationDevice = aggregationDeviceSelect.value        
    body = {"device": aggregationDevice}
    fetch('/api/v1/get-aggregation-interfaces/', {        
        method: 'POST',        
        body: JSON.stringify(body),
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json'
          },
        credentials: "same-origin"
    }).then (response => {        
        return response.json().then(data => {
            aggregationPortSpinner.classList.add('d-none')
            let aggregationPortsHTML = '';
            
            for (let i = 0; i < data['aggregation-ports'].length; i++ ) {
                let port = data['aggregation-ports'][i];
                aggregationPortsHTML = aggregationPortsHTML + `<option value="${port}" >${port}</option>\n`;
            }
            aggregationPortSelect.innerHTML = aggregationPortsHTML
        
        })        
    })
});
