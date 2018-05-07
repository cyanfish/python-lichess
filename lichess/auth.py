
class AuthBase(object):

    def headers(self):
        return {}
    
    def cookies(self):
        return {}


class OAuthToken(AuthBase):

    def __init__(self, token):
        self.token = token

    def headers(self):
        return {'Authorization': 'Bearer %s' % self.token}


class Cookie(AuthBase):

    def __init__(self, jar):
        self.jar = jar
    
    def cookies(self):
        return self.jar


EMPTY = AuthBase()
