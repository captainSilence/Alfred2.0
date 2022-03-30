

from genie.testbed import load
import yaml
import os


class GenieConnection():
    def __init__(self, uuid, username, password, custAddress, peName, peAddress, execType):
        self.uuid = uuid
        self.username = username
        self.password = password
        self.custAddress = custAddress
        self.peAddress = peAddress
        self.execType = execType
        self.peName = peName
        return
        
    def connect(self):
        folder = 'outputs'
        debug = True
        learn_hostname = True

        data = {
            "uuid": f"{self.uuid}",
            "folder": f"{folder}",
            "commands":{
                "iosxr": [
                    f"ping {self.custAddress}"
                    ]
                },
            "devices":{
                f"{self.peName}":{
                    "type": "router",
                    "os": "iosxr",
                    "credentials":{
                        "default":{
                            "username": f"{self.username}",
                            "password": f"{self.password}"
                        }
                    },
                    "connections":{
                        "ssh":{
                            "protocol": "ssh",
                            "ip": f"{self.peAddress}",
                            "port": 22,
                            "login_creds": "[default]",
                            "init_exec_commands": ['terminal length 0', 'terminal width 511'],
                            "init_config_commands": []
                        }
                    }
                },
            }
        }
        testbed = {"devices": data["devices"]}    
        testbed = load(yaml.dump(testbed))
        testbed.connect(log_stdout=debug, learn_hostname=learn_hostname)

        for device in testbed.devices:
            os_type = testbed.devices[device].os
            command_list = data["commands"][os_type]  
            log_folder = os.path.join(data['folder'], self.uuid, self.execType, self.peName)
            
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)      
            if testbed.devices[device].connected == True:                        
                for command in command_list:            
                    output = testbed.devices[device].execute(command, timeout=600)
                    if debug is True:
                        with open(os.path.join(log_folder, command + '.txt'), 'w') as fp:
                            fp.write(output)
                testbed.devices[device].disconnect()
                testbed.devices[device].destroy()