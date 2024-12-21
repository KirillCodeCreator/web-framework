import os


class TemplateEngine:
    def __init__(self, template_dir):
        self.template_dir = template_dir

    def render(self, template_name, context=None):
        if context is None:
            context = {}

        template_path = os.path.join(self.template_dir, template_name)
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()

        rendered_content = template_content
        for key, value in context.items():
            rendered_content = rendered_content.replace(f'{{{{ {key} }}}}', str(value))

        css_links = ''.join([f'<link rel="stylesheet" type="text/css" href="/styles/{css_file}">' for css_file in
                             context.get('css_files', [])])
        rendered_content = rendered_content.replace('{{ css_links }}', css_links)

        js_links = ''.join([f'<script src="/scripts/{js_file}"></script>' for js_file in context.get('js_files', [])])
        rendered_content = rendered_content.replace('{{ js_links }}', js_links)

        return rendered_content
