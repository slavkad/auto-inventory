import requests
import json

# get JSON of list of vehicles matching the filter.
# customized URL to paginate on 100 vehicles.
url = 'https://www.elkgrovedodge.net/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_NEW:inventory-data-bus1/getInventory?make=Ram&bodyStyle=Crew%20Cab&driveLine=4x4&normalFuelType=Diesel&sortBy=internetPrice%20asc&pageSize=100'

response = json.loads(requests.get(url).text)

# loop throught he cars and pull the details out
print('{:4s} | {:16s} | {:42s} | {:8s} | {:8s} | {:6s} | {:18s}'.format("Year", "Model", "Trim", "MSRP", "Final", "% Off", "VIN"))
print ('-' * 120)
for i in response["pageInfo"]['trackingData']:
    modelYear = i['modelYear']
    trim = i['trim']
    vin = i['vin']
    model = i['model']
    msrp = i['pricing']['msrp'].replace(',', '').replace('$', '')
    final = i['pricing']['finalPrice'].replace(',', '').replace('$', '')
    msrp2Print = i['pricing']['msrp']
    final2Print = i['pricing']['finalPrice']
    # calculate percent off from MSRP to final price and round to 2 decimal points
    # negative number is discount
    # positive number is markup
    discountPercent =  (((int(final) / int(msrp)) -1) * 100)
    discountPercent = round(discountPercent, 2)
    print('{:4s} | {:16s} | {:42s} | {:8s} | {:8s} | {:6s} | {:18s}'.format(
        str(modelYear), 
        str(model), 
        str(trim), 
        str(msrp2Print), 
        str(final2Print), 
        str(discountPercent), 
        str(vin)
        )
    )