import requests, json, click, urllib3
urllib3.disable_warnings()

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

@click.command()
@click.option('--tenant', '-t', help='Tenant name')
@click.option('--bucket', '-b', help='Tenant bucket name')
@click.option('--hostname', '-h', help='host ip')
@click.option('--maxspace', '-m', help='Max bucket space in GB')
@click.option('--warn', '-w', type=float, help='Warning threshold')
@click.option('--crit', '-c', type=float, help='Crit threshold')
@click.option('--username', '-u', help='Username')
@click.option('--password', '-p', help='Password')
def main(tenant, bucket, hostname, maxspace, warn, crit, username, password):
    HEADERS={'Content-Type': 'application/json',
    'Accept': 'application/json'}
    API='/api/v2'
    API_TOKEN_PATH = API + '/authorize'
    API_ID_PATH = API + '/grid/accounts'
    PROT='https://'

    hostname = PROT+str(hostname)
    data = build_api_data(username, password)
    auth_api = build_api_path(hostname, API_TOKEN_PATH)
    id_api = build_api_path(hostname, API_ID_PATH)
    cookies = req_post(auth_api, HEADERS, data).cookies
    id_json = req_get(id_api, HEADERS, cookies)
    bucket_id = return_bucket_id(id_json, tenant)
    bucket_api = return_bucket_api(hostname, API, bucket_id)
    bucket_json = req_get(bucket_api, HEADERS, cookies)
    bucket_usage_value = return_bucket_usage(bucket_json, bucket)
    gig_usage = convert_bytes_to_GB(bucket_usage_value)
    maxspace = int(maxspace)
    warn_decimal = calc_percentage(warn)
    crit_decimal = calc_percentage(crit)
    warn_usage = maxspace * warn_decimal
    crit_usage = maxspace * crit_decimal
    space_free = maxspace - gig_usage
    bucket_percent_free = (float(space_free)/float(maxspace))*100
    bucket_percent_free = round(bucket_percent_free, 1)

    if gig_usage <= warn_usage:
        print('OK - {}GB in use - {}% bucket space remaining | bucket_space_used={}GB;{};{}'.format(gig_usage, bucket_percent_free, gig_usage, warn, crit))
        exit(0)
    elif gig_usage >= warn_usage and gig_usage <= crit_usage:
        print('WARN - {}GB in use - {}% bucket space remaining | bucket_space_used={}GB;{};{}'.format(gig_usage, bucket_percent_free, gig_usage, warn, crit))
        exit(1)
    elif gig_usage >= crit_usage:
        print('CRIT - {}GB in use - {}% bucket space remaining | bucket_space_used={}GB;{};{}'.format(gig_usage, bucket_percent_free, gig_usage, warn, crit))
        exit(2)
    else:
        print('Value Unknown')
        exit(3)


main()
