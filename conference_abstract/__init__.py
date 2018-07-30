"""Main entry point
"""
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory
import conference_abstract.auth
import conference_abstract.util
import pyramid.security

def notfound(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    return conference_abstract.util.generate_template('notfound.mako',{"user":user,"request":request})

def founderror(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = conference_abstract.auth.check_user(request)
    return conference_abstract.util.generate_template('error.mako',{"user":user,"request":request})

def main(global_config, **settings):
    settings['auth.secret'] = 'conference 2017 abstracts'
    settings['mako.directories'] = '%s:templates' % __name__

    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'], 
    )
    authz_policy = ACLAuthorizationPolicy()


    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
    )

    config.set_session_factory(SignedCookieSessionFactory(settings['auth.secret']))

    config.include("cornice")
    config.include('pyramid_mako')

    config.add_static_view('static', 'static', cache_max_age=0)

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    #config.add_route('reauth','/reauth')

    config.scan("conference_abstract.auth")
    config.scan("conference_abstract.services")
    config.scan("conference_abstract.views")
    
    config.add_notfound_view(notfound)
    #config.add_exception_view(founderror)
    
    return config.make_wsgi_app()


