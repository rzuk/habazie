import logging
from allaccess.views import OAuthRedirect, OAuthCallback
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
print __name__


class EmailPermissionsRedirect(OAuthRedirect):

    def get_additional_parameters(self, provider):
        if provider.name == 'facebook':
            return {'scope': 'email'}
        if provider.name == 'google':
            perms = ['userinfo.email', 'userinfo.profile']
            scope = ' '.join(['https://www.googleapis.com/auth/' + p for p in perms])
            return {'scope': scope}
        return super(EmailPermissionsRedirect, self).get_additional_parameters(provider)


class AssociateCallback(OAuthCallback):

    def get_or_create_user(self, provider, access, info):
        logger.info('get_or_create %s %s' % (provider, info))
        return get_user_model().objects.get(email=info['email'])
