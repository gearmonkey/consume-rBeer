import Beer

NUM_BEERS = 164478


for id in range(1, 164479):
  beer = Beer.Beer(id)
  beer.parse_metadata()
  print("{},{}".format(id, "\""+beer.name+"\""))
