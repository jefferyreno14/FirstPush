from django.urls import re_path, path
from .views import *

urlpatterns = [

    path('',home, name='home_page' ),
    path('date_wise_purchase/',date_wise_purchase, name='date_wise_purchase' ),
    path('date_wise_sale/',date_wise_sale, name='date_wise_sale' ),
    path('current_stock/',current_stock, name='current_stock' ),

    path('date_wise_sale/',date_wise_sale, name='date_wise_sale' ),
    re_path(r'^display_items$', display_items, name="display_items"),
    re_path(r'^supplier_name$', display_suppliers, name="display_suppliers"),

    # re_path(r'^submit_purchase$', submit_purchase, name="submit_purchase"),

    re_path(r'^add_update_delete_items/(?P<action>\w+)/(?P<pk>(.*)+|)$', add_update_delete_items, name="a_u_d_i"),
    re_path(r'^add_update_delete_supplier/(?P<action>\w+)/(?P<pk>(.*)+|)$', add_update_delete_supplier, name="a_u_d_s"),
    
    re_path(r'^purchase-items$', purchase_items, name='purchase_items'),
    
    path('get_item_price/', get_item_price, name='get_item_price'),
    path('get_item_details/', get_item_details, name='get_item_details'),
    
    path('sale-items/', sale_items, name='sale_items'),
    # path('get_purchase_details/', get_purchase_details, name='get_purchase_details'),

    path('datewise_report/', datewise_report, name='datewise_report'),

    path('datewise_report_all_data/', datewise_report_all_data, name='datewise_report_all_data'),


    path('view_invoice/<str:invoice_no>/', view_invoice, name='view_invoice'),
    path('view_invoice2/<str:invoice_no>/', view_invoice2, name='view_invoice2'),
]
   
