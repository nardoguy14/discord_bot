from domain.leagues import Role


class UserRepository():

    async def add_role(self, role_id, role_name):
        return await Role.create(role_id=role_id, name=role_name)