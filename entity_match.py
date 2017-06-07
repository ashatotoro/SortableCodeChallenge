import codecs
import json
import os
import xmltodict
import time

def loadRules(file):
    with codecs.open(input_path+normalization_file) as fd:
        doc = xmltodict.parse(fd.read())
    normalization_list = doc["Root"]["Dictionary"]["add"]
    return normalization_list

def normalizeElements(element, normalization_list):
    for pair in normalization_list:
        if element==pair["@word"]:
            return pair["@normalizedWord"]
    return element

def matchManufacturer(manufacturer_map, manufacturer, title):
    if manufacturer not in manufacturer_map:
        if title[0] in manufacturer_map:
            manufacturer = title[0]
        else:
            manufacturer = ""
    return manufacturer

def matchFamily(manufacturer_map, manufacturer, title, family_maxSize):   
    families = set([None])
    if manufacturer not in manufacturer_map:
        return families
    family_map = manufacturer_map[manufacturer]
    for i in range(0, len(title)):
        for j in range(i, i + (1 + family_maxSize)):
            if title[i:j] in family_map:
                families.add(title[i:j])
    return families

def matchModel(manufacturer_map, manufacturer, families, title, model_maxSize):   
    if manufacturer not in manufacturer_map:
        return ("","")
    if None not in manufacturer_map[manufacturer]:
        families.remove(None)
    best_model = ""
    best_family = ""
    best_match = 0
    for family in families:
        model_map = manufacturer_map[manufacturer][family]
        for i in range(0, len(title)):
            for j in range(i, i + (1 + model_maxSize)):
                if title[i:j] in model_map:
                    (best_family, best_model, best_match) = (family, title[i:j], j-i+1) if j-i+1 > best_match else (best_family, best_model, best_match)
    return best_family, best_model

def loadProductsToDict(file, normalization_list, output_data):
    manufacturer_map = {}
    famliy_maxSize = 0
    model_maxSize = 0
    with codecs.open(file, encoding="utf-8") as products:
        for line in products:
            product = json.loads(line)  
            manu = ''
            if 'manufacturer' in product:
                manu = normalizeElements(product['manufacturer'].lower(), normalization_list)
            family = ''
            if 'family' in product:
                family = normalizeElements(product['family'].lower(), normalization_list)
                famliy_maxSize = len(family) if len(family) > famliy_maxSize else famliy_maxSize
            model = ''
            if 'model' in product:
                model = normalizeElements(product['model'].lower(), normalization_list)
                model_maxSize = len(model) if len(model) > model_maxSize else model_maxSize
            product_name = ''
            if 'product_name' in product:
                product_name = product['product_name']
                if product_name not in output_data:
                    output_data[product_name] = {}
                    output_data[product_name]["product_name"] = product_name 
                    output_data[product_name]["listings"]=[]
            familiy_map = {}
            if manu in manufacturer_map: 
                familiy_map = manufacturer_map[manu]
            else:
                manufacturer_map[manu] = familiy_map
            model_map = {}
            if family in familiy_map:
                model_map = familiy_map[family]
            else:
                familiy_map[family] = model_map
            
            model_map[model] = product_name
    return (manufacturer_map, famliy_maxSize, model_maxSize)        

def matchListings(manufacturer_map, file, normalization_list, family_maxSize, model_maxSize, output_data):
    with codecs.open(file, encoding="utf-8") as listings:
        for line in listings:           
            listing = json.loads(line)
            manu = ''
            if 'manufacturer' in listing:
                manu = normalizeElements(listing['manufacturer'].lower(), normalization_list)
                title = normalizeElements(listing['title'].lower(), normalization_list)
                matchedManu = matchManufacturer(manufacturer_map, manu, title)
                if matchedManu=='':
                    continue
                families = matchFamily(manufacturer_map, matchedManu, title, family_maxSize)
                family, model = matchModel(manufacturer_map, matchedManu, families, title, model_maxSize)               
                if family in manufacturer_map[matchedManu] and model in manufacturer_map[matchedManu][family]:
                    product_name = manufacturer_map[matchedManu][family][model]
                    output_data[product_name]["listings"].append(listing)

def writeOutputToFile(output_data, file):
    with codecs.open(file, 'w', encoding='utf-8') as outfile:
        print('Writing results to ' + file)
        for value in output_data.values():
            line = json.dumps(value, ensure_ascii=False).encode('utf8')
            outfile.write(unicode(line, 'utf-8') + '\n')

if __name__ == "__main__":
    start_time = time.time()
    input_path = './input/'
    output_path = './output/'
    product_file = 'products.txt'
    listing_file = 'listings.txt'
    normalization_file = 'normalizationRules.xml'
    output_file = 'results.json'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    normalization_list = loadRules(input_path+normalization_file)
    output_data = {}
    (manufacturer_map, family_maxSize, model_maxSize) = loadProductsToDict(input_path+product_file, normalization_list, output_data)
    matchListings(manufacturer_map, input_path+listing_file, normalization_list, family_maxSize, model_maxSize, output_data)
    writeOutputToFile(output_data, output_path+output_file)
    print "My program took", time.time() - start_time, "to run"
