from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class OrderCreateForm(forms.Form):
    create_order = forms.BooleanField(required=False, initial=True)

class OrderLineForm(forms.Form):
    order_id = forms.IntegerField()
    item_id = forms.IntegerField()
    qty = forms.IntegerField(min_value=1)

class OrderActionForm(forms.Form):
    order_id = forms.IntegerField()
    action = forms.ChoiceField(choices=[("submit", "submit"), ("fulfill", "fulfill")])
