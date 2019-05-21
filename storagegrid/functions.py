import requests, json, click, urllib3, ast
urllib3.disable_warnings()

#using this as a seperate file to write functions and import into the modules

def build_auth_data(username, password):
    #create data for http post requests for authorization cookie
    data = {"username":username, "password":password, "cookie":True}
    data = json.dumps(data)
    return data

def build_api_path(ip, api):
    #builds the api path, adds the host ip with
    uri = ip+api
    return uri

def build_api_data(username, password):
    #create data for http post requests for authorization cookie
    data = {"username":username, "password":password, "cookie":True}
    data = json.dumps(data)
    return(data)

def req_post(uri, headers, data, verify=False):
    #requests post remplate
    r = requests.post(uri, headers=headers, data=str(data), verify=False)
    return r

def req_get(uri, headers, cookies, verify=False):
    #requests get template
    r = requests.get(uri, headers=headers, cookies=cookies, verify=False)
    return r

def api_iterator(response):
    #input api return value - return total disk size
    return_value = 0
    for entry in response['data']['result']:
        add_value = int(entry['value'][1])
        return_value = return_value + add_value
    return return_value

def return_bucket_id(json_resp, client):
    #takes in /grid/accounts api json response and returns tenant id
    json_resp = json_resp.text
    json_resp = json.loads(json_resp)
    if json_resp['data'][0]['name'] == client:
        tenant_id = json_resp['data'][0]['id']
        return tenant_id

def return_bucket_api(host,api,bucket_id):
    #takes in hostname, api version and bucket id and returns json
    bucket_api = host+api+'/grid/accounts/'+bucket_id +'/usage'
    return bucket_api

def return_bucket_usage(json_resp, bucket_name):
    #takes in json_resp and bucket name and returns data used for that bucket
    json_resp = json_resp.text
    json_resp = json.loads(json_resp)
    bucket_array = json_resp['data']['buckets']
    for entry in bucket_array:
        if entry['name'] == bucket_name:
            return entry['dataBytes']

def calc_percentage(value):
    #calculate warn/crit value percentages
    value = float(value)
    value = value/100
    return value

def convert_bytes_to_GB(input):
    #converts bytes to storage GB
    output = input/1000/1000/1000
    return int(output)
