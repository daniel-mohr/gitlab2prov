import uuid
import random
from gitlab2prov.domain import objects
from gitlab2prov.domain.constants import ProvRole


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_user():
    name = f"user-name-{random_suffix()}"
    email = f"user-email-{random_suffix()}"
    username = f"gitlab-user-name-{random_suffix()}"
    id = f"gitlab-user-id-{random_suffix()}"
    role = random.choice(list(vars(ProvRole).values()))
    return objects.User(name, email, username, id, role)

