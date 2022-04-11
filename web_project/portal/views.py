from http.client import HTTPResponse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST, require_GET
from rest_framework.decorators import api_view
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import json, sys
import time
import pyodbc
import paramiko
import re
# from . import crq_ticket_class5


states = {
    'diaSingleHome:start': 'Start',
    'diaSingleHome:pre-checks': 'Running Pre-Checks',
    'diaSingleHome:dia-service': 'Configure service on devices',
    'diaSingleHome:update-external': 'Updating external DB',
    'diaSingleHome:post-checks': 'Running Post-Checks',
    'diaSingleHome:completed': 'Completed',
}


server = 'tcp:sql-product.corp.cableone.net'
# server1 = 'SQL-GOLDENGATE\GOLDENGATE'
server1 = '10.128.35.118'
database = 'network_automation'
database1 = 'SVCustom'
username = 'na_proxy'
password = '9tmoDRW4K24#%PEr'

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
    url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=access/device-name'
    headers = {"Content-Type": "application/yang-data+json"}
    response_access = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)

    url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=aggregation/device-name'
    headers = {"Content-Type": "application/yang-data+json"}
    response_aggregation = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    
    try:        
        response_json_acc = json.loads(response_access.text)
        response_json_agg = json.loads(response_aggregation.text)        
        params = {"access": response_json_acc['tailf-ncs:device-name'], "aggregation": response_json_agg['tailf-ncs:device-name']}                    
    except Exception as e:
        print('Error', e)
    return render(request, 'form.html', params)

@require_GET
@login_required(login_url='/login')
def table(request):
    # Query NSO for services
    url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome'
    headers = {"Content-Type": "application/yang-data+json"}
    response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
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
            # Change [0] to [1] to include init component
            for state in entry['plan']['component'][0]['state']:
                params_dict['plan'].append(state)
                if state['status'] == 'reached':
                    params_dict['last_state'] = states[state['name']]
            params['data'].append(params_dict)
    except Exception as e:
        print('Error', e, file=sys.stderr)


    
    return render(request, 'table.html', params )

@require_GET
@login_required(login_url='/login')
def details(request, customer_name, vlan_number):
    headers = {"Content-Type": "application/yang-data+json"}
    # API Create diaChecks start mark
    url = f'http://{settings.NSO_ADDRESS}/restconf/data/diaChecks:diaChecks'
    checksData = {
            "customer-name": customer_name,
            "vlan-number": vlan_number,
            "start": True
        }
    checks_response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"diaChecks:diaChecks":[checksData]}), verify=False)
    print('create-dia-checks entry', checks_response, file=sys.stderr)

    # API Query NSO for services
    url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}'    
    service_response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    try:
        response_json = json.loads(service_response.text.replace('-', '_'))
        params = {'data': response_json['diaSingleHome:diaSingleHome'][0], 'customer_name': customer_name, 'vlan_number': vlan_number, 'log_entry': False}        
              
        if params['data']['log']:
            params['log_entry'] = True

    except Exception as e:
        print('Error', e)

    
    return render(request, 'details.html', params)

@require_POST
@login_required(login_url='/login')
def submit(request):
    data = {}
    data['customer-name']= request.POST.get('customer_name')
    data['vlan-number'] = request.POST.get('vlan_number')
    data['aggregation'] = {}
    data['aggregation']['device-name'] = request.POST.get('aggregation_device-name')
    data['aggregation']['ipv4-address'] = request.POST.get('aggregation_ipv4-address')
    data['aggregation']['cidr-mask'] = netmask_to_cidr(request.POST.get('aggregation_cidr-mask'))
    data['aggregation']['access-interface'] = request.POST.get('aggregation_access-interface')
    data['access'] = {}
    data['access']['device-name'] = request.POST.get('access_device-name')
    data['access']['access-port'] = request.POST.get('access_access-port')
    data['access']['uplink-port'] = request.POST.get('access_uplink-port')

    print(data)
    # summary = "Florida Circuit for testing."
    # description = "this is a test"
    # object = crq_ticket_class5.crq_ticket()
    # object.cls_start(summary, description)

    # Path NSO for services
    try:
        headers = {"Content-Type": "application/yang-data+json"}

        # API to remove pre-existant diaChecks object
        customer_name = data['customer-name']
        vlan_number = data['vlan-number']
        clean_url = f'http://{settings.NSO_ADDRESS}/restconf/data/diaChecks:diaChecks={customer_name},{vlan_number}'
        requests.request('DELETE', clean_url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)

        # API to create service instance
        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome'
        response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"diaSingleHome:diaSingleHome":[data]}), verify=False)
        if response.status_code != 204:
            request.session['error_message'] = response.text
            return redirect(f'/error')    
        
    except Exception as e:
        return redirect(f'/error/{e}')

    return redirect(f"/details/{data['customer-name']}/{data['vlan-number']}")


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
def api_query_ip(request):
    data = request.data
    accountNumber = data['customer-name']
    vlan_number = data['vlan-number']
    ipAddr = {}

    c1_goldengateDB = pyodbc_db_connection(server1, database1, username, password)
    address = pyodbc_query(c1_goldengateDB, '''select * from SVCustom.dbo.CustomerAddresses where SingleviewAccount = \'''' + accountNumber + "'")
    for city in address:
        city = city.ServiceCity.lower().title()

    c1_productDB = pyodbc_db_connection(server, database, username, password)
    ipPool = pyodbc_query(c1_productDB, '''select * from network_automation.dbo.UbrNetworks_copy where sysname = \'''' + city + "' and username is NULL")
    for ip in ipPool:
        ip_address = ip.block.strip()
        subnet_mask = ip.mask.strip()
        # print(ip_address, subnet_mask)
        # ipAddr.append(ip_address)
        ipAddr[ip_address] = subnet_mask
    # customer_name and vlan_number    

    # Replace Sleep with your code
    #time.sleep(3)
    
    # response = {"ipv4-address": "10.239.45.1"}
    return JsonResponse(ipAddr)

@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_access_interfaces(request):
    data = request.data
    device = data['device']
    vlan666_ports = []
    json_response = {"access-ports": [], "uplink-ports": []}
    if device != '':
        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cienacli-acos:vlan/add/vlan=666'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False).json()
        for port in response["tailf-ned-cienacli-acos:vlan"][0]['port']:
           vlan666_ports.append(port['id'])


        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False).json()


        for port_dict in response["tailf-ned-cienacli-acos:set"]['port']:            
            if port_is_access(port_dict, vlan666_ports) == True:
                json_response["access-ports"].append(port_dict["name"])
        for port_dict in response["tailf-ned-cienacli-acos:set"]['port']:                      
            if port_is_uplink(port_dict) == True:
                json_response["uplink-ports"].append(port_dict["name"])
    else:
        response = {}
        
    return JsonResponse(json_response)

@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_aggregation_interfaces(request):
    data = request.data
    device = data['device']
    json_response = {"aggregation-ports": []}
    if device != '':
        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/junos:configuration/junos:interfaces'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False).json()        
        for port_dict in response["junos:interfaces"]['interface']:
            if port_is_aggregatrion(port_dict) == True:
                json_response["aggregation-ports"].append(port_dict["name"])
    else:
        response = {}
    return JsonResponse(json_response)


@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_all_interfaces(request):
    data = request.data
    switch = data['eds_switch']
    router = data['acx_router']
    vlan666_ports = []
    json_response = {"access-ports": [], "uplink-ports": [], "aggregation-ports": []}
    if switch != '' and router != '':
        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/remote/set/ip'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False)
        eds_ip = response.json()['tailf-ned-cienacli-acos:ip'].split('/')[0]


        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/set/gateway'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False)
        car_ip = response.json()['tailf-ned-cienacli-acos:gateway']


        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/add/vlan=666'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False).json()
        for port in response["tailf-ned-cienacli-acos:vlan"][0]['port']:
           vlan666_ports.append(port['id'])


        url = f'http://{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False).json()


        for port_dict in response["tailf-ned-cienacli-acos:set"]['port']:            
            if port_is_access(port_dict, vlan666_ports) == True:
                json_response["access-ports"].append(port_dict["name"])

        print('111111111111111')
        uplink_port = calculate_access_uplink(eds_ip, car_ip)
        json_response["uplink-ports"].append(uplink_port)
        downlink_port = calculate_agg_downlink(eds_ip, car_ip)
        json_response["aggregation-ports"].append(downlink_port)

    else:
        response = {}
        
    return JsonResponse(json_response)



# Validate Ports

def port_is_access(port_dict, vlan666_dict):
    if port_dict ["name"] in vlan666_dict:
        return True
    else:
        return False

def port_is_uplink(port_dict):
    return True

def port_is_aggregatrion(port_dict):
    return True

def pyodbc_db_connection(server, database, username, password):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
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
    startTime = time.time()
    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("22222")
    child.connect(eds_ip, 22, 'autoeng', '}-75S^:j.mf@YJQm')
    print("33333")
    stdin, stdout, stderr = child.exec_command(f'arp show intf remote')
    print("4444")
    string = stdout.read().decode('ascii').strip("\n")    
    mac = re.search(f"\|\s+{acx_ip}\s+\|\s+(\w+:\w+:\w+:\w+:\w+:\w+)", string).group(1)

    stdin, stdout, stderr = child.exec_command(f'flow mac-addr show mac {mac}')
    string = stdout.read().decode('ascii').strip("\n")    
    uplinlport=re.search(f"\|\s+{mac}\s\|\s+(.+?)\s+\|", string, re.IGNORECASE).group(1)
    execute_Time = time.time() - startTime
    print("Request completed in {0:.0f}s".format(execute_Time))
    return uplinlport


def calculate_agg_downlink(eds_ip, acx_ip):
    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    child.connect(acx_ip, 22, 'autoeng', '}-75S^:j.mf@YJQm')
    stdin, stdout, stderr = child.exec_command(f'show arp no-resolve | match {eds_ip}')
    string = stdout.read().decode('ascii').strip("\n")
    # print(string)  
    mac = re.search(f"(\w+:\w+:\w+:\w+:\w+:\w+)\s+{eds_ip}", string).group(1)
    print(mac)

    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    child.connect('10.204.8.1', 22, 'autoeng', '}-75S^:j.mf@YJQm')
    stdin, stdout, stderr = child.exec_command(f'show arp | except em')
    string = stdout.read().decode('ascii').strip("\n")
    outIntf = re.search(f"{mac}.+\s+\[*(\w+-\d+/\d+/\d+)", string)
    outIntfae = re.search(f"{mac}.+\s+\[*(ae\d+)", string)

    if outIntf:
        downlink = outIntf.group(1)
        print(downlink)
    elif outIntfae:
        downlink = outIntfae.group(1)
        print(downlink)
    return downlink