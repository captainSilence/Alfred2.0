# -*- mode: python; python-indent: 4 -*-
from multiprocessing import connection
import ncs
import _ncs
import socket
from ncs.application import Service
from scripts.genie_conection import GenieConnection
import uuid, os, re, json

pre_post_checks_key = r'!'

class Start(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.info("Start:", state)


class PreChecks(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.info("RunPreChecks:", state)
        # Call external pre checks script needs to be async            
        executionId = str(uuid.uuid4())        
        peName = service.aggregation.device_name
        peAddress = root.devices.device[peName].address
        authgroup = root.devices.device[peName].authgroup
        username = root.devices.authgroups.group[authgroup].default_map.remote_name
        encrypted_password = root.devices.authgroups.group[authgroup].default_map.remote_password
        m = ncs.maapi.Maapi()
        m.install_crypto_keys()
        password = str(_ncs.decrypt(encrypted_password))
        custAddress = service.aggregation.ipv4_address
        execType = 'pre-checks'
        try:
            connection = GenieConnection(executionId, username, password, custAddress, peName, peAddress, execType)
            connection.connect()
        except Exception as e:
            self.log.error('Error:', e)
            raise Exception(e)
 
        root.diaChecks__diaChecks[service.customer_name, service.vlan_number].uuid = executionId
        log_folder = os.path.join('outputs', executionId, execType, peName)
        if os.path.exists(log_folder):
            list_files = os.listdir(log_folder)
            if len(list_files) > 0:
                with open(os.path.join(log_folder, list_files[0]), 'r') as fp:
                    raw_output = fp.read()
                    if re.search(pre_post_checks_key, raw_output):
                        # If at least one ping responded mark response as fail for pre-checks
                        error_message = 'Pre-Checks Failed, ip address is not free'                                        
                        self.log.error("Error:", error_message)
                        raise Exception(error_message)                         
                      
                    else:
                        root.diaChecks__diaChecks[service.customer_name, service.vlan_number].pre_checks = True
            else:                
                error_message = 'Pre Checks did not collected device output'
                self.log.error("Error:", error_message)
                raise Exception(error_message)
        else:            
            error_message = 'Pre Checks did not collected device output'
            self.log.error("Error:", error_message)
            raise Exception(error_message)

        # Comment next row for production
        # root.diaChecks__diaChecks[service.customer_name, service.vlan_number].pre_checks = True
        # Logic to analyze output results

class DIAService(ncs.application.NanoService):        
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.info("DIAService:", state)
        if service.access.exists():
            self.log.info('DIAService: Creating access config')
            vars = ncs.template.Variables()
            vars.add('CUSTOMER_NAME', service.customer_name)
            vars.add('VLAN_NUMBER', service.vlan_number)
            vars.add('DEVICE_NAME', service.access.device_name)
            vars.add('ACCESS_PORT', service.access.access_port)
            vars.add('UPLINK_PORT', service.access.uplink_port)
            template = ncs.template.Template(service.access)
            template.apply('diaAccess-template', vars)

        if service.aggregation.exists():
            self.log.info('DIAService: Creating aggregation config')
            vars = ncs.template.Variables()
            vars.add('VLAN_NUMBER', service.vlan_number)
            vars.add('CUSTOMER_NAME', service.customer_name)
            vars.add('DEVICE_NAME', service.aggregation.device_name)
            vars.add('ACCESS_INTERFACE', service.aggregation.access_interface)
            vars.add('IPV4_ADDRESS', service.aggregation.ipv4_address)
            vars.add('CIDR_MASK', service.aggregation.cidr_mask)
            template = ncs.template.Template(service)
            template.apply('diaAggregationSingle-template', vars)

class UpdateExternal(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.info("UpdateExternal:", state)
        self.log.info('IPv4 Address', service.aggregation.ipv4_address)

class PostChecks(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):        
        self.log.info("RunPostChecks:", state)
        executionId = root.diaChecks__diaChecks[service.customer_name, service.vlan_number].uuid
        peName = service.aggregation.device_name
        peAddress = root.devices.device[peName].address
        authgroup = root.devices.device[peName].authgroup
        username = root.devices.authgroups.group[authgroup].default_map.remote_name
        encrypted_password = root.devices.authgroups.group[authgroup].default_map.remote_password
        m = ncs.maapi.Maapi()
        m.install_crypto_keys()
        password = str(_ncs.decrypt(encrypted_password))
        custAddress = service.aggregation.ipv4_address       
        execType = 'post-checks'        
        try:
            connection = GenieConnection(executionId, username, password, custAddress, peName, peAddress, execType)
            connection.connect()
        except Exception as e:
            self.log.error('Error:', e)
            raise Exception(e)

        log_folder = os.path.join('outputs', executionId, execType, peName)
        if os.path.exists(log_folder):
            list_files = os.listdir(log_folder)
            if len(list_files) > 0:
                with open(os.path.join(log_folder, list_files[0]), 'r') as fp:
                    raw_output = fp.read()
                    if re.search(pre_post_checks_key, raw_output):
                        # If at least one ping responded mark response as success
                        root.diaChecks__diaChecks[service.customer_name, service.vlan_number].post_checks = True
                    else:                    
                        error_message = 'Post-Checks Failed, ip address is not reachable'
                        self.log.warning("Warning:", error_message)
                        raise Exception(error_message)
            else:
                error_message = 'Post Checks did not collected device output'
                self.log.error("Error:", error_message)
                raise Exception(error_message)
        else:
            error_message = 'Post Checks did not collected device output'
            self.log.error("Error:", error_message)
            raise Exception(error_message)

        # Remove next row for production environment:
        # root.diaChecks__diaChecks[service.customer_name, service.vlan_number].post_checks = True

class Completed(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.info("Completed:", state)

class DIASingleHome(ncs.application.Application):
    def setup(self):
        self.log.info('DIASingleHome RUNNING')
        self.register_nano_service('diaSingleHome-servicepoint', 'diaSingleHome:dia-single-home', 'diaSingleHome:start', Start)
        self.register_nano_service('diaSingleHome-servicepoint', 'diaSingleHome:dia-single-home', 'diaSingleHome:pre-checks', PreChecks)
        self.register_nano_service('diaSingleHome-servicepoint', 'diaSingleHome:dia-single-home', 'diaSingleHome:dia-service', DIAService)
        self.register_nano_service('diaSingleHome-servicepoint', 'diaSingleHome:dia-single-home', 'diaSingleHome:update-external', UpdateExternal)
        self.register_nano_service('diaSingleHome-servicepoint', 'diaSingleHome:dia-single-home', 'diaSingleHome:post-checks', PostChecks)
        self.register_nano_service('diaSingleHome-servicepoint', 'diaSingleHome:dia-single-home', 'diaSingleHome:completed', Completed)
                
    def teardown(self):
        self.log.info('DIASingleHome FINISHED')