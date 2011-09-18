from datetime import date

from django.contrib import admin
from django.template import Context, Template
from .models import Registration

bill_body = Template('''\
Billing information for PyCon Finland 2011

Invoice number: {{ obj.invoice_number }}
Invoice date: {{ obj.bill_date|date }}
Invoice due date: {{ obj.due_date|date }}
Invoice to: {{ obj.name }}{% if company %}}
Company: {{ obj.company }}{% endif %}

Description:
------------------------------------------------------------------------
PyCon Finland participant fee: {{ obj.ticket_type|stringformat:"-9s" }}{{ obj.price|stringformat:"28s EUR"}}{% if obj.snailmail_bill %}
Paper bill: {{ "5 EUR"|stringformat:"60s"}}{% endif %}

------------------------------------------------------------------------
Total: {{ obj.total_price|stringformat:"61s EUR" }}


Please wire {{ obj.total_price }} EUR to following account:

Beneficary: Python Suomi ry
Bank: Aktia Oyj
IBAN: FI27 4055 0011 0236 33
BIC: HELSFIHH
Reference (viitenumero): {{ obj.reference_number }}

DUE DATE: {{ obj.due_date|date }}

Make sure to use the correct reference when paying.

If there's anything you'd like to ask about billing, don't hesitate to
contact hallitus@python.fi.


See you in the conference!

Cheers,
PyCon Finland organizers

-- 
------------------------------------------------------------------------
Python Suomi ry                                       hallitus@python.fi
c/o Jyrki Pulliainen                                    http://python.fi
Vartiokuja 1 E 37
20700 Turku, Finland
------------------------------------------------------------------------
''')


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'country',
                    'ticket_type', 'snailmail_bill',
                    'billed', 'paid', 'registered_timestamp')
    list_editable = ('paid',)
    list_filter = ('snailmail_bill', 'billed', 'paid', 'ticket_type', 'country')
    ordering = ['-registered_timestamp']
    actions = ['send_bill']

    def send_bill(self, request, queryset):
        for registration in queryset:
            if registration.billed:
                self.message_user(request, 'Some of the selected registrations '
                                  'have already been billed')
                return

            if registration.snailmail_bill:
                self.message_user(request, 'Some of the selected registrations '
                                  'shuld be billed via snail mail')

        for registration in queryset:
            registration.bill_date = date.today()
            email_body = bill_body.render(Context({'obj': registration}))
            email_subject = 'PyCon Finland invoice %s' % \
                registration.invoice_number

            print email_subject
            print email_body

    send_bill.short_description = ('Send an e-mail bill to the '
                                   'selected registrants')


admin.site.register(Registration, RegistrationAdmin)
