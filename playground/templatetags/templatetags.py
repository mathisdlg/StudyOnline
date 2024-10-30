from django import template
from django_redis import get_redis_connection

register = template.Library()

@register.simple_tag(name="is_prof")
def is_prof(username, uuid):
    r = get_redis_connection("default")
    user = r.hgetall(f"user:{username}")
    user_token = r.get(f"user_token:{username}")

    if user == {} or user_token is None:
        return False

    if uuid == user_token.decode():
        return user[b"account_type"].decode() == "Prof"

    return False
