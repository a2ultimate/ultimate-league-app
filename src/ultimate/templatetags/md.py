from django import template
import markdown2

register = template.Library()


@register.filter
def markdownify(text):
    # safe_mode governs how the function handles raw HTML
    return markdown2.markdown(text, safe_mode='escape')
    # return text
