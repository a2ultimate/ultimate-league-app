from django import template
from django.utils.safestring import mark_safe
import markdown2

register = template.Library()


@register.filter
def markdownify(text):
    # safe_mode='escape' neutralizes any raw HTML in the source text, so the
    # rendered markup is safe to emit unescaped. mark_safe stops Django's
    # template auto-escaping from double-escaping the generated HTML.
    return mark_safe(markdown2.markdown(text or '', safe_mode='escape'))
