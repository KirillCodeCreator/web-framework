import os


class TemplateEngine:
    def __init__(self, template_dir):
        self.template_dir = template_dir

    def render(self, template_name, context=None):
        if context is None:
            context = {}

        template_path = os.path.join(self.template_dir, template_name)
        with open(template_path, 'r') as file:
            template_content = file.read()

        rendered_content = template_content
        for key, value in context.items():
            rendered_content = rendered_content.replace(f'{{{{ {key} }}}}', str(value))

        return rendered_content
