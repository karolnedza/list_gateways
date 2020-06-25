#! /usr/bin/python3

import boto3
import requests, json, urllib3, getpass, sys
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

all_gateways = []
init_table = {}
older_amis = {
    'hvm-cloudx-aws-011519',
    'hvm-cloudx-aws-041519',
    'hvm-cloudx-aws-071519',
    'hvm-cloudx-aws-093019'}

### Create a directory with empty values

def start_table(gw):
    for i in range(1,gw):
        init_table['Gateway ' + str(i)] = {}
    return init_table

def create_table():
    for i in range(1,len(all_gateways)):
        init_table['Gateway ' + str(i)]['Number'] = ""
        init_table['Gateway ' + str(i)]['Gateway Name'] = ""
        init_table['Gateway ' + str(i)]['Status'] = ""
        init_table['Gateway ' + str(i)]['Account'] = ""
        init_table['Gateway ' + str(i)]['HA-GW'] = ""
        init_table['Gateway ' + str(i)]["Instance Size"] = ""
        init_table['Gateway ' + str(i)]["AMI Id"] = ""
        init_table['Gateway ' + str(i)]["GW Zone"] = ""
        init_table['Gateway ' + str(i)]["t3.medium supported"] = ""
        init_table['Gateway ' + str(i)]["Resize"] = ""
        init_table['Gateway ' + str(i)]["Replace"] = ""
    return init_table

# login and store CID

def login(controller, username, password):
    url = "https://" + controller + "/v1/api"
    payload = {'action': 'login',   'username': username, 'password': password}
    response = requests.request("POST", url, headers={}, data = payload, files = [], verify = False)
    cid = response.json()["CID"]
    return cid


# Create list of all Gateways

def get_all_gateways(controller, cid):
    url = "https://" + controller + "/v1/api?action=list_vpcs_summary&CID=" + cid + "&acx_gw_only=no"
    response = requests.request("GET", url, headers={}, data = {}, verify = False)
    gw = response.json()
    for i in gw['results']:
        all_gateways.append(i['gw_name'])

# Get  details about GWs

def populate_table(controller, cid, aws_access_key, aws_secret_key):
    for idx, gateway in enumerate(all_gateways, 1):
        url = "https://" + controller + "/v1/api?action=get_gateway_info&&CID=" + cid + "&gateway_name=" + gateway
        response = requests.request("GET", url, headers={}, data = {}, verify = False)
        gateway_desc = response.json()
        print("Creating report for: ", gateway )
        init_table['Gateway ' + str(idx)]['Number'] = idx
        init_table['Gateway ' + str(idx)]['Gateway Name'] = gateway
        init_table['Gateway ' + str(idx)]['Status'] = gateway_desc['results']['vpc_state']
        init_table['Gateway ' + str(idx)]['Account'] = gateway_desc['results']['account_name']
        init_table['Gateway ' + str(idx)]['HA-GW'] = gateway_desc['results']['is_hagw']
        init_table['Gateway ' + str(idx)]["Instance Size"] = gateway_desc['results']['vpc_size']
        init_table['Gateway ' + str(idx)]["AMI Id"] = gateway_desc['results']['gw_image_name']
        init_table['Gateway ' + str(idx)]["GW Zone"] = gateway_desc['results']['gw_zone']

## Adding an extra check. Not all AWS aviability zones offer t3.medium

        session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name="us-east-1")
        ec2_client = session.client('ec2')
        response = ec2_client.describe_instance_type_offerings(LocationType='availability-zone',
        Filters=
                [
                {'Name': 'instance-type','Values': ['t3.medium']},
                {'Name': 'location',      'Values': [gateway_desc['results']['gw_zone']]}
            ]
        )
        if response['InstanceTypeOfferings'] != []:
            init_table['Gateway ' + str(idx)]["t3.medium supported"] =  "Yes"
        else:
            init_table['Gateway ' + str(idx)]["t3.medium supported"] = '-'

        if (("micro" in gateway_desc['results']['vpc_size'] or "small" in gateway_desc['results']['vpc_size']) and (response['InstanceTypeOfferings'] != [])):

            init_table['Gateway ' + str(idx)]["Resize"] = "Yes"
        else:
            init_table['Gateway ' + str(idx)]["Resize"] = "-"

        if gateway_desc['results']['gw_image_name'] in older_amis:
            init_table['Gateway ' + str(idx)]["Replace"] = "Yes"
        else:

            init_table['Gateway ' + str(idx)]["Replace"] = "-"
    return init_table




def main():
    controller = input("Enter Controller IP: ")
    username = input("Enter Controller username: ")
    password = getpass.getpass(prompt='Enter Controller password: ')
    aws_access_key = input("Enter AWS Access Key: ")
    aws_secret_key = getpass.getpass(prompt="Enter AWS Secret Key: ")

    try:
        cid = login(controller, username, password)
    except:
        print("Unable to connect to Controller: ", controller)
        sys.exit(1)
    gateways = get_all_gateways(controller, cid)
    empty_table = start_table(len(all_gateways)+1)
    main_table = create_table()
    final_table = populate_table(controller, cid, aws_access_key, aws_secret_key)
    df = pd.DataFrame(final_table).T
    df_index = df.set_index('Number')
    df_index.to_csv('gw_list.csv')
    df_index.to_html('gw_list.html', justify='center')
    print("Created file gw_list.html")
    print("Created file gw_list.csv")





if __name__ == "__main__":
    main()
