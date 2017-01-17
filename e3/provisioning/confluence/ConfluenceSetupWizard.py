from mechanize import ParseResponse, urlopen, urljoin


def find_form_by_id(forms, id_attr):
    return find_form_by_attr(forms, {'key': 'id', 'value': id_attr})


def find_form_by_name(forms, name):
    return find_form_by_attr(forms, {'key': 'name', 'value': name})


def find_form_by_attr(forms, attr):
    for frm in forms:
        if str(frm.attrs[attr["key"]]) == attr["value"]:
            return frm
    return None


class ConfluenceIntance:
    def __init__(self, base_url, properties=None):
        self.base_url = base_url
        self.properties = properties


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
        form["confLicenseString"] = "AAABDg0ODAoPeNptUF1Lw0AQfL9fEfD55JI2pAbuIV4iRPMhbSpRfDnjVg/SS7iPYP+9SdOiFWEXd\n\
ndmmGGvKgvOvZUO8cYKXRIuicPiyvGI66MYdKNEb0QnKevkrrUgG3gNnWTgreXTHTEFxyHmBuikw\n\
iTAxEXNyL/mjREDUKMsoB/NvB8JmWhAaqgOPRR8D5SVeZ6sWRplqJ2hJ1B60ngo50IakHyMkHz1Q\n\
h3OlsFvy8Lu30CVO9ZabUAV3TtoSlCpPrgUevaPTMu1FlyiDagBVBrT22Bxg+tt+oDrl/oOL9bRM\n\
9okBR0bZ/5qRTx/iU5pR3qWxhfIhfVWj5kpds/8/9M+WtV8cg1/H/cNLE6BtTAsAhRd83UUQYuGZ\n\
cOk0/kRIWK7N/BT1AIUVCaT+e8bNzSBLgPETBQTlT5H0Ys=X02dp"
        return self

    def go_next(self):
        go_next_form = find_form_by_id(self._forms, "licenseform")
        print go_next_form
        print "Go to next action %s" % go_next_form.action
        next_page_response = urlopen(go_next_form.click())
        return LoadContentPage( self._confluence_instance, response=next_page_response)


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
        return LoadContentPage(self._confluence_instance, response=next_page_response)


class FinishSetupPage(PageObject):
    def __init__(self, confluence_instance, response=None, path=None):
        PageObject.__init__(self, confluence_instance, response=None, path=None)
        print 'Finish setup Confluence !!!'


if __name__ == '__main__':
    selectBundles = BundleSelectionPage(ConfluenceIntance("http://localhost:8080/confluence/")).visit()
    licensePage = selectBundles.go_next()
    print "--------------------Go to License Page-------------------------------"
    loadContentPage = licensePage.fill_license().go_next()
    print "--------------------Go to Load Content Page--------------------------"
    userMgmtPage = loadContentPage.with_empty_site()
    print "--------------------Go to User Mgnt Page-----------------------------"
    setupAdminPage = userMgmtPage.with_confluence_manage_users()
    print "--------------------Go to Setup Admin Page---------------------------"
    finishSetupPage = setupAdminPage.fill_admin_info().go_next()
    print "--------------------Go to Finish Page--------------------------------"
