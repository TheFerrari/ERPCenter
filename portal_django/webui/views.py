import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import (
    AddLineForm,
    CreateOrderForm,
    FulfillOrderForm,
    LoginForm,
    SubmitOrderForm,
)


def _api_headers(request: HttpRequest) -> dict:
    token = request.session.get("api_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _api_url(path: str) -> str:
    return f"{settings.API_BASE_URL}{path}"


def _handle_api_error(request: HttpRequest, response: requests.Response) -> None:
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = response.text
    messages.error(request, f"API error {response.status_code}: {detail}")


def _require_login(request: HttpRequest) -> bool:
    if not request.session.get("api_token"):
        messages.error(request, "Please log in first.")
        return False
    return True


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        response = requests.post(
            _api_url("/auth/login"), json=form.cleaned_data, timeout=5
        )
        if response.ok:
            request.session["api_token"] = response.json()["access_token"]
            return redirect("dashboard")
        _handle_api_error(request, response)
    return render(request, "webui/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    request.session.flush()
    return redirect("login")


def dashboard(request: HttpRequest) -> HttpResponse:
    if not _require_login(request):
        return redirect("login")
    return render(request, "webui/dashboard.html")


def items_view(request: HttpRequest) -> HttpResponse:
    if not _require_login(request):
        return redirect("login")
    response = requests.get(
        _api_url("/items"), headers=_api_headers(request), timeout=5
    )
    items = []
    if response.ok:
        items = response.json()
        for item in items:
            stock_response = requests.get(
                _api_url(f"/stock/{item['id']}"),
                headers=_api_headers(request),
                timeout=5,
            )
            if stock_response.ok:
                item["stock"] = stock_response.json()
    else:
        _handle_api_error(request, response)
    return render(request, "webui/items.html", {"items": items})


@require_http_methods(["GET", "POST"])
def orders_view(request: HttpRequest) -> HttpResponse:
    if not _require_login(request):
        return redirect("login")
    create_form = CreateOrderForm(request.POST or None)
    add_line_form = AddLineForm(request.POST or None, prefix="line")
    submit_form = SubmitOrderForm(request.POST or None, prefix="submit")
    fulfill_form = FulfillOrderForm(request.POST or None, prefix="fulfill")

    if request.method == "POST":
        if "create_order" in request.POST and create_form.is_valid():
            response = requests.post(
                _api_url("/orders"),
                headers=_api_headers(request),
                json=create_form.cleaned_data,
                timeout=5,
            )
            if response.ok:
                messages.success(request, "Order created.")
                return redirect("orders")
            _handle_api_error(request, response)

        if "add_line" in request.POST and add_line_form.is_valid():
            order_id = add_line_form.cleaned_data["order_id"]
            payload = {
                "item_id": add_line_form.cleaned_data["item_id"],
                "qty": add_line_form.cleaned_data["qty"],
            }
            response = requests.post(
                _api_url(f"/orders/{order_id}/lines"),
                headers=_api_headers(request),
                json=payload,
                timeout=5,
            )
            if response.ok:
                messages.success(request, "Order line added.")
                return redirect("orders")
            _handle_api_error(request, response)

        if "submit_order" in request.POST and submit_form.is_valid():
            order_id = submit_form.cleaned_data["order_id"]
            response = requests.post(
                _api_url(f"/orders/{order_id}/submit"),
                headers=_api_headers(request),
                timeout=5,
            )
            if response.ok:
                messages.success(request, "Order submitted.")
                return redirect("orders")
            _handle_api_error(request, response)

        if "fulfill_order" in request.POST and fulfill_form.is_valid():
            order_id = fulfill_form.cleaned_data["order_id"]
            response = requests.post(
                _api_url(f"/orders/{order_id}/fulfill"),
                headers=_api_headers(request),
                timeout=5,
            )
            if response.ok:
                messages.success(request, "Order fulfilled.")
                return redirect("orders")
            _handle_api_error(request, response)

    response = requests.get(
        _api_url("/orders"), headers=_api_headers(request), timeout=5
    )
    orders = []
    if response.ok:
        orders = response.json()
    else:
        _handle_api_error(request, response)

    return render(
        request,
        "webui/orders.html",
        {
            "orders": orders,
            "create_form": create_form,
            "add_line_form": add_line_form,
            "submit_form": submit_form,
            "fulfill_form": fulfill_form,
        },
    )
