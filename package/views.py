from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from courier.models import Courier
from package.models import Package
from package_tracking.models import PackageTracking


class PackageForm(forms.Form):

    number = forms.CharField(label="Number:",
                           max_length=50,
                           widget=forms.TextInput(
                               attrs={
                                   'class': 'form-control round-form',
                                   'placeholder': "Enter the number package..."
                               }
                           ))

    couriers = Courier.object.all()
    courier = forms.ModelChoiceField(label="Courier:",
                           queryset=couriers,
                           widget=forms.Select(
                                attrs={
                                    'class': 'form-control'
                                }
                           ))


def main_view(request):
    if request.method == 'POST'
        form = PackageForm(request.POST)
        if form.is_valid():
            number_pack = form.cleaned_data['number']

            pack = Package.objects.get(number=number_pack)

            if pack:

            else:








