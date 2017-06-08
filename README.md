# sortable code challenge
Steps to run:
1. pip install xmltodict
2. python ./entity_match.py

Steps for the solution:
1. Normalize data for both products and listings using xml rules.
2. Construct a 3 layers linked hash map on Manufacture, Family, Model from products.
3. Go through each listing, extract Manufacture to match on the first layer to get the related Family.
4. Extract family to match on the second layer to get the related Model.
   If model matched, the listing is belong to this product.
   
Running time: 6 seconds.  (ubuntu 14.10 8G RAM Intel i7-6500u)

