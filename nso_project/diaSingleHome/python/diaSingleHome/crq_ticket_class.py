import requests
import os
import json
import time
import urllib.parse
from datetime import datetime
#from flask import (jsonify)
#from .crqdata import crqdata

class crq_ticket:


    def __init__(self):

        self.base_url = 'http://remedyar.corp.cableone.net:8008/api'
        self.headers = {'Content-Type': 'application/json'}
        self.username = 'SvcAcctChanges'
        self.password = '%f3Qrphr@jkB'
        #self.headers = None
        self.ticket_no = ""


    def addworklog(self,ticket, type, description, submitter):
        worklog_url = self.base_url + '/arsys/v1/entry/CHG:WorkLog'
        worklog_data = {
            "values": {
            "Submitter": submitter,
            "Infrastructure Change ID": ticket,
            "Detailed Description": description,
            "Work Log Type": type,
            "Status": 'Enabled' 
                }
            }
        response = requests.post(worklog_url, data=json.dumps(worklog_data), headers=self.headers)
        if response.status_code == 201:
            print("addworklog passed")
            return True
        else:
            print(response)
            raise Exception('Worklog creation failed.')

    def login(self):
        credentials = {'username': self.username, 'password': self.password}

        login_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        login_url = self.base_url + '/jwt/login'
        response = requests.post(login_url, data=credentials, headers=login_headers)
        self.headers['Authorization'] = b'AR-JWT ' + response.content
        #print("Response form logging in:" + str(response.content))


    def create_crq(self, summary, description):


        first_name = "Christopher"
        last_name = "Aycock"
        summary_old = "EF-[Anniston HE/Office, AL]-QnQ Circuit for testing."
        #description = "Expected Duration: .25 Hour(s) " + \
        #              "\nReason for Maintenance: Build a QnQ circuit using SVLAN 279 in ['Anniston HE/Office, AL'] for testing. " + \
        #              "\nAnticipated Customer/Associate Impact: No impact expected."
        postdata = {
            "values": {      
                "z1D_Action"                     : "CREATE",
                "Location Company"               : "Cable One",
                "Requestor ID"                   : "SvcAcctChanges",
                "Submitter"                      : "SvcAcctChanges",
                "Description"                    : summary,
                "Detailed Description"           : description,

                "Company3":                       "Cable One",
                "Support Organization"           : "Product Engineering",
                "Support Group Name"             : "Network Automation",
                "Support Organization2"          : "Network Automation",
                "Support Group Name2"            : "Network Automation",
                "CAB Manager ( Change Co-ord )"  : "Clifton Dawes",
                "CAB_Manager_Login"              : "Dawesc",

                "ASCPY"                          : "Cable One",
                "ASORG"                          : "Product Engineering",
                "ASGRP"                          : "Network Automation",
                "ASCHG"                          : "Service Account Changes",
                "ASLOGID"                        : "SvcAcctChanges",

                "Lead Time"                      : "0",
                "Urgency"                        : "3-Medium",
                "Risk Level"                     : "Risk Level 3",
                "Change Type"                    : "Change",
                "Change Timing"                  : "Standard",
                "Timing_Reason"                  : "",
                "Categorization Tier 1"          : "Network",
                "Priority"                       : "Medium",
 
         	"Status"                         : "Draft",
                "Impact"                         : "4-Minor/Localized",
                "Scheduled Start Date"           : "2022-01-25T21:26:40.000+0000",
                "Scheduled End Date"             : "2022-01-25T21:45:40.000+0000",
#            "Earliest Start Date"            : "2022-01-25T21:45:40.000+0000",
            }
        }

        #print(json.dumps(postdata))
        #
        # These calls are coming from naremedy.py
        worklog_url = self.base_url + '/arsys/v1/entry/CHG:ChangeInterface_Create'
        response = requests.post(worklog_url, data=json.dumps(postdata), headers=self.headers)

        print("\n\nResponse:" + str(response.content))
        print("\n\nResponse_statuscode:" + str(response.status_code))

        busjust = "Building QnQ circuit at the request of Service Account Changes."
        submitter = self.username
        backoutp = "---Backout Plan--- Device: BO2-HE-EDS-01 Rollback Commands:"
        installp = "---Install Plan---Device: BO2-HE-EDS-01 Configuration Commands:"

        print("Username:" + self.username)
        print("Response_code:" + str(response.status_code))

        if response.status_code == 201:
            crq_url = response.headers._store['location'][1]
            crq_info = requests.get(crq_url, headers=self.headers)
            self.ticketno = json.loads(crq_info.content)['values']['Infrastructure Change Id']
            print("ticket number:" + str(self.ticketno))
            self.addworklog(self.ticketno, 'Business Justification', busjust, submitter)
            self.addworklog(self.ticketno, 'Backout Plan', backoutp, submitter)
            self.addworklog(self.ticketno, 'Install Plan', installp, submitter)
            print(response.content)
            return self.ticketno



    def addimpactedarea(self, ticket, site, submitter):
        worklog_url = self.base_url + '/arsys/v1/entry/SIT:Site Alias Company LookUp?q=(\'Site\' = "'+ site + '")'
        response = requests.get(worklog_url, headers=self.headers)
        addinfo = json.loads(response.content)

        worklog_url = self.base_url + '/arsys/v1/entry/CHG:Impacted%20Areas'
        worklog_data = {
            "values": {
                "Submitter": submitter,
                "Infrastructure Change ID": self.ticket,
                "Site": "American Falls HE, ID",
                "Site Group" : "Pocatello",
                "Region" : "West",
                "Company" : "Cable One",
                "Short Description" : '.',
                "Status": 'Enabled'
                }
            }
        response = requests.post(worklog_url, data=json.dumps(worklog_data), headers=self.headers)
        if response.status_code == 201:
            print("updated impacted area")
            return True
        else:
            print(response.content)
            raise Exception('Impacted Areas creation failed.')


    def get_crq_info(self,ticket):

        worklog_url = self.base_url + '/arsys/v1/entry/CHG:Infrastructure Change?q=(\'Infrastructure Change ID\' = "' + ticket + '")'
        print(worklog_url)
        response = requests.get(worklog_url, headers=self.headers)
        if response.status_code == 200:
            crq_info = json.loads(response.content)['entries'][0]
            crq_status = crq_info['values']['Change Request Status']
            print("crq_status:" + str(crq_status))
            print("+++++++++++++++++++++")
            #print(response.content[0:400])
            print(response.content)
        else:
            print('CRQ not found.')


    def chg_crq_info(self,ticket):

        postdata = {
                "values": {      
    #            "z1D_Action"                     : "MODIFY",
                "Last Name"                      : "MODIFY",
         	"Infrastructure Change ID"       : "CRQ000000066022"
                #	    "Status"                         : "Cancelled",
            }
        }
        worklog_url = self.base_url + '/arsys/v1/entry/CHG:Infrastructure Change?q=(\'Infrastructure Change ID\' = "' + ticket + '")'
        response = requests.post(worklog_url, data=json.dumps(postdata), headers=self.headers)
        print(response.content)

    def changeCRQstatus(self, ticket, nextstatus):
        change_url = self.base_url + '/arsys/v1/entry/CHG:ChangeInterface'
        query_url = str(change_url) + '?q=(\'Infrastructure Change ID\' = "'+ str(ticket) + '")'
        response = requests.get(query_url, headers=self.headers)
        if response.status_code == 200:
            entries = json.loads(response.content)['entries']
            if entries == []:
                raise Exception('CRQ not found.')
            crq_entry = entries[0]
            crq_link = crq_entry['_links']['self'][0]['href']
            crq_url = urllib.parse.unquote(crq_link)
            crq_info = {
                "values": {
                    "Change Request Status" : nextstatus
                }
            }
            response = requests.put(crq_url, data=json.dumps(crq_info), headers=self.headers)
            if response.status_code == 204:
                return True
            else:
                raise Exception(self.extractErrMsg(response.content))
        else:
            raise Exception(self.extractErrMsg(response.content))

    def completeCRQstatus(self, ticket, nextstatus):
        self.addworklog(ticket, 'Install Results - Details', 'Some result details would be here', self.username)
        change_url = self.base_url + '/arsys/v1/entry/CHG:ChangeInterface'
        query_url = change_url + '?q=(\'Infrastructure Change ID\' = "'+ ticket + '")'
        response = requests.get(query_url, headers=self.headers)
        if response.status_code == 200:
            entries = json.loads(response.content)['entries']
            if entries == []:
                raise Exception('CRQ not found.')
            crq_entry = entries[0]
            crq_link = crq_entry['_links']['self'][0]['href']
            crq_url = urllib.parse.unquote(crq_link)
            crq_info = {
                "values": {
                    "Change Request Status" : nextstatus,
                    "Status Reason" : 'Final Review Complete',
                    "Actual End Date" : datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                }
            }
            response = requests.put(crq_url, data=json.dumps(crq_info), headers=self.headers)
            if response.status_code == 204:
                return True
            else:
                raise Exception(self.extractErrMsg(response.content))
        else:
            raise Exception(self.extractErrMsg(response.content))


    def extractErrMsg(self, content):
        reason = json.loads(content)[0]
        errMsg = reason['messageType'] + ' ' + str(reason['messageNumber']) + ' - '
        msg = False
        if reason['messageText'] != None:
            errMsg += reason['messageText']
            msg = True
        if reason['messageAppendedText'] != None:
            if msg == True:
                errMsg += ". "
            errMsg += reason['messageAppendedText']
        return errMsg


    def cls_start(self, summary, description):
        self.login()
        self.ticket_no = self.create_crq(summary, description)
        self.changeCRQstatus(self.ticket_no, "Request For Authorization")
        print("Done with: Request For Authorization")
        time.sleep(12)
        self.changeCRQstatus(self.ticket_no, "Scheduled For Review")
        print("Done with: Scheduled FOR Review")
        time.sleep(10)
        self.changeCRQstatus(self.ticket_no, "Scheduled")
        print("Done with: Scheduled")
        time.sleep(10)
        self.changeCRQstatus(self.ticket_no, "Implementation In Progress")
        print("Done with: Implementation In Progress")

        time.sleep(10)
        self.completeCRQstatus(self.ticket_no, "Completed")
        print("Done with: Completed")


