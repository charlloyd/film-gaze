# run main functions from other packages here

from bfiscrape import *

voters_list, filmid_manual_dict = scrape_bfi_voters()
film_list = scrape_bfi_films(voters_list, filmid_manual_dict)

print(len(voters_list))
print(len(film_list))