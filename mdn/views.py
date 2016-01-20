"""Views for MDN migration app."""
from collections import Counter
from json import loads
from math import floor

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.six.moves.urllib.parse import urlparse, urlunparse, quote
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import CreateView, UpdateView
import unicodecsv as csv

from .models import FeaturePage, Issue, ISSUES, SEVERITIES, validate_mdn_url
from .tasks import start_crawl, parse_page

DEV_PREFIX = 'https://developer.mozilla.org/en-US/'


def can_create(user):
    return user.has_perm('mdn.add_featurepage')


def can_refresh(user):
    return True


class FeaturePageListView(ListView):
    model = FeaturePage
    template_name = 'mdn/feature_page_list.html'
    paginate_by = 50
    topics = (
        'docs/Web/API',
        'docs/Web/CSS',
        'docs/Web/Events',
        'docs/Web/Guide',
        'docs/Web/HTML',
        'docs/Web/JavaScript',
        'docs/Web/MathML',
        'docs/Web/SVG',
    )
    status_names = dict(FeaturePage.STATUS_CHOICES)
    statuses = (
        (str(FeaturePage.STATUS_PARSED_CRITICAL),
            status_names[FeaturePage.STATUS_PARSED_CRITICAL], 'danger'),
        (str(FeaturePage.STATUS_PARSED_ERROR),
            status_names[FeaturePage.STATUS_PARSED_ERROR], 'danger'),
        (str(FeaturePage.STATUS_PARSED_WARNING),
            status_names[FeaturePage.STATUS_PARSED_WARNING], 'warning'),
        (str(FeaturePage.STATUS_PARSED), 'No Errors', 'success'),
        (str(FeaturePage.STATUS_NO_DATA),
            status_names[FeaturePage.STATUS_NO_DATA], 'default'),
        ('other', 'Other', 'info'),
    )
    standard_statuses = (
        FeaturePage.STATUS_PARSED_CRITICAL,
        FeaturePage.STATUS_PARSED_ERROR,
        FeaturePage.STATUS_PARSED_WARNING,
        FeaturePage.STATUS_PARSED,
        FeaturePage.STATUS_NO_DATA)
    progress_bar_order = (
        (FeaturePage.STATUS_PARSED_CRITICAL, 'Critical errors',
            ('danger', 'striped')),
        (FeaturePage.STATUS_PARSED_ERROR, 'Errors', ('danger',)),
        (FeaturePage.STATUS_PARSED_WARNING, 'Warnings', ('warning',)),
        (FeaturePage.STATUS_PARSED, 'No Errors', ('success',)),
    )
    committed_options = [
        (str(value), name) for value, name in FeaturePage.COMMITTED_CHOICES]
    converted_options = [
        (str(value), name) for value, name in FeaturePage.CONVERTED_CHOICES]

    def get_queryset(self):
        qs = FeaturePage.objects.order_by('url')

        topic = self.request.GET.get('topic')
        if topic:
            qs = qs.filter(url__startswith=DEV_PREFIX + topic)

        status = self.request.GET.get('status')
        if status:
            if status == 'other':
                qs = qs.exclude(status__in=self.standard_statuses)
            else:
                qs = qs.filter(status=status)

        committed = self.request.GET.get('committed')
        if committed:
            qs = qs.filter(committed=committed)

        converted_compat = self.request.GET.get('converted_compat')
        if converted_compat:
            qs = qs.filter(converted_compat=converted_compat)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(FeaturePageListView, self).get_context_data(**kwargs)
        ctx['request'] = self.request

        # Topic filter buttons
        ctx['topic'] = self.request.GET.get('topic')
        ctx['topics'] = self.topics

        # Status filter buttons
        ctx['status'] = self.request.GET.get('status')
        ctx['statuses'] = self.statuses

        # Committed status buttons
        ctx['committed'] = self.request.GET.get('committed')
        ctx['committed_options'] = self.committed_options

        # Converted status buttons
        ctx['converted_compat'] = self.request.GET.get('converted_compat')
        ctx['converted_options'] = self.converted_options

        # Status progress bar
        raw_status_counts = self.object_list.order_by(
            'status').values('status').annotate(total=Count('status'))
        status_counts = {}
        total = 0
        for item in raw_status_counts:
            status_counts[item['status']] = item['total']
            total += item['total']
        have_data_count = sum(
            status_counts.get(item[0], 0) for item in self.progress_bar_order)
        data_counts_list = []
        for status, name, classes in self.progress_bar_order:
            count = status_counts.get(status, 0)
            if count:
                raw = floor(1000.0 * (float(count) / float(have_data_count)))
                percent = '%0.1f' % (raw / 10.0)
            else:
                percent = 0
            data_counts_list.append((name, classes, count, percent))
        ctx['data_counts'] = data_counts_list
        no_data_count = status_counts.get(FeaturePage.STATUS_NO_DATA, 0)
        other_count = total - have_data_count - no_data_count
        ctx['status_counts'] = {
            'total': total,
            'data': have_data_count,
            'no_data': no_data_count,
            'other': other_count
        }

        return ctx


class FeaturePageCreateView(CreateView):
    model = FeaturePage
    template_name = 'mdn/feature_page_form.html'
    fields = ['url', 'feature']

    def get_initial(self):
        initial = self.initial.copy()
        url = self.request.GET.get('url')
        if url:
            initial['url'] = url
        return initial

    def form_valid(self, form):
        """Start the parsing process on submission."""
        redirect = super(FeaturePageCreateView, self).form_valid(form)
        assert self.object and self.object.id
        self.object.reset()
        start_crawl.delay(self.object.id)
        return redirect


class FeaturePageDetailView(DetailView):
    model = FeaturePage
    template_name = 'mdn/feature_page_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super(FeaturePageDetailView, self).get_context_data(**kwargs)
        ctx['request'] = self.request
        return ctx


class FeaturePageJSONView(BaseDetailView):
    model = FeaturePage

    def render_to_response(self, context):
        obj = context['object']
        return JsonResponse(obj.data)


class GetFormView(FormView):
    """A FormView that also submits with GET and URL parameters."""

    def get(self, request, *args, **kwargs):
        get_params = self.request.GET.dict()
        if get_params:
            return self.post(request, *args, **kwargs)
        else:
            return super(GetFormView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(GetFormView, self).get_form_kwargs()
        get_params = self.request.GET.dict()
        if self.request.method == 'GET' and get_params:
            kwargs.setdefault('data', {}).update(get_params)
        return kwargs


class SlugSearchForm(forms.Form):
    slug = forms.SlugField(label='Feature Slug')

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        try:
            fp = FeaturePage.objects.get(feature__slug=slug)
        except FeaturePage.DoesNotExist:
            raise forms.ValidationError('No Feature with this slug.')
        else:
            self.feature_id = fp.feature_id
            return slug


class FeaturePageSlugSearch(GetFormView):
    """Search for an importer page by Feature slug."""

    form_class = SlugSearchForm
    template_name = 'mdn/feature_page_form.html'

    def form_valid(self, form):
        slug = form.cleaned_data['slug']
        fp = FeaturePage.objects.get(feature__slug=slug)
        next_url = reverse('feature_page_detail', kwargs={'pk': fp.pk})
        return HttpResponseRedirect(next_url)

    def get_context_data(self, **kwargs):
        ctx = super(FeaturePageSlugSearch, self).get_context_data(**kwargs)
        ctx['action'] = 'Search by Feature Slug'
        ctx['action_url'] = reverse('feature_page_slug_search')
        ctx['method'] = 'get'
        return ctx


class URLSearchForm(forms.Form):
    url = forms.URLField(
        label='MDN URL',
        widget=forms.URLInput(attrs={'placeholder': DEV_PREFIX + '...'}))

    def clean_url(self):
        data = self.cleaned_data['url']
        scheme, netloc, path, params, query, fragment = urlparse(data)
        if '%' not in path:
            path = quote(path)
        cleaned = urlunparse((scheme, netloc, path, '', '', ''))
        validate_mdn_url(cleaned)
        return cleaned


class FeaturePageURLSearch(GetFormView):
    """Search for a MDN URI via GET."""

    form_class = URLSearchForm
    template_name = 'mdn/feature_page_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(FeaturePageURLSearch, self).get_context_data(**kwargs)
        ctx['action'] = 'Search by URL'
        ctx['action_url'] = reverse('feature_page_url_search')
        ctx['method'] = 'get'
        return ctx

    def form_valid(self, form):
        url = form.cleaned_data['url']
        next_url = None

        # Try loading a specific page
        try:
            fp = FeaturePage.objects.get(url=url)
        except FeaturePage.DoesNotExist:
            pass
        else:
            next_url = reverse('feature_page_detail', kwargs={'pk': fp.pk})

        # Try filtering by a subset of pages
        if (not next_url) and url.startswith(DEV_PREFIX):
            suburl = url
            while suburl.endswith('/'):
                suburl = suburl[:-1]
            fp_start = FeaturePage.objects.filter(url__startswith=suburl)
            if fp_start.exists():
                topic = suburl.replace(DEV_PREFIX, '', 1)
                next_url = reverse('feature_page_list')
                next_url += '?topic={}'.format(topic)

        # Page does not exist
        if not next_url:
            msg = 'URL "%s" has not been scraped.' % url
            if can_create(self.request.user):
                msg += ' Scrape it?'
                messages.add_message(self.request, messages.INFO, msg)
                next_url = reverse('feature_page_create') + '?url=' + url
            else:
                messages.add_message(self.request, messages.INFO, msg)
                next_url = reverse('feature_page_list')

        return HttpResponseRedirect(next_url)


class FeaturePageReParse(UpdateView):
    model = FeaturePage
    fields = []
    template_name = 'mdn/feature_page_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(FeaturePageReParse, self).get_context_data(**kwargs)
        pk = ctx['object'].pk
        ctx['action'] = 'Re-parse MDN Page'
        ctx['action_url'] = reverse(
            'feature_page_reparse', kwargs={'pk': pk})
        ctx['back_url'] = reverse(
            'feature_page_detail', kwargs={'pk': pk})
        ctx['back'] = 'Back to Details'
        return ctx

    def form_valid(self, form):
        """Start reparsing the page on submission."""
        redirect = super(FeaturePageReParse, self).form_valid(form)
        assert self.object and self.object.id
        self.object.status = FeaturePage.STATUS_PARSING
        self.object.reset_data()
        self.object.save()
        messages.add_message(
            self.request, messages.INFO, 'Re-parsed the page.')
        parse_page.delay(self.object.id)
        return redirect


class FeaturePageReset(UpdateView):
    model = FeaturePage
    fields = []
    template_name = 'mdn/feature_page_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(FeaturePageReset, self).get_context_data(**kwargs)
        pk = ctx['object'].pk
        ctx['action'] = 'Reset MDN Page'
        ctx['action_url'] = reverse(
            'feature_page_reset', kwargs={'pk': pk})
        ctx['back_url'] = reverse(
            'feature_page_detail', kwargs={'pk': pk})
        ctx['back'] = 'Back to Details'
        return ctx

    def form_valid(self, form):
        """Start refetching the page on submission."""
        redirect = super(FeaturePageReset, self).form_valid(form)
        assert self.object and self.object.id
        self.object.reset()
        messages.add_message(
            self.request, messages.INFO,
            'Resetting cached MDN pages, re-parsing.')
        start_crawl.delay(self.object.id)
        return redirect


class IssuesSummary(TemplateView):
    template_name = 'mdn/issues_summary.html'

    def get_context_data(self, **kwargs):
        ctx = super(IssuesSummary, self).get_context_data(**kwargs)
        issues = []
        for slug, (severity_num, brief, lengthy) in ISSUES.items():
            severity = SEVERITIES[severity_num]
            target = Issue.objects.filter(slug=slug)
            count = target.count()
            raw = target.values_list('page__url', 'page_id')
            examples = sorted(set(
                (url.replace(DEV_PREFIX, '', 1), pid) for url, pid in raw))
            issues.append((count, slug, severity, brief, examples[:5]))
        issues.sort(reverse=True)
        ctx['total_issues'] = Issue.objects.count()
        ctx['issues'] = issues
        return ctx


class IssuesDetail(TemplateView):
    template_name = 'mdn/issues_detail.html'
    headers_by_issue = {
        'exception': (),
        'failed_download': (),
        'footnote_missing': (),
        'footnote_multiple': (),
        'footnote_unused': (),
        'kumascript_wrong_args': ('kumascript', 'arg_spec', 'scope'),
        'missing_attribute': ('node_type', 'ident'),
        'skipped_h3': (),
        'tag_dropped': ('tag', 'scope'),
        'unexpected_attribute': ('node_type', 'ident', 'value', 'expected'),
        'unexpected_kumascript': ('kumascript', 'scope'),
        'unknown_kumascript': ('kumascript', 'scope'),
        'unknown_version': ('browser_name', 'version'),
    }

    def get_context_data(self, **kwargs):
        ctx = super(IssuesDetail, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        issues = Issue.objects.filter(slug=slug)
        if issues.exists():
            ctx['sample_issue'] = issues.first()
            ctx['count'] = issues.count()
            pages = Counter()
            raw_details = []
            raw_headers = set()
            for url, pid, raw_params in issues.values_list(
                    'page__url', 'page_id', 'params'):
                mdn_slug = url.replace(DEV_PREFIX, '', 1)
                pages[(mdn_slug, pid)] += 1
                params = loads(raw_params)
                raw_details.append((mdn_slug, pid, params))
                raw_headers.update(set(params.keys()))
            headers = list(
                self.headers_by_issue.get(slug, sorted(raw_headers)))
            if headers:
                details = []
                for mdn_slug, pid, params in raw_details:
                    details.append(
                        [mdn_slug, pid] +
                        [params.get(header, '') for header in headers])
                ctx['headers'] = ['Page'] + headers
                ctx['details'] = details
            else:
                ctx['headers'] = []
                ctx['details'] = []
            ctx['pages'] = pages
        else:
            ctx['sample_issue'] = None
            ctx['count'] = 0
            ctx['headers'] = []
            ctx['details'] = []
            ctx['pages'] = {}
        ctx['slug'] = slug
        return ctx


def csv_response(filename, headers, rows):
    """Return a CSV-for-download response."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="{}"'.format(filename))
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def issues_summary_csv(request):
    raw_counts = Issue.objects.values('slug').annotate(total=Count('slug'))
    counts = [(raw['total'], raw['slug']) for raw in raw_counts]
    counts.sort(reverse=True)
    return csv_response('import_issue_counts.csv', ['Count', 'Issue'], counts)


def issues_detail_csv(request, slug):
    issues = Issue.objects.filter(slug=slug).select_related('page__url')
    raw_headers = set()
    lines = []
    raw_params = []
    for issue in issues:
        full_url = request.build_absolute_uri(
            reverse('feature_page_detail', kwargs={'pk': issue.page_id}))
        mdn_slug = issue.page.url.replace(DEV_PREFIX, '', 1)
        lines.append([mdn_slug, full_url, issue.start, issue.end])
        raw_params.append(issue.params)
        raw_headers.update(set(issue.params.keys()))
    headers = sorted(raw_headers)
    for line, params in zip(lines, raw_params):
        line.extend([params.get(header, '') for header in headers])

    filename = 'import_issues_for_{}.csv'.format(slug)
    csv_headers = (
        ['MDN Slug', 'Import URL', 'Source Start', 'Source End'] + headers)
    return csv_response(filename, csv_headers, lines)


feature_page_create = user_passes_test(can_create)(
    FeaturePageCreateView.as_view())
feature_page_detail = FeaturePageDetailView.as_view()
feature_page_json = FeaturePageJSONView.as_view()
feature_page_slug_search = FeaturePageSlugSearch.as_view()
feature_page_url_search = FeaturePageURLSearch.as_view()
feature_page_list = FeaturePageListView.as_view()
feature_page_reset = user_passes_test(can_refresh)(
    FeaturePageReset.as_view())
feature_page_reparse = user_passes_test(can_refresh)(
    FeaturePageReParse.as_view())
issues_summary = IssuesSummary.as_view()
issues_detail = IssuesDetail.as_view()
