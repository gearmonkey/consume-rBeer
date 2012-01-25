import Beer

NUM_BEERS = 164478

def log_rating(id, (_,userid, rating)):
  print("{};{};{}".format(id, userid, rating))

for id in range(1, 164479):
  beer = Beer.Beer(id)
  beer.scrape_user_rating_list()
  map(lambda rating: log_rating(id, rating), beer.ratings)
