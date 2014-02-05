from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social import exceptions as social_exceptions
from django.http import HttpResponse, HttpResponseRedirect, Http404
from base.views import error_page


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):

        if hasattr(social_exceptions, exception.__class__.__name__):
            err_title = 'Authentication Error'
            err_msg = 'There was an error during authentication process.\n\n%s' % exception
            return error_page(request, err_title, err_msg)

        else:
            raise exception

