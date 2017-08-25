from datetime import date

from django.views import generic

from .models import Supplier, Product, Receipt
from dal import autocomplete


base_context = {
    'section_title': 'Mizer',
}


class YearListView(generic.ListView):
    template_name = 'mizer/year.html'
    context_object_name = 'receipts'
    
    def get_year(self):
        year = date.today().year
        if self.kwargs and self.kwargs['year']:
            year = self.kwargs['year']
        return int(year)

    def get_queryset(self):
        """Return all receipts from the current year."""
        return Receipt.objects.filter(date__gt=date(self.get_year() - 1, 12, 31),
                                      date__lt=date(self.get_year() + 1, 1, 1))

    def get_context_data(self, **kwargs):
        context = super(YearListView, self).get_context_data(**kwargs)
        context.update(base_context)

        context['year'] = self.get_year()
        if context['year'] != date.today().year:
            context['page_title'] = '%i Year in Review' % context['year']
        else:
            context['page_title'] = '%i Year-to-Date Summary' % context['year']

        context['total'] = {
            'purchases': 0,
            'fees': 0,
            'discounts': 0,
            'taxes': 0,
            'tips': 0,
            'final': 0
            }

        for receipt in self.get_queryset():
            context['total']['purchases'] += receipt.subtotal
            context['total']['fees'] += receipt.fee
            context['total']['discounts'] += receipt.discount
            context['total']['taxes'] += receipt.tax
            context['total']['tips'] += receipt.tip
            context['total']['final'] += receipt.total

        return context


class DashboardView(generic.TemplateView):
    template_name = 'mizer/home.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context.update(base_context)
        context['page_title'] = 'Dashboard'
        return context


class BaseAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset_by_model(self, model):
        results = model.objects.none()
        if self.request.user.is_authenticated():
            results = model.objects.all()
            if self.q:
                results = results.filter(name__icontains=self.q)
        return results


class SupplierAutocompleteView(BaseAutocompleteView):
    def get_result_label(self, item):
        return """
        <strong>%s</strong><br>%s
        """ % (item.name, item.locality())

    def get_queryset(self):
        return self.get_queryset_by_model(Supplier)


class ProductAutocompleteView(BaseAutocompleteView):
    def get_result_label(self, item):
        return "%s<strong>%s</strong><br>%s%s" % (
            item.image_html(),
            item.name,
            "%s<br>" % item.code if item.code else "",
            ", ".join([product_type.name for product_type in item.types.all()]))

    def get_queryset(self):
        return self.get_queryset_by_model(Product)