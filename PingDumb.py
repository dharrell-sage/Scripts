import requests
import json

requests.packages.urllib3.disable_warnings()

#This address will return code 403
#"https://www.sageone.com.au/",

url_array = ["https://finalaccounts.sageone.com", "https://corporationtax.sageone.com", "https://accountants.sageone.com", "https://app.br.sageone.com/notafiscal/robots.txt", "https://app.br.sageone.com/signup/new", "https://br.sageone.com", "https://mysageone.ca.sageone.com", "https://sageone.ca.sageone.com/health_check", "https://regulatory-reports.sagecompliance.com/health_check", "https://app.de.sageone.com/buchhaltung/health_check", "https://app.de.sageone.com/signup/new", "https://app.es.sageone.com/signup", "https://ab-service.eu.sageone.com/service/health", "https://addons.eu.sageone.com", "https://accounting.eu.sageone.com", "https://mysageone.eu.sageone.com", "https://business.eu.sageone.com/service/health", "https://central.eu.sageone.com/service/health", "https://subscription.eu.sageone.com/service/health", "https://user.eu.sageone.com/service/health", "https://app.fr.sageone.com/signup/new?product=accounts", "https://developers.sageone.com", "https://help.sageone.com", "https://api.sageone.com/health_check", "https://ab-service.na.sageone.com/service/health", "https://addons.na.sageone.com", "https://accounting.na.sageone.com", "https://stripe.na.sageone.com/service/health", "https://core-api.na.sageone.com/service/health", "https://subscription.na.sageone.com/service/health", "https://user.na.sageone.com/service/health", "https://central.na.sageone.com/service/health", "https://app.pt.sageone.com/signup/new", "https://app.sagetracks.com", "https://ab-service.uk.sageone.com/service/health", "https://accounts.sageone.com", "https://addons.sageone.com", "https://collaborate.sageone.com", "https://accounts-extra.sageone.com", "https://payroll.sageone.com", "https://bdp-service.sageone.com/service/health", "https://stripe.uk.sageone.com/service/health", "https://app.sageone.com", "https://uk.sageone.com", "https://invoicing.na.sageone.com/health_check", "https://mysageone.na.sageone.com", "https://sageone.na.sageone.com/health_check"]

def main():
    for url in url_array:
        statusCode = test_url(url)
        if statusCode:
            trigger_incident(url, statusCode)

def test_url(address):
    r = requests.get(address, allow_redirects=True, verify=False)
    if r.status_code != requests.codes.ok:
        #return r.status_code
        return r.status_code

def trigger_incident(URL,statusCode):

    API_KEY = 'Secret'
    SERVICE_ID = 'PSF4JHY'
    FROM = 'dustin.harrell@sage.com'

    #Triggers an incident via the V2 REST API using sample data.

    url = 'https://api.pagerduty.com/incidents'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY),
        'From': FROM
    }

    payload = {
        "incident": {
            "type": "incident",
            "title": "{url} is not responding to pings. Returned status code: {code}".format(url=URL, code=statusCode),
            "service": {
                "id": SERVICE_ID,
                "type": "service_reference"
            },
            "body": {
                "type": "incident_body",
                "details": "Investigate based off of the URL: {url}"
            }
        }
    }

    r = requests.post(url, headers=headers, data=json.dumps(payload))

    #print 'Status Code: {code}'.format(code=r.status_code)
    #print r.json()

if __name__ == '__main__':
    main()
