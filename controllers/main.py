from odoo.addons.web.controllers.home import Home
from odoo import http
from odoo.http import request


class MedisiteHome(Home):

    @http.route('/', type='http', auth='public')
    def index(self, s_action=None, db=None, **kw):
        """Override root route: show homepage if not logged in."""
        if request.session.uid:
            return super().index(s_action=s_action, db=db, **kw)
        return request.redirect('/web/login')

    @http.route('/web/login', type='http', auth='public', readonly=False)
    def web_login(self, redirect=None, **kw):
        """Override login to use our custom homepage template."""
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("Custom web_login called with kw: %s", kw)
        
        response = super().web_login(redirect=redirect, **kw)
        _logger.info("Super response status: %s", getattr(response, 'status_code', None))
        
        # If login was successful, the parent already redirects
        if request.params.get('login_success'):
            return response

        # Check if the login is for other portals (Edupass or SHS)
        redirect_url = redirect or request.params.get('redirect') or ''
        referrer = request.httprequest.referrer or ''
        is_other_portal = any(path in redirect_url or path in referrer for path in ['edupass', 'shs', 'my/'])

        if is_other_portal:
            return response

        # For GET requests (showing login page), render our custom template
        if request.httprequest.method == 'GET' and not request.session.uid:
            values = response.qcontext if hasattr(response, 'qcontext') else {}
            values.setdefault('redirect', redirect or '/odoo')
            return request.render('medisite_clinic.medisite_homepage', values)

        # For failed POST (wrong credentials), also show our template with error
        if hasattr(response, 'qcontext'):
            values = response.qcontext
            values.setdefault('redirect', redirect or '/odoo')
            return request.render('medisite_clinic.medisite_homepage', values)

        return response
