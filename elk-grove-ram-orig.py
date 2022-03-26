import requests
import json
import re


def alert_on_discount(l_modelYear, l_model, l_trim, l_msrp2Print, l_final2Print, l_discountPercent, l_vin):
    percent_sign = '%'
    print ("alert - %i - %s %s with %2.2f%s discount. MSRP %s, Offered Price %s" % (
        l_modelYear, 
        l_model, 
        l_trim, 
        abs(l_discountPercent), 
        percent_sign, 
        l_msrp2Print, 
        l_final2Print)
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


def main():
    url = 'https://www.elkgrovedodge.net/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_NEW:inventory-data-bus1/getInventory?make=Ram&bodyStyle=Crew%20Cab&driveLine=4x4&normalFuelType=Diesel&sortBy=internetPrice%20asc&pageSize=100'
    response = json.loads(requests.get(url).text)

    # alert when discount is more than ...
    alert_percent_threshold = -5.0

    # get dealer info 
    dealer = response['pageInfo']['trackingData'][0]['address']['accountName']
    print ('-' * 35)
    print (dealer)
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
    dealer = response['pageInfo']['trackingData'][0]['address']['accountName']

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
        discountPercent =  (((int(final) / int(msrp)) -1) * 100)
        discountPercent = round(discountPercent, 2)
        if discountPercent <= alert_percent_threshold:
            # discountPercent = str(discountPercent) + "*"
            # print('{:4s} | {:16s} | {:42s} | {:8s} | {:8s} | {:6s} | {:18s}'.format(
            #     str(modelYear), 
            #     str(model), 
            #     str(trim), 
            #     str(msrp2Print), 
            #     str(final2Print), 
            #     str(discountPercent), 
            #     str(vin)
            #     )
            # )
            alert_on_discount(modelYear, model, trim, msrp2Print, final2Print, discountPercent, vin)


if __name__ == "__main__":
    # execute only if run as a script
    main()