# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.template.loader import render_to_string, get_template
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView, ListView, RedirectView, View, FormView
from django.views.generic.edit import ModelFormMixin
from django.views.decorators.csrf import csrf_exempt

from dal import autocomplete
from dateutil.tz import tzutc
from datetime import datetime, date, timedelta
from xhtml2pdf import pisa
from cgi import escape

from poimap.models import Area

from .models import Line, Stop, Route, Service, Customer, Ticket, Order 
from .models import Bus, Order, Connection, PartnerSearch, Travel
from .api_views import compute_timetable
from .forms import SearchServiceForm, CustomerCreationForm


import json
import time
import csv
import payplug
import qrcode
import string
import random
import base64
import cStringIO as StringIO


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
        travel["travellers"].append({
            "first_name" : "",
            "last_name" : "",
            "seats" : {}
        })
    
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
                "go" : json.dumps(go).replace("'", "\\'"),
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

        if(len(request.session["travels"])):
            return RedirectView.get(self, request, *args, **kwargs)
        request.session.flush()
        return redirect("/")


@method_decorator(csrf_exempt, name='dispatch')
class TransportationCartSaveTravellers(View):
    def post(self, request, *args, **kwargs):
        if "travels" in request.session:
            travels = request.session["travels"]
            
            data = request.POST
            fieldname = data["fieldname"]
            travel_id = int(data["travelId"])
            traveller_id = int(data["travellerId"])
            way = data["way"]
            value = data["value"]

            if fieldname == "seat_nb":
                service_slug = data["serviceSlug"]
                travels[travel_id][way]["travellers"][traveller_id]["seats"][service_slug] = value
            else:
                travels[travel_id][way]["travellers"][traveller_id][fieldname] = value
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
                cancel_url = self.request.build_absolute_uri(reverse('transportation-checkout'))
                return_url = self.request.build_absolute_uri(reverse('transportation-checkout-confirmation', args=(order.num,)))
                payment_data = {
                    'amount': int(total * 100),
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
        if "utm_source" in self.request.session:
            source = self.request.session["utm_source"]
        else:
            source = "internal"
        self.order = Order.objects.create(num=id_gen(), customer=customer, source=source)
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
                    try:
                        seat = traveller["seats"][service["service_slug"]]
                    except:
                        seat = None

                    Connection.objects.create(
                        ticket=ticket,
                        service=Service.objects.get(slug=service["service_slug"]),
                        from_stop=Stop.objects.get(name=service["stops"][0]),
                        to_stop=Stop.objects.get(name=service["stops"][1]),
                        seat=seat
                    )
            if "return" in travel and travel["return"]:
                for traveller in travel["return"]["travellers"]:
                    ticket = Ticket.objects.create(
                        num=id_gen(),
                        order=self.order,
                        traveller_first_name=traveller["first_name"],
                        traveller_last_name=traveller["last_name"],
                        departure_stop=Stop.objects.get(id=travel["return"]["timeslots"][0]["stop_id"]),
                        arrival_stop=Stop.objects.get(id=travel["return"]["timeslots"][-1]["stop_id"]),
                        departure_hour=datetime.strptime(travel["return"]["timeslots"][0]["hour"], "%H:%M").time(),
                        arrival_hour=datetime.strptime(travel["return"]["timeslots"][-1]["hour"], "%H:%M").time(),
                        date=datetime.strptime(travel["return"]['departure_date'], "%d/%m/%y"),
                        price=travel["return"]['travel_unit_price'],
                    )
                    for service in travel["return"]["services"]:
                        try:
                            seat = traveller["seats"][service["service_slug"]]
                        except:
                            seat = None
                        
                        Connection.objects.create(
                            ticket=ticket,
                            service=Service.objects.get(slug=service["service_slug"]),
                            from_stop=Stop.objects.get(name=service["stops"][0]),
                            to_stop=Stop.objects.get(name=service["stops"][1]),
                            seat=seat
                        )

        return FormView.form_valid(self, form)
   
    def get_success_url(self):
        return reverse("transportation-checkout-payment", kwargs={"order_num" : self.order.num})


class TransportationCheckoutConfirmation(DetailView):
    model = Order
    template_name = "transportation/checkout_confirmation.html"
    slug_field = 'num'
    slug_url_kwarg = 'order_num'

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if not order.paid_at:
            order.paid_at = datetime.now().replace(tzinfo=tzutc())
            order.save()
            subject = render_to_string("transportation/email/order_confirmation_email_subject.html", {"order" : order})
            message = render_to_string("transportation/email/order_confirmation_email_message.html", {"order" : order, "request" : request})
            from_email = settings.EMAIL_NOTIFICATION_FROM_EMAIL
            recipients = [order.customer.email]
            try:
                recipients.extend(settings.EMAIL_NOTIFICATION_CC_EMAIL)
            except:
                #In case of these is no CC email
                pass
            for to in recipients:
                msg = EmailMultiAlternatives(subject, message, from_email, [to])
                msg.attach_alternative(message, "text/html")
                for ticket in order.ticket_set.all():
                    context = {
                        "ticket" : ticket
                    }
                    validation_url = request.build_absolute_uri(reverse('ticket-validation', args=(ticket.num,)))
                    img = qrcode.make(validation_url)
                    buffer = StringIO.StringIO()
                    img.save(buffer, "PNG")
                    img_str = base64.b64encode(buffer.getvalue())
                    context["qrcode"] = img_str
                    context["today"] = datetime.today()
                    template = get_template("transportation/ticket.html")
                    ticket_html = template.render(context)
                    ticket_pdf = StringIO.StringIO()
                    pisa.pisaDocument(StringIO.StringIO(ticket_html.encode("UTF-*")), ticket_pdf)
                    msg.attach("Ticket #%s.pdf" % ticket.num, ticket_pdf.getvalue(), 'application/pdf')
                template = get_template("transportation/order_invoice.html")
                order_html = template.render({"order" : order})
                order_pdf = StringIO.StringIO()
                pisa.pisaDocument(StringIO.StringIO(order_html.encode("UTF-*")), order_pdf)
                msg.attach("Commande #%s.pdf" % order.num, order_pdf.getvalue(), 'application/pdf')
                msg.send()
        if "travels" in request.session:
            request.session["travels"] = []
        request.session.flush()
        return DetailView.get(self, request, *args, **kwargs)


class TransportationTicketRecovery(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'transportation/ticket_recovery.html', {})

    def post(self, request, *args, **kwargs):
        recovery_mail = request.POST.get("recovery_email", None)
        if recovery_mail:
            try:
                customer = Customer.objects.get(email=recovery_mail)
            except Customer.DoesNotExist:
                return render(request, 'transportation/ticket_recovery.html', {"error" : "unknown_customer"})
            
            tickets = Ticket.objects.filter(order__customer__email=recovery_mail, date__gte=datetime.now(), order__paid_at__isnull=False)
            if tickets.count() == 0:
                return render(request, 'transportation/ticket_recovery.html', {"error" : "no_ticket"})
            subject = render_to_string("transportation/email/tickets_recovery_email_subject.html")
            message = render_to_string("transportation/email/tickets_recovery_email_message.html", {"tickets" : tickets, "request" : request})
            from_email = settings.EMAIL_NOTIFICATION_FROM_EMAIL
            to = customer.email
            msg = EmailMultiAlternatives(subject, message, from_email, [to])
            msg.attach_alternative(message, "text/html")
            for ticket in tickets:
                context = {
                    "ticket" : ticket
                }
                validation_url = request.build_absolute_uri(reverse('ticket-validation', args=(ticket.num,)))
                img = qrcode.make(validation_url)
                buffer = StringIO.StringIO()
                img.save(buffer, "PNG")
                img_str = base64.b64encode(buffer.getvalue())
                context["qrcode"] = img_str
                context["today"] = datetime.today()
                template = get_template("transportation/ticket.html")
                ticket_html = template.render(context)
                ticket_pdf = StringIO.StringIO()
                pisa.pisaDocument(StringIO.StringIO(ticket_html.encode("UTF-*")), ticket_pdf)
                msg.attach("Ticket #%s.pdf" % ticket.num, ticket_pdf.getvalue(), 'application/pdf')
            msg.send()
            return render(request, 'transportation/ticket_recovery.html', {"success" : True})


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


class DriverView(View):

    def get_context_data(self):
        context = {}
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, 'transportation/driver.html', context)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        return redirect("driver")
        

class DriverDailyService(TemplateView):
    login_url = "driver"
    redirect_field_name = 'redirect_to'
    template_name = "transportation/driver_daily_service.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        service_name = self.request.GET.get("service_name", None)
        travel_date = self.request.GET.get("travel_date", None)

        if service_name and travel_date:
            service = Service.objects.get(name=service_name)
            travel_date = datetime.strptime(travel_date, "%d/%m/%y")
            connections = Connection.objects.filter(ticket__date=travel_date, 
                                                    ticket__order__paid_at__isnull=False,
                                                    service=service)

            context.update({
                "service" : service,
                "tickets" : Ticket.objects.filter(id__in=connections.values_list("ticket", flat=True)),
                "travel_date" : travel_date,
            })
        
        return context


class  DriverDailyServicePrintView(LoginRequiredMixin, PDFRenderingMixin, DriverDailyService):
    login_url = "driver"
    redirect_field_name = 'redirect_to'
    pass


class ServiceTimeTableView(TemplateView):
    template_name = "transportation/timetable.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        route_id = self.request.GET.get('route_id', None)
        freq_re = self.request.GET.get('freq_re', None)
        date = self.request.GET.get('date', None)
        context["route"] = Route.objects.get(id=route_id)
        context["timetable"] = compute_timetable(route_id, freq_re=freq_re, date=date)
        return context

class  ServiceTimeTablePrintView(PDFRenderingMixin, ServiceTimeTableView):
    pass


class TransportationPartnerView(View):

    def get(self, request, *args, **kwargs):
        departure_stop_slug = kwargs.get("departure_stop_slug")
        arrival_stop_slug = kwargs.get("arrival_stop_slug")
        
        departure_stop = None
        arrival_stop = None
        travel_date = None
        source = ""

        today = date.today()
        tomorrow = today + timedelta(days=1)
        tomorrow = tomorrow.strftime("%Y-%m-%d_00_00_00")

        try:
            departure_stop = Stop.objects.get(slug=departure_stop_slug)
            arrival_stop = Stop.objects.get(slug=arrival_stop_slug)
            travel_date = request.GET.get("dateAller", tomorrow)  # 2018-07-04_00_00_00
            travel_date = datetime.strptime(travel_date, "%Y-%m-%d_%H_%M_%S")
            source = request.GET.get("utm_source", "external")
            PartnerSearch.objects.create(
                departure_stop=departure_stop,
                arrival_stop=arrival_stop,
                travel_date=travel_date,
                partner=source
            )
            request.session["utm_source"] = source
        except:
            return redirect("/")

        form = SearchServiceForm(initial={
            "departure" : departure_stop,
            "arrival" : arrival_stop,
            "departure_date" : travel_date,
            "source" : source
        })

        return render(request, 'transportation/partner.html', {"search_form" : form})

def stops_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stops.csv"'

    writer = csv.writer(response)
    writer.writerow(["Stop name", "Stop slug", "Latitude", "Longitude"])
    for stop in Stop.objects.all():
        writer.writerow([stop.name.encode("utf-8"),stop.slug, stop.coords["lat"], stop.coords["lng"]])

    return response

def travels_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="travels.csv"'

    writer = csv.writer(response)
    writer.writerow(["Departure stop name", "Departure stop slug", "Arrival stop name", "Arrival stop slug", "Deeplink"])
    # for travel in Travel.objects.all():
    #     writer.writerow([travel.stop1.name.encode("utf-8"), travel.stop1.slug, travel.stop2.name.encode("utf-8"), travel.stop2.slug])
    for stop1 in Stop.objects.all():
        for stop2 in Stop.objects.all():
            if stop1 != stop2:
                site = get_current_site(request)
                deeplink = "https://"+site.domain+reverse("deeplink-partner", args=[stop1.slug, stop2.slug])
                writer.writerow([stop1.name.encode("utf-8"), stop1.slug, stop2.name.encode("utf-8"), stop2.slug, deeplink])

    return response




