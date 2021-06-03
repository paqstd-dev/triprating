# Trip Rating

[![Build Status](https://www.travis-ci.com/paqstd-dev/triprating.svg?branch=master)](https://www.travis-ci.com/paqstd-dev/triprating)

## Tech Stack
Docker, Nginx, Python (Django), SQLite3 (as default).  

## Install
> cp .env.example .env  
> docker-compose build --no-cache  
> docker-compose up -d  
> make postbuild  

And open localhost:8000 as default.  


## Handler
> from trips.handler import TripFinder  

> finder = TripFinder(city='Washington', days=3, miles=400)

> finder.search(rating=True) # it call loop and after call finder.rating(sort=True)

## Author
@paqstd