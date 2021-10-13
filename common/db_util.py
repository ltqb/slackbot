import redis


def create_redis_cli(host, port, password):
    r = redis.Redis(
        host=host,
        port=port,
        password=password,
        decode_responses=True
    )
    return r



#
#cli=create_redis_session("127.0.0.1", 16379, "123456")
# cli get
#print(cli.get("hello"))
# cli set
#cli.set("1aaaa","aaaa")
