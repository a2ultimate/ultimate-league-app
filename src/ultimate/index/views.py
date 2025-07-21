from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from ultimate.index.models import NewsArticle, StaticContent
from ultimate.forms import AnnoucementsForm
from ultimate.utils.calendar import get_events
from ultimate.utils.email_groups import add_to_group

CACHE_KEY_CALENDAR_EVENTS = "CALENDAR_EVENTS"


def index(request):
    news_articles = NewsArticle.objects.filter(published__lte=timezone.now())[:5]

    display_events = cache.get(CACHE_KEY_CALENDAR_EVENTS, None)

    if not display_events:
        events = get_events()
        if events:
            display_events = events[:7]
            cache.set(CACHE_KEY_CALENDAR_EVENTS, display_events, 86400)

    return render(
        request,
        "index/index.html",
        {
            "news_articles": news_articles,
            "events": display_events,
        },
    )


def news(request, url):
    try:
        if url.isdigit():
            news_article = NewsArticle.objects.get(id=url)
        else:
            news_article = NewsArticle.objects.get(url=url)
    except NewsArticle.DoesNotExist:
        news_article = None

    if not news_article:
        raise Http404("Season Not Found")

    return render(request, "index/news.html", {"article": news_article})


def announcements(request):
    if request.method == "POST":
        form = AnnoucementsForm(request.POST)
        user_email_address = request.POST.get("email", False)
        group_email_address = getattr(settings, "ANNOUNCEMENTS_GROUP_ADDRESS", False)

        if form.is_valid() and user_email_address and group_email_address:
            success_count = add_to_group(
                group_email_address=group_email_address,
                email_address=user_email_address,
            )

            if success_count:
                messages.success(request, "Your email address was added successfully.")
                return HttpResponseRedirect(reverse("announcements"))
            else:
                messages.error(
                    request,
                    "Your email address could not be added. It is possible that you are already a member.",
                )

        else:
            messages.error(request, "There was an error on the form you submitted.")
    else:
        form = AnnoucementsForm()

    return render(
        request,
        "index/announcements.html",
        {
            "form": form,
        },
    )


def static(request, content_url):
    try:
        page_content = get_object_or_404(StaticContent, url=content_url)
    except StaticContent.DoesNotExist:
        page_content = ""
    return render(request, "index/static.html", {"content": page_content})
