from mechanize import ParseResponse, urlopen, urljoin
import xmlrpclib
import requests


def find_form_by_id(forms, id_attr):
    return find_form_by_attr(forms, {'key': 'id', 'value': id_attr})


def find_form_by_name(forms, name):
    return find_form_by_attr(forms, {'key': 'name', 'value': name})


def find_form_by_attr(forms, attr):
    for frm in forms:
        try:
            if str(frm.attrs[attr["key"]]) == attr["value"]:
                return frm
        except Exception as inst:
            pass
    return None


class ConfluenceInstance:
    def __init__(self, base_url, properties=None):
        self.base_url = base_url
        self.properties = None if not properties else \
            dict(map(lambda param: tuple(param.split('=', 1)), filter(None, properties.split(','))))
        print properties


class BaseObject:
    def __init__(self, confluence_instance):
        self._confluence_instance = confluence_instance


class PageObject(BaseObject):
    def __init__(self, confluence_instance, response=None, path=None):
        self._response = response
        self._forms = None if not self._response else ParseResponse(self._response, backwards_compat=False)
        self._path = path
        BaseObject.__init__(self, confluence_instance)

    def visit(self):
        url = urljoin(self._confluence_instance.base_url, self._path or '')
        print "visting page %s" % url
        self._response = urlopen(url)
        self._forms = ParseResponse(self._response, backwards_compat=False)
        return self


class BundleSelectionPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response, path)

    def go_next(self):
        go_next_form = find_form_by_id(self._forms, "selectBundlePluginsForm")
        print go_next_form
        print "Go to next action %s" % go_next_form.action
        next_page_response = urlopen(go_next_form.click())
        return LicensePage(self._confluence_instance, response=next_page_response)


class LicensePage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response, path)

    def fill_license(self):
        form = find_form_by_id(self._forms, "licenseform")
        form["confLicenseString"] = self._confluence_instance.properties['conf_license']
        return self

    def go_next(self):
        go_next_form = find_form_by_id(self._forms, "licenseform")
        print go_next_form
        print "Go to next action %s" % go_next_form.action
        next_page_response = urlopen(go_next_form.click())
        return LoadContentPage(self._confluence_instance, response=next_page_response)


class LoadContentPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response, path)

    def with_empty_site(self):
        go_next_form = find_form_by_id(self._forms, "blankChoiceForm")
        print go_next_form
        print "Go to next action %s" % go_next_form.action
        next_page_response = urlopen(go_next_form.click())
        return UserManagementPage(self._confluence_instance, response=next_page_response)


class UserManagementPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response, path)

    def with_confluence_manage_users(self):
        go_next_form = find_form_by_name(self._forms, "internaluser")
        print go_next_form
        print "Go to next action %s" % go_next_form.action
        next_page_response = urlopen(go_next_form.click())
        return SetupAdminPage(self._confluence_instance, response=next_page_response)


class SetupAdminPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response, path)
        self._go_next_form = None

    def fill_admin_info(self):
        self._go_next_form = find_form_by_name(self._forms, 'setupadministratorform')
        self._go_next_form['username'] = 'admin'
        self._go_next_form['fullName'] = 'admin'
        self._go_next_form['email'] = 'admin@g.c'
        self._go_next_form['password'] = 'admin'
        self._go_next_form['confirm'] = 'admin'
        return self

    def go_next(self):
        print self._go_next_form
        print "Go to next action %s" % self._go_next_form.action
        next_page_response = urlopen(self._go_next_form.click())
        return FinishSetupPage(self._confluence_instance, response=next_page_response)


class FinishSetupPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response=response, path=path)
        self._go_next_form = None
        print 'Finish setup Confluence !!!'

    def go_next(self):
        print "Go to further setting config"
        return ConfluenceFurtherSettingsPage(self._confluence_instance, path='admin/viewspacesconfig.action').visit()


class LoginPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response=response, path=path)
        self._go_next_form = None

    def admin_login(self, next_page):
        """
        Login with admin account then navigate to another page
        :param next_page:
        :return:
        """
        self._go_next_form = find_form_by_name(self._forms, 'loginform')
        self._go_next_form['os_username'] = 'admin'
        self._go_next_form['os_password'] = 'admin'
        urlopen(self._go_next_form.click())
        return next_page.visit()


class WebSudoPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None, forms=None, go_to_path=None):
        PageObject.__init__(self, confluence_instance, response=response, path=path)
        self._forms = forms
        self._go_next_form = None
        self._go_to_path = go_to_path

    def fill_admin_password(self):
        self._go_next_form = find_form_by_name(self._forms, 'authenticateform')
        self._go_next_form['password'] = 'admin'
        print self._go_next_form
        print "Go to next action %s" % self._go_next_form.action
        urlopen(self._go_next_form.click())
        print "Go to admin settings"
        url = urljoin(self._confluence_instance.base_url, self._go_to_path)
        print "visiting page %s" % url
        next_page_response = urlopen(url)
        return next_page_response


class ConfluenceFurtherSettingsPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response=response, path=path)
        self._go_next_form = None

    def login_web_sudo(self):
        """
        If current url is authenticate.action then we need to login websudo when return original page
        otherwise return itself
        :return: ConfluenceFurtherSettingsPage instance
        """
        print "Check if we need to login with websudo or not"
        str_url = self._response.geturl()
        if "authenticate.action" in str_url:
            print "Trying to login with websudo"
            web_sudo_page = WebSudoPage(
                self._confluence_instance,
                self._response, self._path,
                self._forms,
                'admin/editspacesconfig.action#features')
            next_page_response = web_sudo_page.fill_admin_password()
            print "Trying to login with websudo => Done"
            return ConfluenceFurtherSettingsPage(self._confluence_instance, response=next_page_response)

        return self

    def enable_xml_rpc(self):
        print "Filling a form to enable xml rpc"
        self._go_next_form = find_form_by_name(self._forms, 'editspacesconfig')
        self._go_next_form.set_single(True, name='allowRemoteApi')
        print self._go_next_form
        print "Filling a form to enable xml rpc => done"
        return self

    def submit(self):
        print "Go to next action %s" % self._go_next_form.action
        urlopen(self._go_next_form.click())
        url = urljoin(self._confluence_instance.base_url, 'admin/editsecurityconfig.action')
        next_page_response = urlopen(url)
        return ConfluenceSecuritySettingsPage(self._confluence_instance, next_page_response)


class ConfluenceSecuritySettingsPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response=response, path=path)
        self._go_next_form = None

    def login_web_sudo(self):
        """
        If current url is authenticate.action then we need to login websudo when return original page
        otherwise return itself
        :return: ConfluenceFurtherSettingsPage instance
        """
        print "Check if we need to login with websudo or not"
        str_url = self._response.geturl()
        if "authenticate.action" in str_url:
            print "Trying to login with websudo"
            web_sudo_page = WebSudoPage(
                self._confluence_instance,
                self._response, self._path,
                self._forms,
                '/confluence/admin/editspacesconfig.action#features')
            next_page_response = web_sudo_page.fill_admin_password()
            print "Trying to login with websudo => Done"
            return ConfluenceFurtherSettingsPage(self._confluence_instance, response=next_page_response)

        return self

    def disable_web_sudo(self):
        print "Filling security settings"
        self._go_next_form = find_form_by_name(self._forms, "editsecurityconfig")
        self._go_next_form.set_single(False, name='webSudoEnabled')
        print self._go_next_form
        print "Filling security settings => done"
        return self

    def submit(self):
        print "Go to next action %s" % self._go_next_form.action
        next_page_response = urlopen(self._go_next_form.click())


if __name__ == '__main__':
    confluence_instance = ConfluenceInstance("http://localhost:8080/confluence/",
                                            "conf_license=AAABKQ0ODAoPeNptUV1LwzAUfd+vCPiiDx3tRhkOAs6uk+q+mJtU367htgbbZNykxf17s6bCFCFP5\n\
x7OV64WJNljo1g0YtF4Gk6mUcSyZM9GYRQPhFbFMNHKgrDpCmTFy1ZbarQq78BWYIwENRS69kzHk\n\
i1yR0APbIGsQlpDjdwjc7CQoLJIF7SlFKgM7k9H7KjJZrVKd0k2W/r7hkpQ0oCVWvEtWJLi01/SF\n\
qrG4wVUptdzSZ2DAiUw/TpKOjlX5K7RJAjdiwbPSC1SNuf3k/FtkB+ypyB/yxfBeDd79RLrpn5H2\n\
hQHg2R4HIZh36gh8QEGfxTjXvGyx/+evj4aQfLYBXa7FlWDLiS7Ps/C/C437OzGOuNfH9BN8+AGL\n\
9mL7i+EXfm/ab4B7kecvDAsAhRPd5JtwVC0TRgGfz5rxy80GnCUlwIUVq55S9Oew9F0b5pnFN8Ms\n\
de+cwU=X02eu")
    selectBundles = BundleSelectionPage(confluence_instance).visit()
    license_page = selectBundles.go_next()
    print "--------------------Selecting no bundles--------------------------------"
    load_content_page = license_page.fill_license().go_next()
    print "--------------------Configuring license---------------------------------"
    user_mgmt_page = load_content_page.with_empty_site()
    print "--------------------Loading empty site----------------------------------"
    setup_admin_page = user_mgmt_page.with_confluence_manage_users()
    print "--------------------Configuring internal user management----------------"
    finish_setup_page = setup_admin_page.fill_admin_info().go_next()
    print "--------------------Adding admin account--------------------------------"
    further_settings_page = finish_setup_page.go_next()
    print "--------------------Confluence Further Settings-------------------------"
    security_settings_page = further_settings_page.login_web_sudo().enable_xml_rpc().submit()
    print "--------------------Confluence Security Settings------------------------"
    security_settings_page.login_web_sudo().submit()
