# Using Redis in Development

Start redis in the background with:

```shell
$ docker run --name redis -d -p 6379:6379 redis
```

Next, optionally, test redis using the redis CLI as follows:

```
$ docker run -it --network host --rm redis redis-cli
127.0.0.1:6379> HSET bike:1 model Deimos brand Ergonom type 'Enduro bikes' price 4972
(integer) 4
127.0.0.1:6379> HGET bike:1 model
"Deimos"
127.0.0.1:6379> HGETALL bike:1
1) "model"
2) "Deimos"
3) "brand"
4) "Ergonom"
5) "type"
6) "Enduro bikes"
7) "price"
8) "4972"
127.0.0.1:6379> 
```
