# 1 Deploy a redis in docker loaclly

##### 1.1 **Create redis folders**
```shell
# create redis.conf 
mkdir -p deploy/redis/conf/
mkdir -p deploy/redis/data/

```
##### 1.2 **Write simple conf file**
```shell
cat >> redis.conf  << EOF 
# set redis server port
port 6379 

# set up password 
requirepass 123456

# open redis data persistent
appendonly yes
EOF
```
##### 1.3 **Build docker contaner for redis**
```
docker run -d -p 16379:6379 --restart=always -v $('pwd')/redis/conf/redis.conf:/etc/redis/redis.conf -v $('pwd')/redis/data/:/redis/data --name slack_redis redis redis-server /etc/redis/redis.conf
```


