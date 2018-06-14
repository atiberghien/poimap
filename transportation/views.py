# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, DetailView, ListView, RedirectView, View, FormView
from django.views.generic.edit import ModelFormMixin
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, reverse
from django.http import HttpResponse
from django.conf import settings

from dal import autocomplete

from poimap.models import Area

from .models import Line, Stop, Route, Service, Customer, Ticket, Order, Bus, Order, Connection
from .forms import SearchServiceForm, CustomerCreationForm
import json
import time
from datetime import datetime

import payplug
import qrcode

import string
import random
import base64
import cStringIO as StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from cgi import escape


def id_gen(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for x in range(size)) + str(int(time.time()))


class MapView(TemplateView):
    template_name = 'transportation/map.html'

    def get_context_data(self):
        context = TemplateView.get_context_data(self)
        context["area"] = Area.objects.first()
        context["lines"] = Line.objects.all()
        return context


class LineDetailView(DetailView):
    model = Line

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        try:
            context["to_route"] = self.get_object().route_set.get(direction=1)
        except Route.DoesNotExist:
            context["to_route"] = None
        try:
            context["from_route"] = self.get_object().route_set.get(direction=2)
        except Route.DoesNotExist:
            context["from_route"] = None

        return context


class LineListView(ListView):
    model = Line


class StopListView(ListView):
    model = Stop
    queryset = Stop.objects.all().order_by('name')
    context_object_name = "stops"

class StopAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Stop.objects.all()
        departure = self.forwarded.get('departure', None)
        if departure:
            qs = qs.exclude(id=departure)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs.order_by('name')

def _init_travel_info(travel):
    travel["travellers"] = []
    for x in range(int(travel["traveler_count"])):
        travel["travellers"].append({})
    
    travel["services"] = []
    for timeslot in travel["timeslots"]:
        if "service_slug" in timeslot:
            travel["services"].append({
                "service_slug" : timeslot["service_slug"],
                "stops" : [timeslot["stop_name"]],
            })
        else:
            travel["services"][-1]["stops"].append(timeslot["stop_name"])


@method_decorator(csrf_exempt, name='dispatch')
class TransportationItinerary(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'transportation/itinerary_form.html', context)


    def post(self, request, *args, **kwargs):
        context = {}
        form_data = request.POST
        context["direction"] = 1
        if "go" in request.POST:
            go = json.loads(request.POST.get('go'))
            if "return" in request.POST or not go["arrival_date"]:
                ret_data = request.POST.get('return', None)
                ret = json.loads(ret_data) if ret_data else None
                travel = {
                    "go" : go,
                    "return" : ret,
                }
                
                _init_travel_info(travel["go"])

                if ret:
                    _init_travel_info(travel["return"])
                    travel["go"]["has_return"] = True
                    travel["return"]["is_return"] = True
                

                if "travels" in request.session:
                    travels = request.session["travels"]
                    travels.append(travel)
                    request.session["travels"] = travels
                else:
                    request.session["travels"] = [travel]
                return redirect("transportation-summary")
            form_data = {
                "departure" :  go["timeslots"][0]["stop_id"],
                "arrival" : go["timeslots"][-1]["stop_id"],
                "departure_hour" : go["timeslots"][0]["hour"],
                "arrival_hour" : go["timeslots"][-1]["hour"],
                "arrival_date" : go["arrival_date"],
                "departure_date" : go["departure_date"],
                "nb_passengers" : go["traveler_count"],
            }
            context.update({
                "go" : json.dumps(go),
                "direction" : 2,
            })

        form = SearchServiceForm(form_data)
        if form.is_valid():
            context.update(form.cleaned_data)

        context["search_form"] = form
        return render(request, 'transportation/itinerary.html', context)


class TransportationCart(TemplateView):
    template_name = "transportation/itinerary_summary.html"

    def dispatch(self, request, *args, **kwargs):
        if "travels" not in request.session:
            return redirect("transportation-itinerary")
        return TemplateView.dispatch(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context["travels"] = self.request.session["travels"]
        return context


class TransportationCartDeleteItem(RedirectView):
    pattern_name = "transportation-summary"

    def get(self, request, *args, **kwargs):
        delete_all = request.GET.get("delete_all", None)
        travel_id = request.GET.get("travel_id", None)
        travel_way = request.GET.get("travel_way", None)
        if delete_all:
            request.session["travels"] = []
            return RedirectView.get(self, request, *args, **kwargs)
        elif travel_id and travel_way:
            travels = request.session["travels"]
            if travel_way == "return":
                travels[int(travel_id)]["go"]["has_return"] = False
                travels[int(travel_id)]["return"] = {}
            elif travel_way == "go" and travels[int(travel_id)]["return"]:
                travels[int(travel_id)]["go"] = travels[int(travel_id)]["return"]
                travels[int(travel_id)]["go"]["has_return"] = False
                del travels[int(travel_id)]["go"]["is_return"]
                travels[int(travel_id)]["return"] = {}
            else:
                travels.pop(int(travel_id))

            request.session["travels"] = travels
            return RedirectView.get(self, request, *args, **kwargs)
        return redirect("transportation-itinerary")


@method_decorator(csrf_exempt, name='dispatch')
class TransportationCartSaveTravellers(View):
    def post(self, request, *args, **kwargs):
        if "travels" in request.session:
            travels = request.session["travels"]
            data = request.POST
            if data["fieldname"] == "seat_nb":
                if "seats" in travels[int(data["travelId"])][data["way"]]["travellers"][int(data["travellerId"])]:
                    travels[int(data["travelId"])][data["way"]]["travellers"][int(data["travellerId"])]["seats"][data["serviceSlug"]] = data["value"]
                else:
                    travels[int(data["travelId"])][data["way"]]["travellers"][int(data["travellerId"])]["seats"] = {
                        data["serviceSlug"] : data["value"]
                    }
            else:
                travels[int(data["travelId"])][data["way"]]["travellers"][int(data["travellerId"])][data["fieldname"]] = data["value"]
            request.session["travels"] = travels
        return HttpResponse()

class TransportationCheckout(FormView):
    template_name = "transportation/checkout.html"
    form_class = CustomerCreationForm

    def dispatch(self, request, *args, **kwargs):
        if "travels" not in request.session:
            return redirect("transportation-itinerary")
        self.order_num = kwargs.get("order_num", None)
        return FormView.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)
        context["travels"] = self.request.session["travels"]
        total = 0
        for travel in context["travels"]:
            total += float(travel["go"]["travel_price"])
            if "return" in travel and travel["return"]:
                total += float(travel["return"]["travel_price"])
        context["total"] = total

        if self.order_num:    
            try:
                order = Order.objects.get(num=self.order_num)
                payplug.set_secret_key(settings.PAYPLUG_KEY)
                order_amount = int(sum(list(order.ticket_set.values_list('price', flat=True))) * 100)
                cancel_url = self.request.build_absolute_uri(reverse('transportation-checkout'))
                return_url = self.request.build_absolute_uri(reverse('transportation-checkout-confirmation', args=(order.num,)))
                payment_data = {
                    'amount': order_amount,
                    'currency': 'EUR',
                    'customer': {
                        'first_name' : order.customer.first_name,
                        'last_name' : order.customer.last_name,
                        'email': order.customer.email
                    },
                    'hosted_payment': {
                        'return_url': return_url,
                        'cancel_url': cancel_url,
                    },
                    'metadata': {
                        'order_num': order.num,
                        'customer_id': order.customer.id,
                    },
                }
                payment = payplug.Payment.create(**payment_data)
                context["payment"] = payment
                context["order"] = order
            except Order.DoesNotExist:
                pass
        
        return context

    def form_valid(self, form):
        customer = form.save()
        self.order = Order.objects.create(num=id_gen(), customer=customer)
        travels = self.request.session["travels"]
        for travel in travels:
            for traveller in travel["go"]["travellers"]:
                ticket = Ticket.objects.create(
                    num=id_gen(),
                    order=self.order,
                    traveller_first_name=traveller["first_name"],
                    traveller_last_name=traveller["last_name"],
                    departure_stop=Stop.objects.get(id=travel["go"]["timeslots"][0]["stop_id"]),
                    arrival_stop=Stop.objects.get(id=travel["go"]["timeslots"][-1]["stop_id"]),
                    departure_hour=datetime.strptime(travel["go"]["timeslots"][0]["hour"], "%H:%M").time(),
                    arrival_hour=datetime.strptime(travel["go"]["timeslots"][-1]["hour"], "%H:%M").time(),
                    date=datetime.strptime(travel["go"]['departure_date'], "%d/%m/%y"),
                    price=travel["go"]['travel_unit_price'],
                )
                for service in travel["go"]["services"]:
                    Connection.objects.create(
                        ticket=ticket,
                        service=Service.objects.get(slug=service["service_slug"]),
                        from_stop=Stop.objects.get(name=service["stops"][0]),
                        to_stop=Stop.objects.get(name=service["stops"][1]),
                        seat=traveller["seats"][service["service_slug"]]
                    )
            if "return" in travel and travel["return"]:
                for traveller in travel["return"]["travellers"]:
                    ticket = Ticket.objects.create(
                        num=id_gen(),
                        order=self.order,
                        traveller_first_name=traveller["name"],
                        traveller_last_name=traveller["last_name"],
                        departure_stop=Stop.objects.get(id=travel["return"]["timeslots"][0]["stop_id"]),
                        arrival_stop=Stop.objects.get(id=travel["return"]["timeslots"][-1]["stop_id"]),
                        departure_hour=datetime.strptime(travel["return"]["timeslots"][0]["hour"], "%H:%M").time(),
                        arrival_hour=datetime.strptime(travel["return"]["timeslots"][-1]["hour"], "%H:%M").time(),
                        date=datetime.strptime(travel["return"]['departure_date'], "%d/%m/%y"),
                        price=travel["return"]['travel_unit_price'],
                    )
                    for service in travel["return"]["services"]:
                        Connection.objects.create(
                            ticket=ticket,
                            service=Service.objects.get(slug=service["service_slug"]),
                            from_stop=Stop.objects.get(name=service["stops"][0]),
                            to_stop=Stop.objects.get(name=service["stops"][1]),
                            seat=traveller["seats"][service["service_slug"]]
                        )

        return FormView.form_valid(self, form)
   
    def get_success_url(self):
        return reverse("transportation-checkout-payment", kwargs={"order_num" : self.order.num})


class TransportationCheckoutConfirmation(DetailView):
    model = Order
    template_name = "transportation/checkout_confirmation.html"
    slug_field = 'num'
    slug_url_kwarg = 'order_num'


class TransportationTicketRecovery(TemplateView):
    template_name = "transportation/ticket_recovery.html"


class PDFRenderingMixin(object):
     def render_to_response(self, context, **response_kwargs):
        template = get_template(self.template_name)
        html  = template.render(self.get_context_data())
        result = StringIO.StringIO()
        pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-*")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


class TransportationTicket(DetailView):
    model = Ticket
    template_name = "transportation/ticket.html"
    slug_field = 'num'
    slug_url_kwarg = 'num'

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        validation_url = self.request.build_absolute_uri(reverse('ticket-validation', args=(self.get_object().num,)))
        img = qrcode.make(validation_url)
        buffer = StringIO.StringIO()
        img.save(buffer, "PNG")
        img_str = base64.b64encode(buffer.getvalue())
        context["qrcode"] = img_str
        context["today"] = datetime.today()
        return context

class TransportationTicketPrintView(PDFRenderingMixin, TransportationTicket):
    pass


class TransportationTicketValidation(DetailView):
    model = Ticket
    template_name = "transportation/ticket_validation.html"
    slug_field = 'num'
    slug_url_kwarg = 'num'

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        ticket_valid = True
        if self.get_object().is_validated:
            ticket_valid = False
        else:
            self.object.is_validated = True
            self.object.save()
            
        context["ticket_valid"] = ticket_valid
        return context

class TransportationOrderInvoice(DetailView):
    model = Order
    template_name = "transportation/order_invoice.html"
    slug_field = 'num'
    slug_url_kwarg = 'num'

class  TransportationOrderInvoicePrintView(PDFRenderingMixin, TransportationOrderInvoice):
    pass


class TransportationFleet(ListView):
    model = Line
    template_name = "transportation/fleet_list.html"

class TransportationFleetVehicule(DetailView):
    model = Bus
    template_name = "transportation/fleet_vehicule_detail.html"
