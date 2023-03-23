const formFieldsDict = {
    "customer_account": "Account #",
    "customer_name": "Customer Name",
    "vlan_number": "VLAN",
    "primary_router_downlink": "Hub router downlink",
    "primary_router_distinguisher": "Hub router distinguisher",
    "primary_router_vrf": "Hub router vrf",
    "access_access-port": "Hub switch access-port",
    "access_uplink-port": "Hub switch uplink-port",
    "remote_router_downlink": "Remote router downlink",
    "remote_router_distinguisher": "Remote router distinguisher",
    "remote_router_vrf": "Remote router vrf",
    "remote_access_uplink-port": "Remote switch uplink-port"
}

let ipAddrAndMask = {}
let customerAddress = {}

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

function check_form(event) {
    //CDA
    //let customerInput = document.querySelector('input[name="customer_name"]')
    let customerInput = document.querySelector('input[name="customer_account"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    //alert('customer len:' + customerInput.value.length);
    //alert('vlan len:' + vlanInput.value.length);
    //alert('customer len:' + length(customerInput.value));

    if (customerInput.value.length > 2 && vlanInput.value.length > 2) {
        //alert('cust value:' + customerInput.value.length);
        //alert('both values are there' );
        queryCustomerAddress()

    }


}


// Validate Form at Submit Event Raise Confirmation Modal
function validateForm(event) {
    let customerInput = document.querySelector('input[name="customer_account"]')
    let customerName = document.querySelector('input[name="customer_name"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    // let ipv4AddressInput = document.querySelector('select[name="aggregation_ipv4-address"]')
    let aggregationDeviceSelect = document.querySelector('select[name="aggregation_device-name"]')
    let routerDownlinkSelect = document.querySelector('select[name="primary_router_downlink"]')
    let routerDistinguisherSelect = document.querySelector('select[name="primary_router_distinguisher"]')
    let routeVrfSelect = document.querySelector('select[name="primary_router_vrf"]')
    let accessDeviceSelect = document.querySelector('select[name="access_device-name"]')
    let accessPortSelect = document.querySelector('select[name="access_access-port"]')
    let uplinkPortSelect = document.querySelector('select[name="access_uplink-port"]')
    // let aggregationPortSelect = document.querySelector('select[name="aggregation_access-interface"]')
    let remoteAggregationDeviceSelect = document.querySelector('select[name="remote_aggregation_device-name"]')
    let remoteRouterDownlinkSelect = document.querySelector('select[name="remote_router_downlink"]')
    let remoteRouterDistinguisherSelect = document.querySelector('select[name="remote_router_distinguisher"]')
    let remoteRouteVrfSelect = document.querySelector('select[name="remote_router_vrf"]')
    let remoteAccessDeviceSelect = document.querySelector('select[name="remote_access_device-name"]')
    let remoteUplinkPortSelect = document.querySelector('select[name="remote_access_uplink-port"]')
    // let aggregationCIDRMask = document.querySelector('select[name="aggregation_cidr-mask"]')


    customerInput.classList.remove('form-error')
    customerName.classList.remove('form-error')
    vlanInput.classList.remove('form-error')
    aggregationDeviceSelect.classList.remove('form-error')
    routerDownlinkSelect.classList.remove('form-error')
    routerDistinguisherSelect.classList.remove('form-error')
    routeVrfSelect.classList.remove('form-error')
    accessDeviceSelect.classList.remove('form-error')
    accessPortSelect.classList.remove('form-error')
    uplinkPortSelect.classList.remove('form-error')
    remoteAggregationDeviceSelect.classList.remove('form-error')
    remoteRouterDownlinkSelect.classList.remove('form-error')
    remoteRouterDistinguisherSelect.classList.remove('form-error')
    remoteRouteVrfSelect.classList.remove('form-error')
    remoteAccessDeviceSelect.classList.remove('form-error')
    remoteUplinkPortSelect.classList.remove('form-error')



    let formValid = true
    if (customerInput.value == '') {
        customerInput.classList.add('form-error')
        formValid = false
    }
    if (customerName.value == '') {
        customerName.classList.add('form-error')
        formValid = false
    }
    if (vlanInput.value == '') {
        vlanInput.classList.add('form-error')
        formValid = false
    }
    if (isNaN(parseInt(vlanInput.value))) {
        vlanInput.classList.add('form-error')
        formValid = false
    }

    if (aggregationDeviceSelect.value == '') {
        aggregationDeviceSelect.classList.add('form-error')
        formValid = false
    }
    if (routerDownlinkSelect.value == '') {
        routerDownlinkSelect.classList.add('form-error')
        formValid = false
    }
    if (routerDistinguisherSelect.value == '') {
        routerDistinguisherSelect.classList.add('form-error')
        formValid = false
    }
    if (routeVrfSelect.value == '') {
        routeVrfSelect.classList.add('form-error')
        formValid = false
    }
    if (accessDeviceSelect.value == '') {
        accessDeviceSelect.classList.add('form-error')
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
    if (remoteAggregationDeviceSelect.value == '') {
        remoteAggregationDeviceSelect.classList.add('form-error')
        formValid = false
    }
    if (remoteRouterDownlinkSelect.value == '') {
        remoteRouterDownlinkSelect.classList.add('form-error')
        formValid = false
    }
    if (remoteRouterDistinguisherSelect.value == '') {
        remoteRouterDistinguisherSelect.classList.add('form-error')
        formValid = false
    }
    if (remoteRouteVrfSelect.value == '') {
        remoteRouteVrfSelect.classList.add('form-error')
        formValid = false
    }
    if (remoteAccessDeviceSelect.value == '') {
        remoteAccessDeviceSelect.classList.add('form-error')
        formValid = false
    }
    if (remoteUplinkPortSelect.value == '') {
        remoteUplinkPortSelect.classList.add('form-error')
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

    document.querySelector('#confirmation-modal-submit').disabled = true;
    document.querySelector('#confirmation-modal-cancel').disabled = true;
    document.querySelector('select[name="access_device-name"]').disabled = false;
    document.querySelector('select[name="aggregation_device-name"]').disabled = false;
    document.querySelector('select[name="remote_access_device-name"]').disabled = false;
    document.querySelector('select[name="remote_aggregation_device-name"]').disabled = false;
    document.querySelector('select[name="primary_router_downlink"]').disabled = false;
    document.querySelector('select[name="primary_router_distinguisher"]').disabled = false;
    document.querySelector('select[name="primary_router_vrf"]').disabled = false;
    document.querySelector('select[name="access_uplink-port"]').disabled = false;
    document.querySelector('select[name="remote_router_downlink"]').disabled = false;
    document.querySelector('select[name="remote_router_distinguisher"]').disabled = false;
    document.querySelector('select[name="remote_router_vrf"]').disabled = false;
    document.querySelector('select[name="remote_access_uplink-port"]').disabled = false;
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
    let address = document.getElementById('customer_address')
    document.querySelectorAll('select[name="primary_router_downlink"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="primary_router_distinguisher"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="primary_router_vrf"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="access_access-port"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="access_uplink-port"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="remote_router_downlink"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="remote_router_distinguisher"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="remote_router_vrf"] option').forEach(o => o.remove())
    document.querySelectorAll('select[name="remote_access_uplink-port"] option').forEach(o => o.remove())
    customerInput.removeAttribute('readonly', 'readonly')
    vlanInput.removeAttribute('readonly', 'readonly')
    address.innerHTML = ""
    address.hidden = true

    document.querySelector('select[name="access_device-name"]').disabled = false;
    document.querySelector('select[name="aggregation_device-name"]').disabled = false;
    document.querySelector('select[name="remote_access_device-name"]').disabled = false;
    document.querySelector('select[name="remote_aggregation_device-name"]').disabled = false;
    document.querySelector('select[name="primary_router_downlink"]').disabled = false;
    document.querySelector('select[name="primary_router_distinguisher"]').disabled = false;
    document.querySelector('select[name="primary_router_vrf"]').disabled = false;
    document.querySelector('select[name="access_uplink-port"]').disabled = false;
    document.querySelector('select[name="remote_router_downlink"]').disabled = false;
    document.querySelector('select[name="remote_router_distinguisher"]').disabled = false;
    document.querySelector('select[name="remote_router_vrf"]').disabled = false;
    document.querySelector('select[name="remote_access_uplink-port"]').disabled = false;

})


// Query customer Address
function queryCustomerAddress() {
    let customerInput = document.querySelector('input[name="customer_account"]')
    let customerName = document.querySelector('input[name="customer_name"]')
    let vlanInput = document.querySelector('input[name="vlan_number"]')
    let body = { "customer-acc": customerInput.value, "vlan-number": vlanInput.value }

    return fetch('/api/v1/query-customer-address/', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json'
        },
        credentials: "same-origin"
    }).then(response => {

        return response.json().then(data => {
            customerAddress = data;
            console.log(customerAddress)
            console.log(customerAddress["customerDetail"])
            let address = document.getElementById('customer_address')
            address.removeAttribute("hidden")
            address.innerHTML = customerAddress["customerDetail"]
            customerName.value = customerAddress["customerName"]
        })
    })
}


// load all sysname - CDA
document.addEventListener('DOMContentLoaded', function () {
    //  querySysname()
    //let element = document.getElementById('navBarForm_epl');
    let element = document.getElementById('navBarForm123');
    //alert("Hi from EPL JS page");
    element.classList.add('active');
})


function cal_interface(event) {
    let accessDeviceSelect = document.querySelector('select[name="access_device-name"]')
    let aggregationDeviceSelect = document.querySelector('select[name="aggregation_device-name"]')
    let vlan = document.querySelector('input[name="vlan_number"]')
    if (vlan.value == "") {
        alert("please enter the VLAN number first")
        let form = document.querySelector('#dia-form')
        form.reset()
    }
    else if (aggregationDeviceSelect.value != "" && accessDeviceSelect.value != "") {
        let accessPortSpinner = document.querySelector('#access-port-spinner')
        let uplinkPortSpinner = document.querySelector('#uplink-port-spinner')
        let aggregationPortSpinner = document.querySelector('#aggregation-port-spinner')
        let routerDistinguisherSpinner = document.querySelector('#router-distinguisher-spinner')
        let routerVrfSpinner = document.querySelector('#router-vrf-spinner')
        accessPortSpinner.classList.remove('d-none')
        uplinkPortSpinner.classList.remove('d-none')
        aggregationPortSpinner.classList.remove('d-none')
        routerDistinguisherSpinner.classList.remove('d-none')
        routerVrfSpinner.classList.remove('d-none')
        accessDeviceSelect.disabled = true
        aggregationDeviceSelect.disabled = true

        let accessPortSelect = document.querySelector('select[name="access_access-port"]')
        let uplinkPortSelect = document.querySelector('select[name="access_uplink-port"]')
        let aggregationPortSelect = document.querySelector('select[name="primary_router_downlink"]')
        let routeDistinguisherSelect = document.querySelector('select[name="primary_router_distinguisher"]')
        let vrfTargetSelect = document.querySelector('select[name="primary_router_vrf"]')
        accessPortSelect.innerHTML = '';
        uplinkPortSelect.innerHTML = '';
        aggregationPortSelect.innerHTML = '';
        routeDistinguisherSelect.innerHTML = '';
        vrfTargetSelect.innerHTML = '';

        let accessDevice = accessDeviceSelect.value
        let aggregationDevice = aggregationDeviceSelect.value
        let vlanNumber = vlan.value
        body = { "eds_switch": accessDevice, "acx_router": aggregationDevice, "vlan": vlanNumber }
        fetch('/api/v1/epl-get-all-interfaces/', {
            method: 'POST',
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
            },
            credentials: "same-origin"
        }).then(response => {
            return response.json().then(data => {
                accessPortSpinner.classList.add('d-none')
                uplinkPortSpinner.classList.add('d-none')
                aggregationPortSpinner.classList.add('d-none')
                routerDistinguisherSpinner.classList.add('d-none')
                routerVrfSpinner.classList.add('d-none')
                let accessPortsHTML = '';
                for (let i = 0; i < data['access-ports'].length; i++) {
                    let port = data['access-ports'][i];
                    accessPortsHTML = accessPortsHTML + `<option value="${port}" >${port}</option>\n`;
                }
                accessPortSelect.innerHTML = accessPortsHTML

                let uplinkPortsHTML = '';
                for (let i = 0; i < data['uplink-ports'].length; i++) {
                    let port = data['uplink-ports'][i];
                    uplinkPortsHTML = uplinkPortsHTML + `<option value="${port}" >${port}</option>\n`;
                }
                uplinkPortSelect.innerHTML = uplinkPortsHTML
                if (data['uplink-ports'].length == 1) {
                    uplinkPortSelect.disabled = true
                }

                let aggregationPortsHTML = '';
                for (let i = 0; i < data['aggregation-ports'].length; i++) {
                    let port = data['aggregation-ports'][i];
                    aggregationPortsHTML = aggregationPortsHTML + `<option value="${port}" >${port}</option>\n`;
                }
                aggregationPortSelect.innerHTML = aggregationPortsHTML
                if (data['aggregation-ports'].length == 1) {
                    aggregationPortSelect.disabled = true
                }

                let routeDistinguisherHTML = '';
                for (let i = 0; i < data['route-distinguisher'].length; i++) {
                    let route = data['route-distinguisher'][i];
                    routeDistinguisherHTML = routeDistinguisherHTML + `<option value="${route}" >${route}</option>\n`;
                }
                routeDistinguisherSelect.innerHTML = routeDistinguisherHTML
                if (data['route-distinguisher'].length == 1) {
                    routeDistinguisherSelect.disabled = true
                }

                let vrfTargetHTML = '';
                for (let i = 0; i < data['vrf-target'].length; i++) {
                    let vrf = data['vrf-target'][i];
                    vrfTargetHTML = vrfTargetHTML + `<option value="${vrf}" >${vrf}</option>\n`;
                }
                vrfTargetSelect.innerHTML = vrfTargetHTML
                if (data['vrf-target'].length == 1) {
                    vrfTargetSelect.disabled = true
                }

            })
        })
    } else {
        alert("please select the other primary router/switch")
    }

}


function cal_remote_interface(event) {
    let accessDeviceSelect = document.querySelector('select[name="remote_access_device-name"]')
    let aggregationDeviceSelect = document.querySelector('select[name="remote_aggregation_device-name"]')
    let vlan = document.querySelector('input[name="vlan_number"]')
    let hubVRF = document.querySelector('select[name="primary_router_vrf"]')
    if (vlan.value == "") {
        alert("please enter the VLAN number first")
        let form = document.querySelector('#dia-form')
        form.reset()
    }
    else if (hubVRF.value == "") {
        alert("please wait until the Primary router VRF Target shows up")
    }
    else if (aggregationDeviceSelect.value != "" && accessDeviceSelect.value != "") {
        console.log(hubVRF.value)
        console.log(vlan.value)
        // let accessPortSpinner = document.querySelector('#access-port-spinner')
        let uplinkPortSpinner = document.querySelector('#remote-uplink-port-spinner')
        let aggregationPortSpinner = document.querySelector('#remote-aggregation-port-spinner')
        let routerDistinguisherSpinner = document.querySelector('#remote-router-distinguisher-spinner')
        let routerVrfSpinner = document.querySelector('#remote-router-vrf-spinner')
        // accessPortSpinner.classList.remove('d-none')
        uplinkPortSpinner.classList.remove('d-none')
        aggregationPortSpinner.classList.remove('d-none')
        routerDistinguisherSpinner.classList.remove('d-none')
        routerVrfSpinner.classList.remove('d-none')
        accessDeviceSelect.disabled = true
        aggregationDeviceSelect.disabled = true

        // let accessPortSelect = document.querySelector('select[name="access_access-port"]')
        let uplinkPortSelect = document.querySelector('select[name="remote_access_uplink-port"]')
        let aggregationPortSelect = document.querySelector('select[name="remote_router_downlink"]')
        let routeDistinguisherSelect = document.querySelector('select[name="remote_router_distinguisher"]')
        let vrfTargetSelect = document.querySelector('select[name="remote_router_vrf"]')
        // accessPortSelect.innerHTML = '';
        uplinkPortSelect.innerHTML = '';
        aggregationPortSelect.innerHTML = '';
        routeDistinguisherSelect.innerHTML = '';
        vrfTargetSelect.innerHTML = '';

        let accessDevice = accessDeviceSelect.value
        let aggregationDevice = aggregationDeviceSelect.value
        let vlanNumber = vlan.value
        body = { "eds_switch": accessDevice, "acx_router": aggregationDevice, "vlan": vlanNumber }
        fetch('/api/v1/epl-get-all-interfaces/', {
            method: 'POST',
            body: JSON.stringify(body),
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
            },
            credentials: "same-origin"
        }).then(response => {
            return response.json().then(data => {
                // accessPortSpinner.classList.add('d-none')
                uplinkPortSpinner.classList.add('d-none')
                aggregationPortSpinner.classList.add('d-none')
                routerDistinguisherSpinner.classList.add('d-none')
                routerVrfSpinner.classList.add('d-none')
                // let accessPortsHTML = '';            
                // for (let i = 0; i < data['access-ports'].length; i++ ) {
                //     let port = data['access-ports'][i];
                //     accessPortsHTML = accessPortsHTML + `<option value="${port}" >${port}</option>\n`;
                // }
                // accessPortSelect.innerHTML = accessPortsHTML

                let uplinkPortsHTML = '';
                for (let i = 0; i < data['uplink-ports'].length; i++) {
                    let port = data['uplink-ports'][i];
                    uplinkPortsHTML = uplinkPortsHTML + `<option value="${port}" >${port}</option>\n`;
                }
                uplinkPortSelect.innerHTML = uplinkPortsHTML
                if (data['uplink-ports'].length == 1) {
                    uplinkPortSelect.disabled = true
                }

                let aggregationPortsHTML = '';
                for (let i = 0; i < data['aggregation-ports'].length; i++) {
                    let port = data['aggregation-ports'][i];
                    aggregationPortsHTML = aggregationPortsHTML + `<option value="${port}" >${port}</option>\n`;
                }
                aggregationPortSelect.innerHTML = aggregationPortsHTML
                if (data['aggregation-ports'].length == 1) {
                    aggregationPortSelect.disabled = true
                }

                let routeDistinguisherHTML = '';
                for (let i = 0; i < data['route-distinguisher'].length; i++) {
                    let route = data['route-distinguisher'][i];
                    routeDistinguisherHTML = routeDistinguisherHTML + `<option value="${route}" >${route}</option>\n`;
                }
                routeDistinguisherSelect.innerHTML = routeDistinguisherHTML
                if (data['route-distinguisher'].length == 1) {
                    routeDistinguisherSelect.disabled = true
                }

                let vrfTargetHTML = '';
                let vrf = hubVRF.value
                vrfTargetHTML = vrfTargetHTML + `<option value="${vrf}" >${vrf}</option>\n`;
                vrfTargetSelect.innerHTML = vrfTargetHTML
                vrfTargetSelect.disabled = true

            })
        })
    } else {
        alert("please select the other remote router/switch")
    }

}