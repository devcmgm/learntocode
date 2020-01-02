import pymongo

client = pymongo.MongoClient(
   "mongodb+srv://root:demopass@cluster0-rlthj.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.sample_airbnb

collection = db['listingsAndReviews']
mydata = { "name" : "Deluxe Loft Suite" }

found = collection.find(mydata)

for x in found:
  print("Property Type: " + x["property_type"])

