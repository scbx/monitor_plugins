import requests, click, json, urllib3, ast
urllib3.disable_warnings()

def build_api_path(ip, api):
    #builds the api path, adds the host ip with
    uri = ip+api
    return uri

def build_auth_data(username, password):
    #create data for http post requests for authorization cookie
    data = {"username":username, "password":password, "cookie":True}
    data = json.dumps(data)
    return data

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
@click.option('--hostname', '-h', help='host ip')
@click.option('--warn', '-w', type=float, help='Warning threshold percentage')
@click.option('--crit', '-c', type=float, help='Crit threshold percentage')
@click.option('--username', '-u', help='Username' )
@click.option('--password', '-p', help='Password' )
def main(hostname, warn, crit, username, password):
    HEADERS={'Content-Type': 'application/json',
    'Accept': 'application/json',}
    API='/api/v2'
    API_TOKEN_PATH = API + '/authorize'
    API_TOTAL_STORAGE_PATH = API + '/grid/metric-query?query=storagegrid_storage_utilization_total_space_bytes&timeout=120s'
    API_USED_STORAGE_PATH = API + '/grid/metric-query?query=storagegrid_storage_utilization_usable_space_bytes&timeout=120s'
    PROT='https://'

    hostname = PROT+str(hostname)
    data = build_auth_data(username, password)
    auth_api = build_api_path(hostname, API_TOKEN_PATH)
    cookies = req_post(auth_api, HEADERS, data).cookies
    total_storage_path = build_api_path(hostname, API_TOTAL_STORAGE_PATH)
    used_storage_path = build_api_path(hostname, API_USED_STORAGE_PATH)
    total_storage_resp = req_get(total_storage_path, headers=HEADERS, cookies=cookies).text
    used_storage_resp = req_get(used_storage_path, headers=HEADERS, cookies=cookies).text
    total_storage_dict = ast.literal_eval(total_storage_resp)
    used_storage_dict = ast.literal_eval(used_storage_resp)
    total_storage = api_iterator(total_storage_dict)
    used_storage = api_iterator(used_storage_dict)
    warn_decimal = calc_percentage(warn)
    crit_decimal = calc_percentage(crit)
    total_storage_gig = convert_bytes_to_GB(total_storage)
    free_storage_gig = convert_bytes_to_GB(used_storage)
    warn_storage_gig = total_storage_gig*warn_decimal
    crit_storage_gig = total_storage_gig*crit_decimal
    used_storage_gig = total_storage_gig - free_storage_gig
    used_percent = int((float(free_storage_gig)/float(total_storage_gig))*100)
    if used_storage_gig <= warn_storage_gig:
        print('OK - {}GB in use - {}% space remaining | grid_storage_used={}GB;{};{}'.format(used_storage_gig, used_percent, used_storage_gig, warn, crit))
        exit(0)
    elif used_storage_gig >= warn_storage_gig and used_storage_gig <= crit_storage_gig:
        print('WARN - {}GB in use - {}% space remaining | grid_storage_used={}GB;{};{}'.format(used_storage_gig, used_percent, used_storage_gig, warn, crit))
        exit(1)
    elif used_storage_gig>= crit_storage_gig:
        print('CRIT - {}GB in use - {}% space remaining | grid_storage_used={}GB;{};{}'.format(used_storage_gig, used_percent, used_storage_gig, warn, crit))
        exit(2)
    else:
        print('Value Unknown')
        exit(3)


main()
