# Trip Rating

[![Build Status](https://www.travis-ci.com/paqstd-dev/triprating.svg?branch=master)](https://www.travis-ci.com/paqstd-dev/triprating)

## Tech Stack
Docker  
Nginx  
Python (Django, Multiprocessing) 


## Install
` $ cp .env.example .env  `   
` $ docker-compose build --no-cache  `   
` $ docker-compose up -d  `   
` $ make postbuild  `   

And open localhost:8000 as default.  


## Handler
```
from trips.handler import TripFinder

finder = TripFinder(
    city='Washington',  # the city from which the journey begins
    days=3,             # number of travel days (travel from the starting city is not counted)
    miles=400,          # the maximum number of miles a car can drive
    ttl=60,             # time to live cache (default = 24h)
    client='127.0.1'    # client for redis cache prefix (default = 'default')
)

# one process
finder.search()

# some processes
finder.multisearch()

# show result
trips = finder.rating()
```


## Author
@paqstd