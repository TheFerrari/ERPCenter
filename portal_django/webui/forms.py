from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateOrderForm(forms.Form):
    status = forms.ChoiceField(choices=[("draft", "draft")])


class AddLineForm(forms.Form):
    order_id = forms.IntegerField(min_value=1)
    item_id = forms.IntegerField(min_value=1)
    qty = forms.IntegerField(min_value=1)


class SubmitOrderForm(forms.Form):
    order_id = forms.IntegerField(min_value=1)


class FulfillOrderForm(forms.Form):
    order_id = forms.IntegerField(min_value=1)
