from django import forms
from .models import *

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemMaster
        fields  = ['item_name', 'item_code','price', 'status']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields  = ['supplier_name', 'mobile_no', 'address', 'status']

class PurchaseMasterForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all())  # Define supplier field correctly

    def __init__(self, *args, **kwargs):
        super(PurchaseMasterForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].empty_label = "Select supplier"

    class Meta:
        model = PurchaseMaster
        fields = ['invoice_no', 'invoice_date', 'supplier', 'total_amount']   

class PurchaseDetailForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=ItemMaster.objects.all())  # Define item field correctly

    def __init__(self, *args, **kwargs):
        super(PurchaseDetailForm, self).__init__(*args, **kwargs)
        self.fields['item'].empty_label = "Select Item"

    class Meta:
        model = PurchaseDetail
        fields = ['item', 'quantity', 'amount', 'price']

class SaleMasterForm(forms.ModelForm):
    class Meta:
        model=SaleMaster
        fields=['customer_name','number','total_amount']

class SaleDetailsForm(forms.ModelForm):
    forms.ModelChoiceField(queryset=ItemMaster.objects.all())
    
    def __init__(self, *args, **kwargs):
        super(SaleDetailsForm, self).__init__(*args, **kwargs)
        self.fields['item'].empty_label = "Select Item"

    
    class Meta:
        model=SaleDetails
        fields=['item','qty','price','amount']