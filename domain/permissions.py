

class Permissions():

    permissions = {
        "BASIC_USER_PERMISSIONS": "139586718784"
    }

    def get_permission_id(self, permission_name):
        return self.permissions.get(permission_name, None)
