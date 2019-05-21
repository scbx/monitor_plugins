from functions import *
from variables import *

#used to check individual bucket usage on the s3 cluster

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
    
    API_ID_PATH = API + '/grid/accounts'

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
