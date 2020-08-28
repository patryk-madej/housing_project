import json
import requests
import boto3
from bs4 import BeautifulSoup
from urllib import request, parse
from datetime import datetime
from os import environ


def lambda_handler(event, context):

    google_api_key=environ['google_api_key'] #for coordinates
    apigateway_DBendpoint = environ['apigateway_DBendpoint']  #for dynamoDB coordinates

    
    url1= 'https://www.otodom.pl/sprzedaz/mieszkanie/wroclaw/?search%5Bfilter_float_price%3Afrom%5D=200000&search%5Bfilter_float_price%3Ato%5D=400000&search%5Bfilter_float_price_per_m%3Afrom%5D=3000&search%5Bfilter_float_m%3Afrom%5D=30&search%5Bfilter_enum_rooms_num%5D%5B0%5D=2&search%5Bfilter_enum_rooms_num%5D%5B1%5D=3&search%5Bfilter_enum_rooms_num%5D%5B2%5D=4&search%5Bfilter_enum_rooms_num%5D%5B3%5D=5&search%5Bfilter_enum_rooms_num%5D%5B4%5D=6&search%5Bfilter_enum_rooms_num%5D%5B5%5D=7&search%5Bfilter_enum_rooms_num%5D%5B6%5D=8&search%5Bfilter_enum_market%5D=secondary&search%5Border%5D=created_at_first%3Adesc&search%5Bregion_id%5D=1&search%5Bsubregion_id%5D=381&search%5Bcity_id%5D=39&nrAdsPerPage=72'
    url2= 'https://gratka.pl/nieruchomosci/mieszkania?liczba-pokoi:min=2&powierzchnia-w-m2:min=30&cena-calkowita:max=400000&cena-calkowita:min=200000&rynek=wtorny&cena-za-m2:min=3000&lokalizacja[0]=116327&lokalizacja[1]=17218337&lokalizacja[2]=88889'
    url3= 'https://www.szybko.pl/l/na-sprzedaz/lokal-mieszkalny/Wroc%C5%82aw?assetType=lokal-mieszkalny&localization_search_text=Wroc%C5%82aw&market=aftermarket&price_min_sell=200000&price_max_sell=400000&meters_min=30&rooms_min=2&price_meters_min=3000'#
    url4= 'https://www.morizon.pl/mieszkania/wroclaw/?ps%5Bprice_from%5D=200000&ps%5Bprice_to%5D=400000&ps%5Bprice_m2_from%5D=3000&ps%5Bliving_area_from%5D=30&ps%5Bnumber_of_rooms_from%5D=2&ps%5Bmarket_type%5D%5B0%5D=2'
    url5= 'https://www.domiporta.pl/mieszkanie/sprzedam/dolnoslaskie/wroclaw?Surface.From=30&Price.From=200000&Price.To=400000&Rooms.From=2&PricePerMeter.From=3000&Rynek=Wtorny'
    
    
    
    # # Scraping url1: otodom.pl
    
    
    def get_last_page1(url):
        
        result = requests.get(url)
        source = result.content
        soup = BeautifulSoup(source, 'html.parser')
        pager = soup.find("ul",{'class': 'pager'}) #find just one
        
        if pager == None:
            return 1
        else:
        
            pages=[]
    
            for i in range(len(pager)):
                try:
                    txt=pager.text.split()[i]
                    if txt != '...':
                        pages.append(int(txt))
                except:
                    break
    
            last_page = pages[-1]
    
            return last_page
    
        
        
    def get_list_of_soups1(url):
        
        list_of_soups=[]
        for page in range(1,get_last_page1(url)+1):
            try:
                result = requests.get(url+'&Page='+str(page))
                source = result.content
                soup = BeautifulSoup(source, 'html.parser')
                ads = soup.find_all("div",{'class': 'offer-item-details'}) 
                list_of_soups.append(ads)
            except IndexError:
                break
                
        return list_of_soups
    

    all_ads1 = []
    
    try:
        for soup in get_list_of_soups1(url1):
            for s in soup:
    
                name = s.find("span",{'class': 'offer-item-title'}).text.replace('"','').replace("'",'').replace('  ',' ')
                district  = s.find("p",{'class': 'text-nowrap'}).text.replace('Mieszkanie na sprzedaż: ','').replace(', dolnośląskie','')
                price = s.find("li",{'class': 'offer-item-price'}).text.strip().replace(' zł','').replace(' ','').replace(',','.')
                rooms = s.find("li",{'class': 'offer-item-rooms hidden-xs'}).text.replace(' pokoje','').replace(' pokoi','')
                sq = s.find("li",{'class': 'hidden-xs offer-item-area'}).text.replace(' m²','').replace(',','.')
                price_sq = s.find("li",{'class': 'hidden-xs offer-item-price-per-m'}).text.replace(' zł/m²','').replace(' ','')
                link = s.find('a')['href'].strip()
                
                ad=[name,district,int(float(price)),int(rooms),round(float(sq)),int(price_sq),link]
                
                all_ads1.append(ad)
                
    except Exception as e:
        print('error: website changed or unresponsive',e)
    
    
    
    
    
    # # Scraping url2: gratka.pl


    def get_last_page2(url):
        
        result = requests.get(url)
        source = result.content
        soup = BeautifulSoup(source, 'html.parser')
        pager = soup.find("div",{'class': 'pagination'}) #find just one
        last_page = pager.find_all("a")[-2].text
        
        return int(last_page)
    
    def get_list_of_soups2(url):
        list_of_soups2=[]
        for page in range(1,get_last_page2(url)+1):
            try:
    
                result = requests.get(url+'&Page='+str(page))
                source = result.content
                
                soup = BeautifulSoup(source, 'html.parser')
                ads = soup.find_all("div",{'class': 'teaserEstate__infoBox'}) 
                
                list_of_soups2.append(ads)
                
            except IndexError:
                break
                
        return list_of_soups2
    
    
    
    all_ads2 = []
    
    try:
        for soup in get_list_of_soups2(url2):
            for s in soup:
    
                name = s.find("a",{'class': 'teaserEstate__anchor'}).text   #.replace('"','').replace("'",'').replace('  ',' ')
                district  = s.find("span",{'class': 'teaserEstate__localization'}).text.replace('\n','').replace('  ','').replace(', dolnośląskie','')
                price = s.find("p",{'class': 'teaserEstate__price'}).text.strip().replace(' zł','').replace(' ','')[:6]
                rooms = s.find("ul",{'class': 'teaserEstate__offerParams'}).findAll('li')[1].text.replace(' pokoje','').replace(' pokoi','')
                sq = s.find("ul",{'class': 'teaserEstate__offerParams'}).find("li").text.replace(' m2','').replace(',','.')
                price_sq = s.find("span",{'class': 'teaserEstate__additionalPrice'}).text.replace('zł/m2','').replace(' ','')
                link = s.find('a',{'class': 'teaserEstate__anchor'})['href'].strip()
                
                ad=[name,district,int(price),int(rooms),round(float(sq)),int(price_sq),link]
                
                all_ads2.append(ad)
                
    except Exception as e:
        print('error: website changed or unresponsive',e)
    
    
    
    
    
    # # Scraping url3: szybko.pl
    
    def get_last_page3(url):
    
        result = requests.get(url)
        source = result.content
        soup = BeautifulSoup(source, 'html.parser')
        last_page = soup.find_all("li",{'class': 'blank'})[1].text
        
        return int(last_page)
    
    
    def get_list_of_soups3(url):
        list_of_soups=[]
        for page in range(1,get_last_page3(url)+1):
            try:
                result = requests.get(url+'&strona='+str(page))
                #print('RESULT:',result)
                source = result.content
                soup = BeautifulSoup(source, 'html.parser')
                #print('SOUP:',soup) #it's fine
                ads = soup.find_all("div",{'class': "listing-content"})
                #print('ADS:',ads)
                list_of_soups.append(ads)
                
            except Exception as e:
                print(e)
                break
            
        return list_of_soups


    all_ads3 = []
    for soup in get_list_of_soups3(url3):
        for s in soup:
            name = s.find("a",{'class': 'listing-title-heading hide-overflow-text'}).find("div",{'class': "tooltip"}).text#.replace('Szczegóły ogłoszenia - ','')
            district  = s.find("a",{'class': 'mapClassClick list-elem-address popup-gmaps'}).text.replace('\n','').replace('  ','').replace(', dolnośląskie','').strip()
            price = s.find("div",{'class': 'listing-title'}).find_all("span")[2]['content']#.text.strip().replace(' zł','').replace(' ','')[:6]
            rooms = s.find("li",{'class': 'asset-feature rooms'}).text.replace(' ','')
            sq = s.find("li",{'class': 'asset-feature area'}).text.replace('m²','').replace(',','.')
            price_sq = int(price)/round(float(sq))
            link = s.find('a')['href'].strip()
    
            ad=[name,district,int(price),int(rooms),round(float(sq)),int(price_sq),link]
            all_ads3.append(ad)
    
    
    
    
    # # Scraping url4: morizon.pl
    
    def get_last_page4(url):
    
        result = requests.get(url)
        source = result.content
        soup = BeautifulSoup(source, 'html.parser')
        last_page = soup.find("ul",{'class': 'nav nav-pills mz-pagination-number'}).find_all('a')[-2].text#.replace('\n','')
        
        return int(last_page) #int
    
    def get_list_of_soups4(url):
        
        list_of_soups=[]
        
        for page in range(1,get_last_page4(url)+1):
            try:
    
                result = requests.get(url+'&page='+str(page))
                source = result.content
                soup = BeautifulSoup(source, 'html.parser')
                ads = soup.find_all("section",{'class': "single-result__content single-result__content--height"}) 
                list_of_soups.append(ads)
                
            except IndexError:
                break
                
        return list_of_soups
    
    
    all_ads4 = []
    
    try:
        for soup in get_list_of_soups4(url4):
            for s in soup:
                try:
                    name = s.find("h3",{'class': "single-result__category single-result__category--title"})
                    try:
                        name=name.text.replace('\n','').strip()
                    except:
                        name='Mieszkanie'
    
                    district  = s.find("h2",{'class': 'single-result__title'}).text.replace('\n','').strip().replace('dolnośląskie, ','')
                    price = s.find("p",{'class': 'single-result__price'}).text.strip().replace('zł','').replace(u'\xa0','')
                    rooms = s.find("ul",{'class': 'param list-unstyled list-inline'}).text.replace('\n','')[:1]
                    sqm = s.find("ul",{'class': 'param list-unstyled list-inline'}).find_all('li')[1].text.replace(' m²','').replace(' m²','')
                    price_sq = s.find("p",{'class': 'single-result__price single-result__price--currency'}).text.replace(' ','').replace(',','.').replace('zł/m²','')
                    link = s.find('a')['href'].strip()
    
                    ad=[name,district,int(price),int(rooms),round(float(sqm)),round(float(price_sq)),link]
    
                    all_ads4.append(ad)
    
                except:
                    #price = s.find("p",{'class': 'single-result__price'})#.text.strip().replace('zł','').replace(u'\xa0','')
                    #print(price,e, end='\n\n')
                    continue
                            
    except Exception as e:
        print('error: website changed or unresponsive. Exception:',e)
    
    
    
    
    # # Scraping url5: domiporta.pl
    
    def get_last_page5(url):
    
        result = requests.get(url)
        source = result.content
        soup = BeautifulSoup(source, 'html.parser')
        last_page = soup.find("ul",{'class': 'pagination'}).find_all("li")[-2].text        
        
        return int(last_page) #int
    
    def get_list_of_soups5(url):
        
        list_of_soups=[]
        
        for page in range(1,get_last_page5(url)+1):
            try:
    
                result = requests.get(url+'&PageNumber='+str(page))
                source = result.content
                soup = BeautifulSoup(source, 'html.parser')
                ads = soup.find_all("div",{'class': "sneakpeak__data sneakpeak__data--list"}) 
                list_of_soups.append(ads)
                
            except IndexError:
                break
                
        return list_of_soups
    
    all_ads5 = []
    
    try:
        for soup in get_list_of_soups5(url5):
            for s in soup:
                try:
                    name = 'Mieszkanie'#s.find("span",{'class': 'sneakpeak__title--bold'}).text.replace('mieszkanie ','')
                    district  = s.find("span",{'class': 'sneakpeak__title--bold'}).text.replace('mieszkanie ','')
                    price = s.find("span",{'class': 'sneakpeak__details_price'}).text.strip().replace(' zł','').replace('\xa0','')#[:6]
                    rooms = s.find("span",{'class': 'sneakpeak__details_item sneakpeak__details_item--room'}).text.strip()
                    sqm = s.find("span",{'class': 'sneakpeak__details_item sneakpeak__details_item--area'}).text.replace(',','.').replace('m2','').strip()
                    price_sq = s.find("span",{'class': 'sneakpeak__details_item sneakpeak__details_item--price'}).text.replace('\xa0','').replace('zł/m2','').replace(' ','').strip()
                    link = 'https://www.domiporta.pl'+s.find('a')['href'].strip()
    
                    ad=[name,district,int(price),int(rooms),round(float(sqm)),round(float(price_sq)),link]
    
                    all_ads5.append(ad)
    
                except Exception as e:
                    #price = s.find("p",{'class': 'single-result__price'})#.text.strip().replace('zł','').replace(u'\xa0','')
                    print(e,'/probably not a real listing')
                    continue
                            
    except Exception as e:
        print('error: website changed or unresponsive. Exception:',e)
        
        
    
    
    
    # # Cleaning
    
    # In[17]:
    print(len(all_ads1),len(all_ads2),len(all_ads3),len(all_ads4),len(all_ads5))
    
    all_ads=all_ads1+all_ads2+all_ads3+all_ads4+all_ads5
    
    def removeAccents(input_text):
        strange='ĄąĆćĘęŁłŃńÓóŚśŹźŻż'
        ascii_replacements='AaCcEeLlNnOoSsZzZz'   
        translator=str.maketrans(strange,ascii_replacements)  
        
        return input_text.translate(translator)
    
    
    #remove duplicates using set()
    s = set()
    original_ads = []
    for name, district, price, rooms, sqm, price_sq, link in all_ads: 
        l=(name,price_sq)
        
        if l not in s:
            s.add(l)
            original_ads.append([name, district, price, rooms, sqm, price_sq, link])
            
            
    # filter by the name of district
    rejected_ads = []
    selected_ads = []
    for ad in original_ads: 
        
        if any(s in ad[0] for s in ('Psi','Muchob','Broch','Partyn','Jagod','Kleci','Kozan','Leśn')):
            rejected_ads.append(ad)
            
        elif any(s in ad[1] for s in ('Nowy Dw','Kuźniki','Psi','Muchob','Broch','Księże','Pilczy', 'Leśnica',
                                      'Partyn','Jagod','Kleci','Kozan','Żerniki','Stabłowice','Maślice', 'Pracz')):
            rejected_ads.append(ad)
            
        else:
            ad[1] = removeAccents(ad[1]) # translate into ascii district names
            selected_ads.append(ad)
    
    print('original_ads:',len(original_ads))
    print('rejected_ads',len(rejected_ads))
    print('selected_ads:',len(selected_ads))
    
    
    # # Coordinates
    
    def get_coordinate(district):
        district_url = parse.quote(district).replace(' ','+') #replace(quote) special symbols and spaces
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={district_url}&key={google_api_key}'
        req = request.Request(url)
        source = request.urlopen(req).read()
        deserialised = json.loads(source)
        coordinate = deserialised['results'][0]['geometry']['location']
        return coordinate
    
    
    def get_lat(coordinate):
        return coordinate['lat']
    
    
    def get_lon(coordinate):
        return coordinate['lng']
    
    districts_all = [ad[1] for ad in selected_ads] 
    districts_uniq=list(set(districts_all)) #filter out duplicates
    
    # read from the coordinates DynamoDB
    result = requests.get(url=apigateway_DBendpoint)
    source = result.content
    coordinatesDB = json.loads(source)
    
    districts_saved=[]
    for i in range(len(coordinatesDB)):
        districts_saved.append(coordinatesDB[i]['district'])
        
    districts_really_uniq=[]
    for i in range(len(districts_uniq)):
        if districts_uniq[i] not in districts_saved:
            districts_really_uniq.append(districts_uniq[i])
            
    print('districts_really_uniq:',len(districts_really_uniq))
    
    
    #get new coordinates through Google Maps API
    coordinates = [get_coordinate(district) for district in districts_really_uniq] 
    
    
    # pair
    for i in range(len(districts_really_uniq)):
        coordinates[i].update({'district':districts_really_uniq[i]})
    
        
    # send new coordinates to the DynamoDB
    for i in range(len(coordinates)):
        coordinates[i]['district']=removeAccents(coordinates[i]['district'])
        body = coordinates[i] #turn each dictionary in the inp list into json object
        r = requests.post(url = apigateway_DBendpoint, json = body) 
        pastebin_url = r.text 
        print("Coordinates DB updated:", pastebin_url) 
        
    coordinatesDB += coordinates
    
    
    # add latitudes and longitudes to ads in original_ads
    for i in range(len(selected_ads)):
        for j in range(len(coordinatesDB)):
            if selected_ads[i][1] == coordinatesDB[j]['district']:
                
                selected_ads[i].append(coordinatesDB[j]["lat"])
                selected_ads[i].append(coordinatesDB[j]["lng"])
    
    
    # # Send to S3 and then to another Lambda and to RDS
    
    keys=['ID','Name','District','Price','Rooms','sqm','Price_sq','Link','Latitude', 'Longitude']
    
    # prepare new list inp, for the database
    inp=[]
    for ad in selected_ads:
        ad[0]=removeAccents(ad[0])
        ad[1]=removeAccents(ad[1])
        
        ad.insert(0,0) # add temporary ID
        inp.append(dict(zip(keys, ad)))
        ad.remove(0) # remove temporary ID
    
    print('db input:',len(inp))
    
    
    #create timestamps
    now=str(datetime.now())
    timestamp=now.replace('-','').replace(':','').replace(' ','')[2:10]
    
    
    # generate IDs based on timestamp and order
    for i in range(len(inp)):
        
        if i < 10:
            ID=int(timestamp+str('000')+str(i))
            
        elif i > 9 and i < 100:
            ID=int(timestamp+str('00')+str(i))
            
        elif i > 99 and i < 1000:
            ID=int(timestamp+str('0')+str(i))
            
        elif i > 999 and i < 10000:
            ID=int(timestamp+str('')+str(i))
                    
        else:
            raise Exception("ID wasn't generated, over 10 000 records")
        
        inp[i]["ID"]=ID
    

    
    # test for bugs and notify through SNS if any are found
    if len(all_ads1)==0 or len(all_ads2)==0 or len(all_ads3)==0 or len(all_ads4)==0 or len(all_ads5)==0 or len(selected_ads)==0:
        er='Lambda error: Housing Wroclaw Scraper'
        msg=f"""None of the values should be zero:
scraped ads: 1,2,3,4,5: {len(all_ads1),len(all_ads2),len(all_ads3),len(all_ads4),len(all_ads5)}
all_ads: {len(all_ads)}
original_ads: {len(original_ads)}
selected_ads: {len(selected_ads)}
coordinates: {len(coordinatesDB)}

Check Lambda: https://eu-west-2.console.aws.amazon.com/lambda/home?region=eu-west-2#/functions/housing_wroclaw_scrape?tab=configuration
Check CloudWatch: https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#logStream:group=%252Faws%252Flambda%252Fhousing_wroclaw_scrape"""
        
        print(er,msg)

        client = boto3.client('sns')
        response = client.publish(
            TargetArn='arn:aws:sns:eu-west-2:709303708159:dynamodb',
            Message=msg,
            Subject=er
        )
        
        
    else:
        print('success')
    
        #send to s3
        object=json.dumps(inp)
        s3 = boto3.client('s3')
        s3.put_object(
             Body=str(object),
             Bucket='housing-scraper',
             Key='housing_wroclaw.data'
        )
    
    return 'NOTHING WAS ZERO!','coordinates:',len(coordinatesDB),'original_ads:',len(original_ads),'selected_ads:',len(selected_ads),'ADS 1,2,3,4,5:',len(all_ads1),len(all_ads2),len(all_ads3),len(all_ads4),len(all_ads5),'ALL ADS:',len(all_ads)
