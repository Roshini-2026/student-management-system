from .views import COMPANY_NAME


def company(request):
    return {"company_name": COMPANY_NAME}