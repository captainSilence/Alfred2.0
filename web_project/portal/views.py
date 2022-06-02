from http.client import HTTPResponse
from traceback import print_tb
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
import datetime
import pyodbc
import paramiko
import re
import psycopg2
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

# connect to PostgreSQL
t_host = "10.128.64.11" # this will be either "localhost", a domain name, or an IP address.
t_port = "5432" # default port for postgres server
t_dbname = "postgres"
t_user = "myprojectuser"
t_pw = "password"
pre_post_checks_key = r'!'

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
    headers = {"Content-Type": "application/yang-data+json"}
    response_access = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)

    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device-group=aggregation/device-name'
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
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome'
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
            params_dict['ticket'] = find_ticket_num(entry['customer-name'], entry['vlan-number'])
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
def device_config(request, customer_name, vlan_number):
    # api for rollback plan
    # headers = {"Content-Type": "application/yang-data+json"}
    # url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}?dryrun=native'
    # response = requests.request('DELETE', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False)
    # config = response.json()['dryrun-result']['native']['device']
    # params = {'config': config, 'customer_name': customer_name, 'vlan_number': vlan_number}

    headers = {"Content-Type": "application/yang-data+json"}
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}/get-modifications'
    response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    data = response.json()["diaSingleHome:output"]["cli"]["local-node"]["data"]
    router_config = removeSpace(data.split('device')[2].replace("{", "").replace("}", ""))
    switch_config = removeSpace(data.split('device')[3].split('diaChecks')[0].replace("{", "").replace("}", ""))
    config = {"aggregation": {"ACX Router": router_config}, "access": {"EDS Switch": switch_config}}
    params = {'config': config, 'customer_name': customer_name, 'vlan_number': vlan_number}   
    # print(router_config)
    # removeSpace
    # print(switch_config)

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
    checks_response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"diaChecks:diaChecks":[checksData]}), verify=False)
    print('create-dia-checks entry', checks_response, file=sys.stderr)

    # API to check the pre-check condition
    # url = f'http://10.128.64.13:8080/restconf/data/diaChecks:diaChecks={customer_name},{vlan_number}/pre-checks'
    # response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    # if response.status_code != 200:
    #     # re-deploy the service
    #     url = f'http://10.128.64.13:8080/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}/re-deploy'
    #     response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
    #     print(response)
    #     print(response.text)

    # API Query NSO for services
    url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome={customer_name},{vlan_number}'    
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
    data['vlan-number'] = int(request.POST.get('vlan_number'))
    data['aggregation'] = {}
    data['aggregation']['device-name'] = request.POST.get('aggregation_device-name')
    data['aggregation']['ipv4-address'] = request.POST.get('aggregation_ipv4-address')
    data['aggregation']['cidr-mask'] = netmask_to_cidr(request.POST.get('aggregation_cidr-mask'))
    data['aggregation']['access-interface'] = request.POST.get('aggregation_access-interface')
    data['access'] = {}
    data['access']['device-name'] = request.POST.get('access_device-name')
    data['access']['access-port'] = request.POST.get('access_access-port')
    data['access']['uplink-port'] = request.POST.get('access_uplink-port')
    user = request.user.username
    time = datetime.datetime.now()
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
        eds_switch = data['access']['device-name']
        car_router = data['aggregation']['device-name']
        clean_url = f'{settings.NSO_ADDRESS}/restconf/data/diaChecks:diaChecks={customer_name},{vlan_number}'
        requests.request('DELETE', clean_url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)


        # API to create service instance
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:services/diaSingleHome:diaSingleHome'
        response = requests.request('PATCH', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), data=json.dumps({"diaSingleHome:diaSingleHome":[data]}), verify=False)
        if response.status_code != 204:
            request.session['error_message'] = response.text
            return redirect(f'/error')    
        
    except Exception as e:
        return redirect(f'/error/{e}')

    # log the user activity into the DB
    conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute("INSERT INTO user_session (customer_acc_number, vlan, user_name, time_service_created) " +
                "VALUES(%s, %s, %s, %s)",
                (customer_name, vlan_number, user, time))
    # commit the changes to the database
    conn.commit()
    # close the communication with the PostgresQL database
    cur.close()
    conn.close()


    return redirect(f"/details/{customer_name}/{vlan_number}")


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
    ipPool = pyodbc_query(c1_productDB, '''select * from network_automation.dbo.UbrNetworks_copy where sysname = \'''' + city + '''' and username = \'''' + accountNumber + "' and ssu is null and macadd is null and wirelessActive is null")
    if ipPool == []:
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
        headers = {"Content-Type": "application/yang-data+json"}
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False).json()
        for port in response["tailf-ned-cienacli-acos:vlan"][0]['port']:
           vlan666_ports.append(port['id'])


        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
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


# not in use, see get_all_interfaces function
@require_POST
@login_required(login_url='/login')
@api_view(['POST'])
def api_get_aggregation_interfaces(request):
    data = request.data
    device = data['device']
    json_response = {"aggregation-ports": []}
    if device != '':
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={device}/config/junos:configuration/junos:interfaces'
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
    ports_removed_from_vlan666 = []
    json_response = {"access-ports": [], "uplink-ports": [], "aggregation-ports": []}
    headers = {"Content-Type": "application/yang-data+json"}



    if switch != '' and router != '':
        # API to sync the devices
        url = f'http://10.128.64.13:8080/restconf/data/tailf-ncs:devices/device={eds_switch}/sync-from'
        response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False)
        print(response.json())

        url = f'http://10.128.64.13:8080/restconf/data/tailf-ncs:devices/device={car_router}/sync-from'
        response = requests.request('POST', url, headers=headers, auth=HTTPBasicAuth("autoeng", "xt,xnDHk9t:qdQxm"), verify=False)
        print(response.json())

        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/remote/set/ip'
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
        eds_ip = response.json()['tailf-ned-cienacli-acos:ip'].split('/')[0]


        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:interface/set/gateway'
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
        car_ip = response.json()['tailf-ned-cienacli-acos:gateway']


        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/add/vlan=666'
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
        if response.status_code == 200:
            for port in response.json()["tailf-ned-cienacli-acos:vlan"][0]['port']:
               vlan666_ports.append(port['id'])

        
        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:vlan/remove/vlan=666'
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False)
        if response.status_code == 200:
            for port in response.json()["tailf-ned-cienacli-acos:vlan"][0]['port']:
               ports_removed_from_vlan666.append(port['id'])


        url = f'{settings.NSO_ADDRESS}/restconf/data/tailf-ncs:devices/device={switch}/config/tailf-ned-cienacli-acos:port/tailf-ned-cienacli-acos:set'
        response = requests.request('GET', url, headers=headers, auth=HTTPBasicAuth(settings.NSO_USERNAME, settings.NSO_PASSWORD), verify=False).json()


        for port_dict in response["tailf-ned-cienacli-acos:set"]['port']:            
            if port_is_access(port_dict, vlan666_ports) == True and remove_port_from_vlan666(port_dict, ports_removed_from_vlan666) == True:
                json_response["access-ports"].append(port_dict["name"])


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


def remove_port_from_vlan666(port_dict, ports_removed_from_vlan666):
    if port_dict ["name"] not in ports_removed_from_vlan666:
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
    # print(eds_ip, acx_ip)
    startTime = time.time()
    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    child.connect(eds_ip, 22, settings.AD_USER, settings.AD_PASSWORD)
    stdin, stdout, stderr = child.exec_command(f'arp show intf remote')
    string = stdout.read().decode('ascii').strip("\n")    
    mac = re.search(f"\|\s+{acx_ip}\s+\|\s+(\w+:\w+:\w+:\w+:\w+:\w+)", string).group(1)

    stdin, stdout, stderr = child.exec_command(f'flow mac-addr show mac {mac}')
    string = stdout.read().decode('ascii').strip("\n")    
    uplinkport=re.search(f"\|\s+{mac}\s\|\s+(.+?)\s+\|", string, re.IGNORECASE).group(1)
    execute_Time = time.time() - startTime
    print("Request completed in {0:.0f}s".format(execute_Time))
    return uplinkport


def calculate_agg_downlink(eds_ip, acx_ip):
    child = paramiko.SSHClient()
    child.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    child.connect(acx_ip, 22, settings.AD_USER, settings.AD_PASSWORD)
    stdin, stdout, stderr = child.exec_command(f'show arp no-resolve | match {eds_ip}')
    string = stdout.read().decode('ascii').strip("\n")
    # print(string)  
    mac = re.search(f"(\w+:\w+:\w+:\w+:\w+:\w+)\s+{eds_ip}", string).group(1)
    # print(mac)

    stdin, stdout, stderr = child.exec_command(f'show arp | except em')
    string = stdout.read().decode('ascii').strip("\n")
    outIntf = re.search(f"{mac}.+\s+\[*(\w+-\d+[\/]\d+[\/]\d+)", string)
    outIntfae = re.search(f"{mac}.+\s+\[*(ae\d+)", string)
    # print(outIntf)
    # print(outIntfae)

    if outIntf:
        downlink = outIntf.group(1)
        # print(downlink)
    elif outIntfae:
        downlink = outIntfae.group(1)
        # print(downlink)
    return downlink


def removeSpace(string_with_empty_lines):
    lines = string_with_empty_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]

    string_without_empty_lines = ""
    for line in non_empty_lines:
          string_without_empty_lines += line + "\n"

    return string_without_empty_lines


def find_ticket_num(customer_acc, vlan):
    conn = psycopg2.connect(dbname="postgres", user="myprojectuser", password="password", host="10.128.64.11")
    cur = conn.cursor()
    cur.execute(f"SELECT ticket_number FROM dia where customer_acc_number = '{customer_acc}' and vlan = {vlan};")
    ticket_num = cur.fetchone()
    cur.close()
    conn.close()

    if ticket_num == None:
        return "No CRQ Found"
    else:
        return ticket_num[0]

