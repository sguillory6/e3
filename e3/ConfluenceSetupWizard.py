from splinter import Browser
from common import Utils


class ConfluenceIntance():
    def __init__(self, base_url):
        self.base_url = base_url


class BaseObject():
    def __init__(self, browser, confluence_instance):
        self._browser = browser
        self._confluence_instance = confluence_instance


class PageObject(BaseObject):
    def __init__(self, browser, confluence_instance):
        BaseObject.__init__(browser, confluence_instance)

    def visit(self):
        self._browser.visit(self._confluence_instance.base_url)
        return self


class BundleSelectionPage(PageObject):
    def __init__(self, browser, confluence_instance):
        PageObject.__init__(browser, confluence_instance)
        self._next_button = self._browser.find_by_id('setup-next-button')

    def go_next(self):
        self._next_button.click()
        Utils.poll_url(
            self._confluence_instance.base_url,
            900,
            lambda response: 'setuplicense.action' in response.url
        )
        return LicensePage(self._browser, self._confluence_instance)


class LicensePage(PageObject):
    def __init__(self, browser, confluence_instance):
        PageObject.__init__(browser, confluence_instance)
        self._license_txt_field = self._browser.find_by_id('confLicenseString')
        self._next_button = self._browser.find_by_id('setup-next-button')

    def fill_license(self):
        self._license_txt_field.fill('some license is filled in')

    def go_next(self):
        self._next_button.click()
        Utils.poll_url(
            self._confluence_instance.base_url,
            900,
            lambda response: 'setupdata-start.action' in response.url
        )
        return LoadContentPage(self._browser, self._confluence_instance)


class LoadContentPage(PageObject):
    def __init__(self, browser, confluence_instance):
        PageObject.__init__(browser, confluence_instance)
        self._demo_data_button = self._browser.find_by_css('form#demoChoiceForm input.setupdata-button')
        self._empty_data_button = self._browser.find_by_css('form#blankChoiceForm input.setupdata-button')

    def with_empty_site(self):
        self._empty_data_button.click()
        Utils.poll_url(
            self._confluence_instance.base_url,
            900,
            lambda response: 'setupusermanagementchoice-start.action' in response.url
        )
        return UserManagementPage(self._browser, self._confluence_instance)


class UserManagementPage(PageObject):
    def __init__(self, browser, confluence_instance):
        PageObject.__init__(browser, confluence_instance)
        self._confluence_button = self._browser.find_by_css('input#internal')

    def with_confluence_manage_users(self):
        self._empty_data_button.click()
        return SetupAdminPage(self._browser, self._confluence_instance)


class SetupAdminPage(PageObject):
    def __init__(self, browser, confluence_instance):
        PageObject.__init__(browser, confluence_instance)
        self._full_name_txt = self._browser.find_by_id('fullName')
        self._email_txt = self._browser.find_by_id('email')
        self._password_txt = self._browser.find_by_id('password')
        self._confirm_password_txt = self._browser.find_by_id('confirm')
        self._next_button = self._browser.find_by_id('setup-next-button')

    def fill_admin_info(self):
        self._full_name_txt.fill('admin')
        self._email_txt.fill('admin@g.c')
        self._password_txt.fill('admin')
        self._confirm_password_txt.fill('admin')

    def go_next(self):
        self._next_button.click()
        Utils.poll_url(
            self._confluence_instance.base_url,
            900,
            lambda response: 'setupdata-start.action' in response.url
        )
        return LoadContentPage(self._browser, self._confluence_instance)


class FinishSetupPage(PageObject):
    def __init__(self, browser, confluence_instance):
        PageObject.__init__(browser, confluence_instance)
        self._full_name_txt = self._browser.find_by_id('fullName')
        self._email_txt = self._browser.find_by_id('email')
        self._password_txt = self._browser.find_by_id('password')
        self._confirm_password_txt = self._browser.find_by_id('confirm')
        self._next_button = self._browser.find_by_id('setup-next-button')