"""Asyncronous tasks for MDN scraping."""

from json import dumps
from traceback import format_exc

from celery import shared_task
import requests

from .models import FeaturePage, TranslatedContent
from .scrape import scrape_feature_page


@shared_task(ignore_result=True)
def start_crawl(featurepage_id):
    """Start the calling process for an MDN page."""
    fp = FeaturePage.objects.get(id=featurepage_id)
    assert fp.status == fp.STATUS_STARTING, fp.status
    meta = fp.meta()

    # Determine next state / task
    next_task = None
    if meta.status == meta.STATUS_STARTING:
        fp.status = fp.STATUS_META
        next_task = (fetch_meta, fp.id)
    elif meta.status == meta.STATUS_FETCHING:
        fp.status = fp.STATUS_META
    elif meta.status == meta.STATUS_FETCHED:
        fp.status = fp.STATUS_PAGES
        next_task = (fetch_all_translations, fp.id)
    else:
        assert meta.status == meta.STATUS_ERROR, meta.get_status_display()
        fp.status = fp.STATUS_ERROR
    fp.save()
    if next_task is not None:
        next_func, next_id = next_task
        next_func.delay(next_id)


@shared_task(ignore_result=True)
def fetch_meta(featurepage_id):
    """Fetch metadata for an MDN page."""
    fp = FeaturePage.objects.get(id=featurepage_id)
    assert fp.status == fp.STATUS_META, fp.get_status_display()
    meta = fp.meta()
    assert meta.status == meta.STATUS_STARTING, meta.get_status_display()

    # Avoid double fetching
    meta.status = meta.STATUS_FETCHING
    meta.save(update_fields=['status'])

    # Request and validate the metadata
    url = meta.url()
    r = requests.get(url, headers={'Cache-Control': 'no-cache'})
    next_task = None
    next_task_args = []
    if r.url != url and not r.url.endswith('$json'):
        # There was a redirect to the regular page
        meta.delete()
        fp.url = r.url
        fp.status = fp.STATUS_META
        fp.save()
    elif r.status_code != requests.codes.ok:
        issue = (
            'failed_download', 0, 0,
            {'url': url, 'status': r.status_code, 'content': r.text})
        meta.raw = 'Status %d, Content:\n%s' % (r.status_code, r.text)
        meta.status = meta.STATUS_ERROR
        next_task = r.raise_for_status
    else:
        if r.url != url and r.url.endswith('$json'):
            # There was a redirect to another meta (zone change)
            fp.url = r.url[:-len('$json')]
        try:
            meta.raw = dumps(r.json())
        except ValueError:
            meta.raw = 'Response is not JSON:\n' + r.text
            issue = ('bad_json', 0, 0, {'url': url, 'content': r.text})
            meta.status = meta.STATUS_ERROR
            next_task = r.json
        else:
            meta.status = meta.STATUS_FETCHED
    meta.save()

    # Determine next state / task
    if meta.status == meta.STATUS_ERROR:
        fp.status = fp.STATUS_ERROR
        fp.add_issue(issue)
    elif meta.status == fp.STATUS_META:
        next_task = fetch_meta.delay
        next_task_args = (fp.id, )
    else:
        assert meta.status == meta.STATUS_FETCHED, meta.get_status_display()
        fp.status = fp.STATUS_PAGES
        next_task = fetch_all_translations.delay
        next_task_args = (fp.id, )
    fp.save()
    assert next_task
    next_task(*next_task_args)


@shared_task(ignore_result=True)
def fetch_all_translations(featurepage_id):
    """Fetch all translations for an MDN page."""
    fp = FeaturePage.objects.get(id=featurepage_id)
    if fp.status != fp.STATUS_PAGES:
        # Exit early if not called after fetch_meta
        return
    translations = fp.translations()
    assert translations, translations

    # Gather / count by status
    to_fetch = []
    fetching = 0
    errored = 0
    for trans in translations:
        obj = trans.obj
        if obj is None:
            continue
        if obj.status == obj.STATUS_STARTING:
            to_fetch.append(trans.locale)
        elif obj.status == obj.STATUS_FETCHING:
            fetching += 1
        elif obj.status == obj.STATUS_ERROR:
            errored += 1
        else:
            assert obj.status == obj.STATUS_FETCHED, obj.get_status_display()

    # Determine next status / task
    if errored:
        fp.status = fp.STATUS_ERROR
        fp.save()
    elif (not fetching) and (not to_fetch):
        fp.status = fp.STATUS_PARSING
        fp.save()
        parse_page.delay(fp.id)
    elif to_fetch:
        fetch_translation.delay(fp.id, to_fetch[0])


@shared_task(ignore_result=True)
def fetch_translation(featurepage_id, locale):
    """Fetch a translations for an MDN page."""
    fp = FeaturePage.objects.get(id=featurepage_id)
    if fp.status in (fp.STATUS_PARSING, fp.STATUS_PARSED, fp.STATUS_NO_DATA):
        # Already fetched
        t = TranslatedContent.objects.get(page=fp, locale=locale)
        assert t.status == t.STATUS_FETCHED, t.get_status_display()
        return
    assert fp.status == fp.STATUS_PAGES, fp.get_status_display()
    t = TranslatedContent.objects.get(page=fp, locale=locale)
    assert t.status == t.STATUS_STARTING, t.get_status_display()

    # Avoid double fetching
    t.status = t.STATUS_FETCHING
    t.save(update_fields=['status'])

    # Request the translation
    url = t.url() + '?raw'
    r = requests.get(t.url() + '?raw', headers={'Cache-Control': 'no-cache'})
    t.raw = r.text
    if r.status_code == requests.codes.ok:
        t.status = t.STATUS_FETCHED
    else:
        t.status = t.STATUS_ERROR
        issue = ((
            'failed_download', 0, 0,
            {'url': url, 'status': r.status_code, 'content': r.text[:100]}))
        fp.add_issue(issue)
        fp.save()
    t.save()

    fetch_all_translations.delay(fp.id)


@shared_task(ignore_result=True)
def parse_page(featurepage_id):
    fp = FeaturePage.objects.get(id=featurepage_id)
    assert fp.status == fp.STATUS_PARSING, fp.get_status_display()
    try:
        scrape_feature_page(fp)
    except:
        # Unexpected exceptions are added and re-raised
        # Expected exceptions are handled by scrape_feature_page
        fp.status = FeaturePage.STATUS_ERROR
        fp.add_issue(('exception', 0, 0, {'traceback': format_exc()}))
        fp.save()
        raise
