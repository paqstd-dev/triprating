# Trip Rating

## Install
> cp .env.example .env  
> docker-compose build --no-cache  
> docker-compose up -d  
> make postbuild  


## Handler
> from trips.handler import TripFinder  

> finder = TripFinder(city='Washington', days=3, miles=400)

> finder.search(rating=True) # it call loop and after call finder.rating(sort=True)

## Author
@paqstd