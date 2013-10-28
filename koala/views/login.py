"""
Pyramid views for Login/Logout

"""
from pyramid.view import view_config

from ..forms.login import EucaLoginForm, AWSLoginForm


class LoginView(object):
    template = '../templates/login.pt'

    def __init__(self, request):
        self.request = request
        self.euca_login_form = EucaLoginForm(self.request)
        self.aws_login_form = AWSLoginForm(self.request)

    @view_config(route_name='login', request_method='GET', renderer=template)
    def login_page(self):
        return dict(
            euca_login_form=self.euca_login_form,
            aws_login_form=self.aws_login_form,
        )

    @view_config(route_name='login', request_method='POST', renderer=template)
    def handle_login(self):
        """Handle login form post"""
        login_type = self.request.POST.get('login_type')
        euca_login_form = self.euca_login_form
        aws_login_form = self.aws_login_form
        if login_type == 'Eucalyptus':
            euca_login_form = EucaLoginForm(self.request, formdata=self.request.POST)
            if euca_login_form.validate():
                return dict()
        elif login_type == 'AWS':
            aws_login_form = AWSLoginForm(self.request, formdata=self.request.POST)
            if aws_login_form.validate():
                return dict()
        return dict(
            euca_login_form=euca_login_form,
            aws_login_form=aws_login_form,
        )

