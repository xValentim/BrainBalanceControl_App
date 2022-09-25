from django.shortcuts import render, redirect
from .models import *
from bbc_glue.data_client import *

def index(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if customer_id not in ['427.282.572-59', '595.080.896-84']:
            return redirect('index')
        else:
            if customer_id == '427.282.572-59':
                pfm_da_valentina = PFM(customerId='427.282.572-59', customer_data=other_customer_data, initialInvestment=0)
                ip_da_valentina = InitPayment(pfm_da_valentina)
                credit_engine_da_valentina = CreditEngine(pfm_da_valentina)
                all_accounts = pfm_da_valentina.allMyAccounts
                return render(request, 'glue/home.html', {'banks': all_accounts, 'investment': pfm_da_valentina.investment})
                
            if customer_id == '595.080.896-84':
                pfm_da_valentina = PFM(customerId='595.080.896-84', customer_data=customer_data, initialInvestment=0)
                ip_da_valentina = InitPayment(pfm_da_valentina)
                credit_engine_da_valentina = CreditEngine(pfm_da_valentina)
                all_accounts = pfm_da_valentina.allMyAccounts
                return redirect('home')
    else:
        return render(request, 'glue/index.html')

def home(request):
    pfm_da_valentina = PFM(customerId='595.080.896-84', customer_data=customer_data, initialInvestment=0)
    ip_da_valentina = InitPayment(pfm_da_valentina)
    credit_engine_da_valentina = CreditEngine(pfm_da_valentina)
    return render(request, 'glue/home.html', {'banks': pfm_da_valentina.allMyAccounts, 'investment': pfm_da_valentina.investment})

def home_1(request):
    pfm_da_valentina = PFM(customerId='595.080.896-84')
    ip_da_valentina = InitPayment(pfm=pfm_da_valentina)
    credit_engine_da_valentina = CreditEngine(pfm=pfm_da_valentina)
    ip_da_valentina.toRealocateAccounts()
    return render(request, 'glue/bbc_1.html', {'banks': pfm_da_valentina.allMyAccounts, 'investment': pfm_da_valentina.investment})