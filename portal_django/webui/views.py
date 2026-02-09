import os
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, OrderLineForm, OrderActionForm

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _get_headers(request):
    token = request.session.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _api_request(request, method, path, payload=None):
    url = f"{API_BASE_URL}{path}"
    headers = _get_headers(request)
    response = requests.request(method, url, json=payload, headers=headers, timeout=10)
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = response.text
        raise ValueError(f"{response.status_code}: {detail}")
    return response.json()


@require_http_methods(["GET", "POST"])
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            payload = {
                "email": form.cleaned_data["email"],
                "password": form.cleaned_data["password"],
            }
            data = _api_request(request, "POST", "/auth/login", payload)
            request.session["access_token"] = data["access_token"]
            return redirect("dashboard")
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, "webui/login.html", {"form": form})


def logout_view(request):
    request.session.flush()
    return redirect("login")


def _require_login(request):
    if not request.session.get("access_token"):
        return redirect("login")
    return None


def dashboard_view(request):
    redirect_response = _require_login(request)
    if redirect_response:
        return redirect_response
    return render(request, "webui/dashboard.html")


def items_view(request):
    redirect_response = _require_login(request)
    if redirect_response:
        return redirect_response
    try:
        items = _api_request(request, "GET", "/items")
        stocks = {}
        for item in items:
            stock = _api_request(request, "GET", f"/stock/{item['id']}")
            stocks[item["id"]] = stock["quantity"]
        return render(request, "webui/items.html", {"items": items, "stocks": stocks})
    except ValueError as exc:
        messages.error(request, str(exc))
        return render(request, "webui/items.html", {"items": [], "stocks": {}})


@require_http_methods(["GET", "POST"])
def orders_view(request):
    redirect_response = _require_login(request)
    if redirect_response:
        return redirect_response
    if request.method == "POST":
        if "create_order" in request.POST:
            try:
                _api_request(request, "POST", "/orders")
                messages.success(request, "Order created.")
            except ValueError as exc:
                messages.error(request, str(exc))
        elif "add_line" in request.POST:
            form = OrderLineForm(request.POST)
            if form.is_valid():
                payload = {"item_id": form.cleaned_data["item_id"], "qty": form.cleaned_data["qty"]}
                try:
                    _api_request(request, "POST", f"/orders/{form.cleaned_data['order_id']}/lines", payload)
                    messages.success(request, "Line added.")
                except ValueError as exc:
                    messages.error(request, str(exc))
        elif "order_action" in request.POST:
            form = OrderActionForm(request.POST)
            if form.is_valid():
                action = form.cleaned_data["action"]
                try:
                    _api_request(request, "POST", f"/orders/{form.cleaned_data['order_id']}/{action}")
                    messages.success(request, f"Order {action}ed.")
                except ValueError as exc:
                    messages.error(request, str(exc))

    try:
        orders = _api_request(request, "GET", "/orders")
    except ValueError as exc:
        messages.error(request, str(exc))
        orders = []
    return render(
        request,
        "webui/orders.html",
        {
            "orders": orders,
            "line_form": OrderLineForm(),
            "action_form": OrderActionForm(),
        },
    )
