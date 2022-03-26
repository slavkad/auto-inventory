import requests
import json
import re
import sys, getopt

"""

The purpose of this script it to leverage a JSON call to dealer.com network and to parse the output.
With this methond, we can scan any dealership which utilizes dealer.com network for their inventory.

using in conjunction with filters, I am able to get a list of all matching vehicles and determine their
current discount.

to identify if dealership is using dealer.com, simply nagivate to their site and scroll to the bottom

to extend this script:
1) nagivate to dealer site and build your search
2) get the url generated and extract search arguments, such as model, engine, package, etc.
3) in this script locate dealerDOTcom_dic dictionary and add element to it matching from existing examples.
    3a) be sure to add dealer url
    3b) be sure to split up search arguments.
4) remember the dictionary element name given for this new daeler

run the script with --dealer [your dictionary element name]

TODO:

* add alert mechanism to get notified when vehicle is available with certain discount percentage
* make nicer output
* extend the script to also process dealer Inspire network

NOTES:

JSON returned from the dealer site offers a lot more details and data.  This script is easy to extend to
provide more info if desired.

"""

def alert_on_discount(l_modelYear, l_model, l_trim, l_msrp2Print, l_final2Print, l_discountPercent, l_vin):
    percent_sign = '%'
    print ("ALERT!!! - %i - %s %s with %2.2f%s discount. MSRP %s, Offered Price %s, VIN %s" % (
        l_modelYear, 
        l_model, 
        l_trim, 
        abs(l_discountPercent), 
        percent_sign, 
        l_msrp2Print, 
        l_final2Print,
        l_vin)
    )

    # print ("alert - %i - %s %s with %2.2f discount. MSRP " % (l_modelYear, l_model, l_trim, l_discountPercent))

# get JSON of list of vehicles matching the filter.
# customized URL to paginate on 100 vehicles.
# to find this url .. navigate to elk grove dodge ram site.
# generate a search you are interested in.
# click inspect and copy generated URL call which produced inventory JSON.
# place that URL here.
# you can also add pageSize to the end of the URL to increase number of returns
# you recieve, thefore no need to make multiple calls.

def dealerDOTcom(l_dealer_info):
    l_dealer_url = l_dealer_info['url']
    uri = 'apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_NEW:inventory-data-bus1/getInventory?'
    search = ''
    for l_each_search in l_dealer_info['search']:
        search = search + l_each_search + '=' + l_dealer_info['search'][l_each_search] + '&'
    uri_static = 'sortBy=internetPrice%20asc&pageSize=100'
    url = l_dealer_url + '/' + uri + search + uri_static

    response = json.loads(requests.get(url).text)

    # alert when discount is more than ...
    alert_percent_threshold = l_dealer_info['alert_percent_threshold']

    # get dealer info 
    dealer = response['pageInfo']['trackingData'][0]['address']['accountName']
    print ()
    print ('=' * 50)
    print ('=' * 50)
    print ()
    print ('-' * 35)
    print (dealer)
    print (l_dealer_url)
    print ('-' * 35)
    print ()

    # split the URL
    (uri,arguments)=url.split('?')
    # split the arguments into array
    search_criteria=arguments.split('&')
    # exclude list of what we do not want to display as part of arguments list
    exclude_search_criteria = ['sortBy', 'pageSize']
    # loop through and figure out if we want to display it
    # search filters
    print ()
    print ("Search filters")
    print ('-' * 30)
    for each_search_criteria in search_criteria:
        (key, value) = each_search_criteria.split('=')
        if key not in exclude_search_criteria:
            value = re.sub('%20', ' ', value)
            print (key, " = ", value)
    # loop throught he cars and pull the details out
    print ('-' * 30)
    print ()

    for i in response["pageInfo"]['trackingData']:
        modelYear = i['modelYear']
        trim = i['trim']
        vin = i['vin']
        model = i['model']
        try:
            msrp = i['pricing']['msrp'].replace(',', '').replace('$', '')
        except:
            msrp = 999999

        try:
            final = i['pricing']['finalPrice'].replace(',', '').replace('$', '')
        except:
            final = 999999
        
        try:
            msrp2Print = i['pricing']['msrp']
        except:
            msrp2Print = 999999

        try:
            final2Print = i['pricing']['finalPrice']
        except:
            final2Print = 999999
        # calculate percent off from MSRP to final price and round to 2 decimal points
        # negative number is discount
        # positive number is markup
        try:
            discountPercent =  (((int(final) / int(msrp)) -1) * 100)
        except:
            discountPercent = 0.0
        # lets make this float more friendly to read
        # and round to 2 decimal points
        discountPercent = round(discountPercent, 2)
        # decide if discount on car is below our threshold
        # to display
        if discountPercent <= alert_percent_threshold:
            alert_on_discount(modelYear, model, trim, msrp2Print, final2Print, discountPercent, vin)


# work in progress
def dealerInspire (argv):
    url = 'https://sewjn80htn-3.algolianet.com/1/indexes/*/queries'

    payload = {
	"{\"requests\":[{\"indexName\":\"boardwalkchryslerdodgejeepram_production_inventory_specials_price\",\"params\":\"maxValuesPerFacet": "250",
	"hitsPerPage": [
		"20",
		"1",
		"1"
	],
	"facets": [
		"[\"features\",\"our_price\",\"lightning.lease_monthly_payment\",\"lightning.finance_monthly_payment\",\"type\",\"api_id\",\"year\",\"make\",\"model\",\"model_number\",\"trim\",\"body\",\"doors\",\"miles\",\"ext_color_generic\",\"features\",\"lightning.isSpecial\",\"lightning.locations\",\"fueltype\",\"engine_description\",\"transmission_description\",\"metal_flags\",\"city_mpg\",\"hw_mpg\",\"days_in_stock\",\"lightning.locations.meta_location\",\"ctp\",\"Misc_Price2\",\"special_field_2\",\"model_code\",\"Invoice\",\"title_vrp\",\"ext_color\",\"int_color\",\"certified\",\"lightning\",\"location\",\"drivetrain\",\"int_options\",\"ext_options\",\"cylinders\",\"vin\",\"stock\",\"msrp\",\"our_price_label\",\"finance_details\",\"lease_details\",\"thumbnail\",\"link\",\"objectID\",\"algolia_sort_order\"]",
		"fueltype",
		"type"
	],
	"tagFilters": [
		"",
		"",
		""
	],
	"facetFilters": [
		"[[\"fueltype:Gasoline Fuel\"],[\"type:New\"]]\"},{\"indexName\":\"boardwalkchryslerdodgejeepram_production_inventory_specials_price\",\"params\":\"maxValuesPerFacet",
		"[[\"type:New\"]]\"},{\"indexName\":\"boardwalkchryslerdodgejeepram_production_inventory_specials_price\",\"params\":\"maxValuesPerFacet",
		"[[\"fueltype:Gasoline Fuel\"]]\"}]}"
	],
	"page": [
		"0",
		"0"
	],
	"attributesToRetrieve": [
		"[]",
		"[]"
	],
	"attributesToHighlight": [
		"[]",
		"[]"
	],
	"attributesToSnippet": [
		"[]",
		"[]"
	],
	"analytics": [
		"false",
		"false"
	],
	"clickAnalytics": [
		"false",
		"false"
	]
    }

    # response = requests.post(url, data = json.dumps(payload), headers = {'Content-type': 'application/json', 'Accept': 'application/json'})
    response = requests.post(url, data = payload, headers = {
        'Content-type': 'application/json', 
        'Accept': 'application/json',
        'x-algolia-agent': 'Algolia for JavaScript (4.8.5); Browser (lite); JS Helper (3.4.4)',
        'x-algolia-api-key': '179608f32563367799314290254e3e44',
        'x-algolia-application-id': 'SEWJN80HTN'
        }
    )
 
    print (response)

def main(argv):

    # build a dictions for dealer specific details, search, and alert threshold
    # witht his script, any dealer leveraging dealer.com framework we can query
    dealerDOTcom_dic = {
        'elkGroveRam' :  {
            'url' :  'https://www.elkgrovedodge.net',
            'alert_percent_threshold' : -5.0,
            'search' : {
                'make' : 'Ram',
                'bodyStyle' : 'Crew Cab',
                'driveLine' : '4x4',
                'normalFuelType' : 'Diesel'
            }
        },
        'putnamChrysler' :  {
            'url' :  'https://www.putnamchrysler.com/',
            'alert_percent_threshold' : -0.0,
            'search' : {
                'make' : 'Ram',
                'bodyStyle' : 'Crew Cab',
                'driveLine' : '4x4',
                'normalFuelType' : 'Diesel'
            }
        },
        'burlingameVolvo' :  {
            'url' :  'https://www.volvocarsburlingame.com/',
            'alert_percent_threshold' : -0.0,
            'search' : {
                'model' : 'XC90 Recharge Plug-In Hybrid',
                'gvBodyStyle': 'SUV'
            }
        },
        'ElkGroveKia' :  {
            'url' :  'https://www.elkgrovekia.com/',
            'alert_percent_threshold' : -0.0,
            'search' : {
                'model' : 'Telluride',
                'year': '2022',
                'gvBodyStyle': 'SUV',
                'normalDriveLine': 'AWD'
            }
        },
        # 'StevenCreekHundai' :  {
        #     'url' :  'https://www.stevenscreekhyundai.com/',
        #     'alert_percent_threshold' : -0.0,
        #     'search' : {
        #         'model' : 'Palisade',
        #         'drivetrain': 'AWD',
        #         'make': 'Hyundai'
        #     }
        # }
    }

    # lets process the arguments
    user_arg = ''
    try:
        opts, args = getopt.getopt(argv,"had:",["all","dealer="])
    except getopt.GetoptError:
        print ('elk-grove-ram.py -d|--dealer <dealerName> -a|--all')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('elk-grove-ram.py -d|--dealer <dealerName>  -a|--all')
            sys.exit()
        elif opt in ("-a", "--all"):
            user_arg = "all"
        elif opt in ("-d", "--dealer"):
            user_arg = arg

    if user_arg == "all":
        for each_dealer in dealerDOTcom_dic:
            dealerDOTcom(dealerDOTcom_dic[each_dealer])
    else:
        # refer to specific dictionary element to only display results for one dealer
        dealerDOTcom(dealerDOTcom_dic[user_arg])

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])