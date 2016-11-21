from jinja2 import Template


class TemplateEngine(object):
    """A super simple template engine around jinja2"""
    __base_dir = None
    __arguments = dict()

    def __init__(self, base_dir, arguments):
        self.__base_dir = base_dir
        self.__arguments['tpl'] = self
        self.__arguments.update(arguments)

    def load(self, template_name):
        template_path = self.__base_dir + "/" + template_name
        return file(template_path).read()

    def include(self, template_name):
        return Template(self.load(template_name)).render(self.__arguments) + "\n"
