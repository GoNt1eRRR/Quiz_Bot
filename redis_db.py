import redis


def connect_to_db(host, port, password):
    return redis.Redis(
        host=host,
        port=port,
        password=password,
        decode_responses=True
    )