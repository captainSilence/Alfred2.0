from http.client import HTTPResponse
from traceback import print_tb
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST, require_GET
from rest_framework.decorators import api_view
from requests.auth import HTTPBasicAuth
from django.conf import settings
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from . import crq_ticket_class
import smtplib
import requests
import json
import sys
import time
import datetime
import pyodbc
import paramiko
import re
import psycopg2


states = {
    'diaSingleHome:start': 'Start',
    'diaSingleHome:pre-checks': 'Running Pre-Checks',
    'diaSingleHome:dia-service': 'Configure service on devices',
    'diaSingleHome:update-external': 'Updating external DB',
    'diaSingleHome:post-checks': 'Running Post-Checks',
    'diaSingleHome:completed': 'Completed',
}


# server = 'tcp:sql-product.corp.cableone.net'
# SQL-ProductPub.corp.cableone.net
server = '10.128.36.80'
database = 'CableOneInternet'
# server1 = 'SQL-GOLDENGATE\GOLDENGATE'
server1 = '10.128.35.118'
# database = 'network_automation'
database1 = 'SVCustom'
username = 'internetReadWrite'
password = 'j0hnnyb!@ze'
username1 = 'na_proxy'
password1 = '9tmoDRW4K24#%PEr'

# connect to PostgreSQL
# this will be either "localhost", a domain name, or an IP address.
t_host = "10.128.64.11"
t_port = "5432"  # default port for postgres server
t_dbname = "postgres"
t_user = "myprojectuser"
t_pw = "password"
pre_post_checks_key = r'!'

# email notification var
strFrom = 'bizhou.duan@cableone.biz'
strTo = 'bizhou.duan@cableone.biz, Sparklight-NetworkAutomation@cableone.biz'


@require_GET
@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')


@require_GET
@login_required(login_url='/login')
def logout_request(request):
    logout(request)
    return render(request, 'login.html', {'loggout': 'Successfully Logged out'})


@require_GET
@login_required(login_url='/login')
def form(request):
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=access/device-name'
    response_access = get_request(url)

    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=aggregation/device-name'
    response_aggregation = get_request(url)

    try:
        response_json_acc = json.loads(response_access.text)
        response_json_agg = json.loads(response_aggregation.text)
        params = {"access": response_json_acc['tailf-ncs:device-name'],
                  "aggregation": response_json_agg['tailf-ncs:device-name']}
    except Exception as e:
        print('Error', e)
    return render(request, 'form.html', params)


@require_GET
@login_required(login_url='/login')
def formepl(request):
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=access/device-name'
    response_access = get_request(url)

    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=aggregation/device-name'
    response_aggregation = get_request(url)

    try:
        response_json_acc = json.loads(response_access.text)
        response_json_agg = json.loads(response_aggregation.text)
        params = {"access": response_json_acc['tailf-ncs:device-name'],
                  "aggregation": response_json_agg['tailf-ncs:device-name']}
    except Exception as e:
        print('Error', e)

    return render(request, 'formepl.html', params)


@require_GET
@login_required(login_url='/login')
def table(request):
    # Query NSO for existing services
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome'
    response = get_request(url)
    params = {'data': []}
    try:
        response_json = json.loads(response.text)
        id = 0
        for entry in response_json['diaSingleHome:diaSingleHome']:
            id += 1
            params_dict = {}
            params_dict['id'] = id
            params_dict['customer_name'] = entry['customer-name']
            params_dict['vlan_number'] = entry['vlan-number']
            params_dict['switch'] = entry['access']['device-name']
            params_dict['router'] = entry['aggregation']['device-name']
            params_dict['plan'] = []
            params_dict['ticket'] = find_ticket_num(
                entry['customer-name'], entry['vlan-number'])

            params_dict['customer_acc'] = get_acc_number_by_name(
                entry['customer-name'], entry['vlan-number'])

            # Change [0] to [1] to include init component
            for state in entry['plan']['component'][0]['state']:
                params_dict['plan'].append(state)
                if state['status'] == 'reached':
                    params_dict['last_state'] = states[state['name']]
            params['data'].append(params_dict)
    except Exception as e:
        print('Error', e, file=sys.stderr)

    print(params)
    return render(request, 'table.html', params)


@require_GET
@login_required(login_url='/login')
def table_epl(request):
    # Query NSO for services
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/eplHubRemote:eplHubRemote'
    response = get_request(url)
    params = {'data': []}
    try:
        response_json = json.loads(response.text)        
        id = 0
        for entry in response_json['eplHubRemote:eplHubRemote']:
            id += 1
            params_dict = {}    
            params_dict['id'] = id
            params_dict['customer_name'] = entry['customer-name']
            params_dict['vlan_number'] = entry['vlan-number']
            params_dict['hubSwitch'] = entry['access']['device-name']
            params_dict['hubRouter'] = entry['hubRouter']['device-name']
            params_dict['remoteSwitch'] = entry['remoteAccess']['device-name']
            params_dict['remoteRouter'] = entry['remoteRouter']['device-name']        
            params_dict['customer_acc'], params_dict['ticket'], params_dict['status'] = epl_find_allInfo(entry['customer-name'], entry['vlan-number'])

            params['data'].append(params_dict)
            print(params)
    except Exception as e:
        print('Error', e, file=sys.stderr)


    return render(request, 'tableepl.html', params)


@require_GET
@login_required(login_url='/login')
def device_config(request, customer_name, vlan_number):
    headers = {"Content-Type": "application/yang-data+json"}
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}/get-modifications'
    response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth(
        settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    data = response.json()["diaSingleHome:output"]["cli"]["local-node"]["data"]
    router_config = removeSpace(data.split(
        'device')[2].replace("{", "").replace("}", ""))
    switch_config = removeSpace(data.split('device')[3].split(
        'diaChecks')[0].replace("{", "").replace("}", ""))
    config = {"aggregation": {"ACX Router": router_config},
              "access": {"EDS Switch": switch_config}}
    params = {'config': config, 'customer_name': customer_name,
              'vlan_number': vlan_number}

    return render(request, 'config.html', params)


@require_GET
@login_required(login_url='/login')
def details(request, customer_name, vlan_number):
    headers = {"Content-Type": "application/yang-data+json"}
    # API Create diaChecks start mark
    url = f'{settings.NSO_ADDRESS}/restconf/data/diaChecks:diaChecks'
    checksData = {
        "customer-name": customer_name,
        "vlan-number": vlan_number,
        "start": True
    }
    checks_response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(
        settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"diaChecks:diaChecks": [checksData]}), verify=False)
    print('create-dia-checks entry', checks_response, file=sys.stderr)

    # API Query NSO for services
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}'
    service_response = get_request(url)
    try:
        response_json = json.loads(service_response.text.replace('-', '_'))
        params = {'data': response_json['diaSingleHome:diaSingleHome'][0],
                  'customer_name': customer_name, 'vlan_number': vlan_number, 'log_entry': False}

        if params['data']['log']:
            params['log_entry'] = True

    except Exception as e:
        print('Error', e)

    return render(request, 'details.html', params)


@require_GET
@login_required(login_url='/login')
def detailsepl(request, customer_name, vlan_number):
    # API Query NSO for services
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/eplHubRemote:eplHubRemote={customer_name},{vlan_number}' 
    service_response = get_request(url)

    try:
        response_json = json.loads(service_response.text)
        params = {'data': response_json['eplHubRemote:eplHubRemote'][0], 'customer_name': customer_name, 'vlan_number': vlan_number, 'log_entry': False}
    except Exception as e:
        print('Error', e)
        return redirect(f'/error/{e}')

    return render(request, 'detailsepl.html', params)


@require_POST
@login_required(login_url='/login')
def submit(request):
    customer_acc = request.POST.get('customer_name')
    data = {}
    data['customer-name'] = get_cust_name(customer_acc)
    data['vlan-number'] = int(request.POST.get('vlan_number'))
    data['aggregation'] = {}
    data['aggregation']['device-name'] = request.POST.get(
        'aggregation_device-name')
    data['aggregation']['ipv4-address'] = request.POST.get(
        'aggregation_ipv4-address')
    data['aggregation']['cidr-mask'] = netmask_to_cidr(
        request.POST.get('aggregation_cidr-mask'))
    data['aggregation']['access-interface'] = request.POST.get(
        'aggregation_access-interface')
    data['access'] = {}
    data['access']['device-name'] = request.POST.get('access_device-name')
    data['access']['access-port'] = request.POST.get('access_access-port')
    data['access']['uplink-port'] = request.POST.get('access_uplink-port')
    user = request.user.username
    time = datetime.datetime.now()


    # Path NSO for services
    try:
        headers = {"Content-Type": "application/yang-data+json"}
        # API to remove pre-existant diaChecks object
        customer_name = data['customer-name']
        vlan_number = data['vlan-number']
        eds_switch = data['access']['device-name']
        car_router = data['aggregation']['device-name']
        clean_url = f'{settings.NSO_ADDRESS}/restconf/data/diaChecks:diaChecks={customer_name},{vlan_number}'
        requests.request('DELETE', clean_url, headers=headers, auth=HTTPBasicAuth(
            settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)

        # API to create service instance
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome'
        response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(
            settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"diaSingleHome:diaSingleHome": [data]}), verify=False)
        if response.status_code != 204:
            request.session['error_message'] = response.text
            return redirect(f'/error')

        # log the user activity into the DB
        conn = psycopg2.connect(host=t_host, port=t_port,
                                dbname=t_dbname, user=t_user, password=t_pw)
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute("INSERT INTO user_session (customer_acc_number, vlan, user_name, time_service_created) VALUES (%s, %s, %s, %s)",
                    (customer_acc, vlan_number, user, time))
        cur.execute("INSERT INTO dia_test (customer_acc_number, customer_name, vlan, ticket_number) VALUES (%s, %s, %s, %s)",
                    (customer_acc, customer_name, vlan_number, "NULL"))
        # commit the changes to the database
        conn.commit()
        # close the communication with the PostgresQL database
        cur.close()
        conn.close()

        # send email notification
        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Alfred 2.0 Login Notification'
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        text = f'user {user} has just submitted a DIA provisioning request for customer {customer_name}'
        msgText = MIMEText(text)
        msgAlternative.attach(msgText)

        connection = smtplib.SMTP(host='smtp-relay.corp.cableone.net', port=25)
        connection.starttls()
        connection.send_message(msgRoot)
        connection.quit()

    except Exception as e:
        return redirect(f'/error/{e}')

    
    return redirect(f"/details/{customer_name}/{vlan_number}")


@require_POST
@login_required(login_url='/login')
def submit_epl(request):
    customer_acc = request.POST.get('customer_account')
    customer_name = request.POST.get('customer_name')
    hubRouter = request.POST.get('aggregation_device-name')
    hubSwitch = request.POST.get('access_device-name') 
    remoteRouter = request.POST.get('remote_aggregation_device-name')
    remoteSwitch = request.POST.get('remote_access_device-name')
    vlan = request.POST.get('vlan_number')
    vlan_name = get_vlan_name(customer_name, hubRouter, remoteRouter, vlan)
    status = 'complete'
    data = {}
    data['customer-name'] = vlan_name
    data['vlan-number'] = int(vlan)
    data['access'] = {}
    data['access']['device-name'] = hubSwitch
    data['access']['access-port'] = request.POST.get('access_access-port')
    data['access']['uplink-port'] = request.POST.get('access_uplink-port')
    data['remoteAccess'] = {}
    data['remoteAccess']['device-name'] = remoteSwitch
    data['remoteAccess']['uplink-port'] = request.POST.get('remote_access_uplink-port')
    data['hubRouter'] = {}
    data['hubRouter']['device-name'] = hubRouter
    data['hubRouter']['route-distinguisher'] = request.POST.get('primary_router_distinguisher')
    data['hubRouter']['vrf-target'] = request.POST.get('primary_router_vrf')
    data['hubRouter']['access-interface'] = request.POST.get('primary_router_downlink')
    data['hubRouter']['site-number'] = int(1)
    data['remoteRouter'] = {}
    data['remoteRouter']['device-name'] = remoteRouter
    data['remoteRouter']['route-distinguisher'] = request.POST.get('remote_router_distinguisher')
    data['remoteRouter']['vrf-target'] = request.POST.get('remote_router_vrf')
    data['remoteRouter']['access-interface'] = request.POST.get('remote_router_downlink')
    data['remoteRouter']['site-number'] = int(2)
 
    user = request.user.username
    time = datetime.datetime.now()

    # Path NSO for services
    try:
        headers = {"Content-Type": "application/yang-data+json"}
        # API to create service instance
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/eplHubRemote:eplHubRemote'
        response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(
            settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"eplHubRemote:eplHubRemote": [data]}), verify=False)
        if response.status_code != 204:
            request.session['error_message'] = response.text
            return redirect(f'/error')

        # grab device config for the service instance
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/eplHubRemote:eplHubRemote={vlan_name},{vlan}/get-modifications'
        response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth(
            settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
        device_data = response.json()["eplHubRemote:output"]["cli"]["local-node"]["data"]
        print(device_data)
        
        # creating Remedy ticket for EPL service instance
        new_line = '\n'
        summary = f"EPL Circuit provisioning for customer {customer_name} with vlan {vlan}."
        description = f"Customer account: {customer_acc}, Vlan: {vlan}, Hub router: {hubRouter}, Hub switch: {hubSwitch}, Remote router: {remoteRouter}, Remote switch: {remoteSwitch}"
        description = f"Customer account: {customer_acc}, Vlan: {vlan}{new_line}{new_line}{device_data}"
        object = crq_ticket_class.crq_ticket()
        object.cls_start(summary, description)
        ticket_number = object.ticket_no

        # log the user activity into the DB
        conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute("INSERT INTO epl (customer_acc_number, customer_name, vlan, hub_router, hub_switch, remote_router, remote_switch, status, ticket_number, user_name, time_service_created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (customer_acc, vlan_name, vlan, hubRouter, hubSwitch, remoteRouter, remoteSwitch, status, ticket_number, user, time))

        # commit the changes to the database
        conn.commit()
        # close the communication with the PostgresQL database
        cur.close()
        conn.close()

        # send email notification
        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Alfred 2.0 Login Notification'
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        text = f'user {user} has just submitted a EPL provisioning request for customer {customer_name}'
        msgText = MIMEText(text)
        msgAlternative.attach(msgText)

        connection = smtplib.SMTP(host='smtp-relay.corp.cableone.net', port=25)
        connection.starttls()
        connection.send_message(msgRoot)
        connection.quit()
    except Exception as e:
        return redirect(f'/error/{e}')
    
    return redirect(f"/detailsepl/{vlan_name}/{vlan}")


@require_GET
@login_required(login_url='/login')
def error(request):
    error_message = request.session['error_message']
    return render(request, 'error.html', {'error_message': error_message})


@require_GET
def login_page(request):
    return render(request, 'login.html')


@require_POST
def login_request(request):
    redirectUrl = request.GET.get('next')
    if redirectUrl is None:
        redirectUrl = '/'

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            response = HttpResponseRedirect(redirectUrl)
            return response
    return render(request, 'login.html', {'message': 'Authentication Failure'})


@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_query_customer_address(request):
    data = request.data
    accountNumber = data['customer-acc']
    customerInfo = {"customerDetail": "", "custName": ""}
    c1_goldengateDB = pyodbc_db_connection(
        server1, database1, username1, password1)
    address = pyodbc_query(c1_goldengateDB, '''select NAME, ServiceStreetAddress1, ServiceCity, ServiceState
                                                from SVCustom.dbo.CustomerAddresses a
                                                inner join singleview.[dbo].[CUST_ACCT_PE_V] b on a.SingleviewAccount = b.[Primary Account Number]
                                                where SingleviewAccount = \'''' + accountNumber + "'")
    for line in address:
        name = line.NAME.strip().split(":")[1]
        streetAddress = line.ServiceStreetAddress1.lower().title()
        city = line.ServiceCity.lower().title()
        state = line.ServiceState
        customerInfo["customerDetail"] = f"Customer Name: {name}    Address: {streetAddress}, {city}, {state}"
        customerInfo["customerName"] = name
        print(customerInfo)

    return JsonResponse(customerInfo)


@require_GET
@login_required(login_url='/login')
@api_view(['GET'])
def api_get_all_sysname(request):
    sysname = []
    c1_productDB = pyodbc_db_connection(server, database, username, password)
    all_sysname = pyodbc_query(
        c1_productDB, "select distinct sysname from dbo.UbrNetworks")

    for line in all_sysname:
        if line.sysname != None:
            sysname.append(line.sysname.strip())
    sysname.sort()

    return JsonResponse({"city": sysname})


@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_query_ip(request):
    data = request.data
    accountNumber = data['customer-name']
    vlan_number = data['vlan-number']
    city = data['sysname']
    ipAddr = defaultdict(list)

    # c1_goldengateDB = pyodbc_db_connection(server1, database1, username1, password1)
    # address = pyodbc_query(c1_goldengateDB, '''select * from dbo.CustomerAddresses where SingleviewAccount = \'''' + accountNumber + "'")
    # for line in address:
    #     city = line.ServiceCity.lower().title()
    c1_productDB = pyodbc_db_connection(server, database, username, password)
    # ipPool = pyodbc_query(c1_productDB, '''select * from network_automation.dbo.UbrNetworks_copy where sysname = \'''' + city + '''' and username = \'''' + accountNumber + "' and ssu is null and macadd is null and wirelessActive is null")
    # if ipPool == []:
    #     ipPool = pyodbc_query(c1_productDB, '''select * from network_automation.dbo.UbrNetworks_copy where sysname = \'''' + city + "' and username is NULL")

    # ipPool = pyodbc_query(c1_productDB, '''select * from dbo.UbrNetworks where sysname = \'''' + city + '''' and username = \'''' + accountNumber + "' and ssu is null and macadd is null and wirelessActive is null")
    ipPool = pyodbc_query(c1_productDB, '''select * from dbo.UbrNetworks where username = \'''' +
                          accountNumber + "' and ssu = 'Fiber 'and macadd = 'Fiber' and wirelessActive = 0")
    if ipPool == []:
        ipPool = pyodbc_query(
            c1_productDB, '''select * from dbo.UbrNetworks where sysname = \'''' + city + "' and username is NULL")
    for ip in ipPool:
        ip_address = ip.block.strip()
        subnet_mask = ip.mask.strip()
        ipAddr[subnet_mask].append(ip_address)

    return JsonResponse(ipAddr)


# not in use, see get_all_interfaces function
@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_access_interfaces(request):
    data = request.data
    device = data['device']
    vlan666_ports = []
    json_response = {"access-ports": [], "uplink-ports": []}

    if device != '':
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cienacli-acos:vlan/add/vlan=666'
        response = get_request(url).json()

        for port in response["tailf-ned-cienacli-acos:vlan"][0]['port']:
            vlan666_ports.append(port['id'])

        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
        response = get_request(url).json()

        for port_dict in response["tailf-ned-cienacli-acos:set"]['port']:
            if port_is_access(port_dict, vlan666_ports) == True:
                json_response["access-ports"].append(port_dict["name"])
        for port_dict in response["tailf-ned-cienacli-acos:set"]['port']:
            if port_is_uplink(port_dict) == True:
                json_response["uplink-ports"].append(port_dict["name"])
    else:
        response = {}

    return JsonResponse(json_response)


# not in use, testing only, see get_all_interfaces function
@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_aggregation_interfaces(request):
    data = request.data
    device = data['device']
    json_response = {"aggregation-ports": []}
    if device != '':
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/junos:configuration/junos:interfaces'
        response = get_request(url).json()
        for port_dict in response["junos:interfaces"]['interface']:
            if port_is_aggregatrion(port_dict) == True:
                json_response["aggregation-ports"].append(port_dict["name"])
    else:
        response = {}
    return JsonResponse(json_response)


# DIA get uplink/downlink ports for router and switch
@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_all_interfaces(request):
    data = request.data
    switch = data['eds_switch']
    router = data['acx_router']
    vlan666_ports = []
    ports_removed_from_vlan666 = []
    all_access_ports = []
    uplink_port = []
    downlink_port = []
    ports = []
    json_response = {"access-ports": [], "uplink-ports": [], "aggregation-ports": []}
    url_eds_ip = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/remote/set/ip'
    url_car_ip = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={router}/config/junos:configuration/interfaces/interface=irb/unit=800/family/inet/address'
    url_all_vlan666 = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/add/vlan=666'
    url_vlan666_removed = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/remove/vlan=666'
    url_all_switch_ports = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
    url_all_router_ports = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={router}/config/junos:configuration/interfaces'
    startTime = time.time()

    if switch != '' and router != '':

        # API to sync the devices
        with ThreadPoolExecutor() as pool:
            pool.submit(sync_from, router)
            pool.submit(sync_from, switch)


        with ThreadPoolExecutor() as pool:
            future_eds_ip = pool.submit(get_request, url_eds_ip)
            future_car_ip = pool.submit(get_request, url_car_ip)
            future_all_vlan666 = pool.submit(get_request, url_all_vlan666)
            future_vlan666_removed = pool.submit(get_request, url_vlan666_removed)
            future_all_switch_ports = pool.submit(get_request, url_all_switch_ports)
            future_all_router_ports = pool.submit(get_request, url_all_router_ports)

            # get switch ip
            response = future_eds_ip.result()
            eds_ip = response.json()['tailf-ned-cienacli-acos:ip'].split('/')[0]

            # get router MGMT ip
            response = future_car_ip.result()
            if response.status_code == 200:
                car_ip = response.json()['junos:address'][0]['name'].split('/')[0]
            else: 
                url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/set/gateway'
                response = get_request(url)
                car_ip = response.json()['tailf-ned-cienacli-acos:gateway']

            # get all vlan 666 ports
            response = future_all_vlan666.result()
            for port in response.json()["tailf-ned-cienacli-acos:vlan"][0]['port']:
                vlan666_ports.append(port['id'])

            # get all ports are remved from vlan 666
            response = future_vlan666_removed.result()
            if response.status_code == 200:
                for port in response.json()["tailf-ned-cienacli-acos:vlan"][0]['port']:
                    ports_removed_from_vlan666.append(port['id'])

            # get all ports from switch
            response = future_all_switch_ports.result()
            for port_dict in response.json()["tailf-ned-cienacli-acos:set"]['port']:
                if port_is_access(port_dict, vlan666_ports) == True and remove_port_from_vlan666(port_dict, ports_removed_from_vlan666) == True:
                    json_response["access-ports"].append(port_dict["name"])

                all_access_ports.append(port_dict["name"])

            # get all ports from router
            response = future_all_router_ports.result()
            for port in response.json()['junos:interfaces']['interface']:
                ports.append(port['name'])


        # calculate uplink/downlink ports
        with ThreadPoolExecutor() as pool:
            future_uplink = pool.submit(calculate_access_uplink, eds_ip, car_ip)
            future_downlink = pool.submit(calculate_agg_downlink, eds_ip, car_ip)
            pool.shutdown(wait=True)
            try:
                uplink_port.append(future_uplink.result())
            except:
                uplink_port = all_access_ports
            
            try:
                downlink_port.append(future_downlink.result())
            except:
                downlink_port = ports

        json_response["uplink-ports"] = uplink_port
        json_response["aggregation-ports"] = downlink_port

    else:
        response = {}

    execute_Time = time.time() - startTime
    print("Request completed in {0:.0f}s".format(execute_Time))
    print(json_response)
    return JsonResponse(json_response)


## EPL get uplink/downlink ports for router and switch
@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_all_epl_interfaces(request):
    data = request.data
    switch = data['eds_switch']
    router = data['acx_router']
    vlan = data['vlan']
    vlan666_ports = []
    ports_removed_from_vlan666 = []
    all_access_ports = []
    uplink_port = []
    downlink_port = []
    ports = []
    json_response = {"access-ports": [], "uplink-ports": [], "aggregation-ports": [], "route-distinguisher": [], "vrf-target": []}
    url_eds_ip = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/remote/set/ip'
    url_car_ip = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={router}/config/junos:configuration/interfaces/interface=irb/unit=800/family/inet/address'
    url_all_vlan666 = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/add/vlan=666'
    url_vlan666_removed = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/remove/vlan=666'
    url_all_switch_ports = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
    url_all_router_ports = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={router}/config/junos:configuration/interfaces'
    startTime = time.time()

    if switch != '' and router != '':

        # API to sync the devices
        with ThreadPoolExecutor() as pool:
            pool.submit(sync_from, router)
            pool.submit(sync_from, switch)


        with ThreadPoolExecutor() as pool:
            future_eds_ip = pool.submit(get_request, url_eds_ip)
            future_car_ip = pool.submit(get_request, url_car_ip)
            future_all_vlan666 = pool.submit(get_request, url_all_vlan666)
            future_vlan666_removed = pool.submit(get_request, url_vlan666_removed)
            future_all_switch_ports = pool.submit(get_request, url_all_switch_ports)
            future_all_router_ports = pool.submit(get_request, url_all_router_ports)

            # get switch ip
            response = future_eds_ip.result()
            eds_ip = response.json()['tailf-ned-cienacli-acos:ip'].split('/')[0]

            # get router MGMT ip
            response = future_car_ip.result()
            if response.status_code == 200:
                car_ip = response.json()['junos:address'][0]['name'].split('/')[0]
            else: 
                url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/set/gateway'
                response = get_request(url)
                car_ip = response.json()['tailf-ned-cienacli-acos:gateway']

            # get all vlan 666 ports
            response = future_all_vlan666.result()
            for port in response.json()["tailf-ned-cienacli-acos:vlan"][0]['port']:
                vlan666_ports.append(port['id'])

            # get all ports are remved from vlan 666
            response = future_vlan666_removed.result()
            if response.status_code == 200:
                for port in response.json()["tailf-ned-cienacli-acos:vlan"][0]['port']:
                    ports_removed_from_vlan666.append(port['id'])

            # get all ports from switch
            response = future_all_switch_ports.result()
            for port_dict in response.json()["tailf-ned-cienacli-acos:set"]['port']:
                if port_is_access(port_dict, vlan666_ports) == True and remove_port_from_vlan666(port_dict, ports_removed_from_vlan666) == True:
                    json_response["access-ports"].append(port_dict["name"])

                all_access_ports.append(port_dict["name"])

            # get all ports from router
            response = future_all_router_ports.result()
            for port in response.json()['junos:interfaces']['interface']:
                ports.append(port['name'])


        # calculate uplink/downlink ports
        with ThreadPoolExecutor() as pool:
            future_uplink = pool.submit(calculate_access_uplink, eds_ip, car_ip)
            future_downlink = pool.submit(calculate_agg_downlink, eds_ip, car_ip)
            future_route_distinguisher = pool.submit(calculate_route_distinguisher, router, vlan)
            future_vrf_target = pool.submit(calculate_vrf_target, router, vlan)
            try:
                uplink_port.append(future_uplink.result())
            except:
                uplink_port = all_access_ports
            
            try:
                downlink_port.append(future_downlink.result())
            except:
                downlink_port = ports

            json_response["uplink-ports"] = uplink_port
            json_response["aggregation-ports"] = downlink_port
            json_response["route-distinguisher"].append(future_route_distinguisher.result())
            json_response["vrf-target"].append(future_vrf_target.result())

    else:
        response = {}

    execute_Time = time.time() - startTime
    print("Request completed in {0:.0f}s".format(execute_Time))
    print(json_response)
    return JsonResponse(json_response)


# Validate Ports, check to see if port is in vlan 666 list
def port_is_access(port_dict, vlan666_dict):
    if port_dict["name"] in vlan666_dict:
        return True
    else:
        return False


# Validate Ports, check to see if port is not in removed vlan 666 list
def remove_port_from_vlan666(port_dict, ports_removed_from_vlan666):
    if port_dict["name"] not in ports_removed_from_vlan666:
        return True
    else:
        return False


def port_is_uplink(port_dict):
    return True


def port_is_aggregatrion(port_dict):
    return True


def pyodbc_db_connection(server, database, username, password):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    return cursor


def pyodbc_query(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def netmask_to_cidr(netmask):
    # param netmask: netmask ip addr (eg: 255.255.255.0)
    # return: equivalent cidr number to given netmask ip (eg: 24)
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])


def calculate_access_uplink(eds_ip, acx_ip):
    print(eds_ip, acx_ip)
    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    child.connect(eds_ip, 22, settings.AD_USER, settings.AD_PASSWORD)
    stdin, stdout, stderr = child.exec_command(f'arp show intf remote')
    string = stdout.read().decode('ascii').strip("\n")
    mac = re.search(
        f"\|\s+{acx_ip}\s+\|\s+(\w+:\w+:\w+:\w+:\w+:\w+)", string).group(1)

    stdin, stdout, stderr = child.exec_command(f'flow mac-addr show mac {mac}')
    string = stdout.read().decode('ascii').strip("\n")
    uplinkport = re.search(
        f"800\s*\|\s+{mac}\s\|\s+(.+?)\s+\|", string, re.IGNORECASE).group(1)

    return uplinkport


def calculate_agg_downlink(eds_ip, acx_ip):
    print(eds_ip, acx_ip)
    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    child.connect(acx_ip, 22, settings.AD_USER, settings.AD_PASSWORD)
    stdin, stdout, stderr = child.exec_command(
        f'show arp no-resolve | match {eds_ip}')
    string = stdout.read().decode('ascii').strip("\n")
    mac = re.search(f"(\w+:\w+:\w+:\w+:\w+:\w+)\s+{eds_ip}", string).group(1)

    stdin, stdout, stderr = child.exec_command(f'show arp | except em')
    string = stdout.read().decode('ascii').strip("\n")
    outIntf = re.search(f"{mac}.+\s+\[*(\w+-\d+[\/]\d+[\/]\d+)", string)
    outIntfae = re.search(f"{mac}.+\s+\[*(ae\d+)", string)

    if outIntf:
        downlink = outIntf.group(1)
    elif outIntfae:
        downlink = outIntfae.group(1)

    return downlink


def removeSpace(string_with_empty_lines):
    lines = string_with_empty_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    string_without_empty_lines = ""

    for line in non_empty_lines:
        string_without_empty_lines += line + "\n"

    return string_without_empty_lines


def find_ticket_num(customer_name, vlan):
    conn = psycopg2.connect(host=t_host, port=t_port,
                            dbname=t_dbname, user=t_user, password=t_pw)
    cur = conn.cursor()
    cur.execute(
        f"SELECT ticket_number FROM dia_test where customer_name = '{customer_name}' and vlan = {vlan};")
    ticket_num = cur.fetchone()
    cur.close()
    conn.close()

    if ticket_num == None:
        return "No CRQ Found"
    else:
        return ticket_num[0]


def epl_find_allInfo(customer_name, vlan):
    conn = psycopg2.connect(host=t_host, port=t_port,
                            dbname=t_dbname, user=t_user, password=t_pw)
    cur = conn.cursor()
    cur.execute(
        f"SELECT customer_acc_number, ticket_number, status FROM epl where customer_name = '{customer_name}' and vlan = {vlan};")
    info = cur.fetchone()
    cur.close()
    conn.close()

    customer_acc = info[0]
    ticket_num = info[1]
    status = info[2]
    if customer_acc == None:
        customer_acc = "No acc Found"
    if ticket_num == None:
        ticket_num = "No CRQ Found"
    if status == None:
        status = "Status Unknow"
    
    return customer_acc, ticket_num, status


def get_cust_name(accountNumber):
    c1_goldengateDB = pyodbc_db_connection(
        server1, database1, username1, password1)
    address = pyodbc_query(c1_goldengateDB, '''select NAME, ServiceStreetAddress1, ServiceCity, ServiceState
                                                from SVCustom.dbo.CustomerAddresses a
                                                inner join singleview.[dbo].[CUST_ACCT_PE_V] b on a.SingleviewAccount = b.[Primary Account Number]
                                                where SingleviewAccount = \'''' + accountNumber + "'")
    for line in address:
        name = line.NAME.strip().split(":")[1]
    cust_name = name.replace(" ", "_")
    cust_name = cust_name[:27] if len(cust_name) > 27 else cust_name

    return cust_name


def get_acc_number_by_name(customerName, vlan):
    # log the user activity into the DB
    conn = psycopg2.connect(host=t_host, port=t_port,
                            dbname=t_dbname, user=t_user, password=t_pw)
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(
        f"SELECT customer_acc_number FROM dia_test where customer_name = '{customerName}' and vlan = {vlan};")
    cust_acc_number = cur.fetchone()
    # close the communication with the PostgresQL database
    cur.close()
    conn.close()

    if cust_acc_number != None:
        return cust_acc_number[0]
    else:
        return str('no ACC found')


# for testing only
@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_epl_get_all_info(request):
    hubRouter = ['SHO-HE-CAR-01', 'PX3-HE-CAR-AUTOMATE01']
    hubSwitch = ['SHO-HE-EDS-01', 'PX3-HE-EDS-AUTOMATE02']
    remoteRouter = ['PX8-CO-PCR-01', 'PX3-HE-CAR-AUTOMATE02']
    CustomerName = ['VZW_SocSecAdmin-SHO-PX8-311']
    vlan = [311]
    hubRouter_downlink_interface = ['ae0', 'ae1']
    hubRouter_route_distinguisher = ['10.201.3.101:311']
    hubRouter_vrf_target = ['target:1003:311']
    remoteRouter_downlink_interface = ['ae0', 'ae1']
    remoteRouter_route_distinguisher = ['10.201.104.100:311']
    remoteRouter_vrf_target = ['target:1003:311']
    hunSwitch_uplink_interface = ['ae0', 'ae1']
    hunSwitch_downlink_interface = ['5', '6', '7', '8']

    json_response = {'hubRouter': hubRouter, 'hubSwitch': hubSwitch, 'remoteRouter': remoteRouter, 'CustomerName': CustomerName, 'vlan': vlan,
                     'hubRouter_downlink_interface': hubRouter_downlink_interface, 'hubRouter_route_distinguisher': hubRouter_route_distinguisher,
                     'hubRouter_vrf_target': hubRouter_vrf_target, 'remoteRouter_downlink_interface': remoteRouter_downlink_interface,
                     'remoteRouter_route_distinguisher': remoteRouter_route_distinguisher, 'remoteRouter_vrf_target': remoteRouter_vrf_target,
                     'hunSwitch_uplink_interface': hunSwitch_uplink_interface, 'hunSwitch_downlink_interface': hunSwitch_downlink_interface}

    return JsonResponse(json_response)


@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_epl_get_remoteRouter_interfaces(request):
    router = request.data['remoteRouter']
    json_response = {"aggregation-ports": []}
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={router}/config/junos:configuration/interfaces'
    response = get_request(url).json()
    for port in response['junos:interfaces']['interface']:
        json_response["aggregation-ports"].append(port['name'])

    return JsonResponse(json_response)


def get_vlan_name(customerName, hubRouterName, remoteRouterName, vlan):
    customerName = customerName.replace(' ', '_')
    name = customerName[:19] if len(customerName) > 19 else customerName
    systemA = hubRouterName.split('-')[0]
    systemB = remoteRouterName.split('-')[0]
    vlanName = f'{name}-{systemA}-{systemB}-{vlan}'

    return vlanName


def calculate_route_distinguisher(routerName, vlan):
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={routerName}/config/junos:configuration/interfaces/interface=lo0/unit=0/family/inet/address'
    response = get_request(url).json()
    lo0_ip = response['junos:address'][0]['name'].split('/')[0]
    route_distinguisher = f'{lo0_ip}:{vlan}'

    return route_distinguisher


def calculate_vrf_target(routerName, vlan):
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={routerName}/config/junos:configuration/interfaces/interface=lo0/unit=0/family/inet/address'
    response = get_request(url).json()
    lo0_ip = response['junos:address'][0]['name'].split('/')[0]
    ospfCode = lo0_ip.split('.')[2].zfill(3)
    vrf_target = f'target:1{ospfCode}:{vlan}'

    return vrf_target


def sync_from(device):
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/sync-from'
    headers = {"Content-Type": "application/yang-data+json"}
    response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth(
        settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    print(response.json())


def get_request(url):
    headers = {"Content-Type": "application/yang-data+json"}
    url = url
    response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(
        settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    
    return response
    
