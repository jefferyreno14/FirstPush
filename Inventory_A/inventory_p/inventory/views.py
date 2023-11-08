from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
import datetime
from decimal import Decimal
import json
from django.shortcuts import *
from .forms import * 
from .models import *
from django.db import connection
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Sum



# Create your views here.

def home(request):
    return render(request,'home.html')

def display_items(request):
    items = ItemMaster.objects.all()
    context = {
        'items': items,
        'header': 'Item Master'
    }
    return render(request, 'index.html', context)

def display_suppliers(request):
    supplier = Supplier.objects.all()
    context = {
        'supplier': supplier,
        'header': 'Supplier Master'
    }
    return render(request, 'supplier.html', context)

def add_update_delete_items(request, action, pk=None):
    if action == "add":
        if request.method == "POST":
            form = ItemForm(request.POST)
            if form.is_valid():
                ItemMaster.objects.create(
                    item_name=request.POST['item_name'],
                    item_code=request.POST['item_code'],
                    price=request.POST['price'],
                    status=request.POST['status'],
                )
                return redirect('display_items')
        else: 
            form = ItemForm()  # Create an empty form for GET requests
        return render(request, 'add_item.html', {'form': form})  # Render the form for GET and POST requests

    # The rest of your code for "update" and "delete" actions...


    elif action == "update":
        item = get_object_or_404(ItemMaster, pk=pk)
        if request.method == "POST":
            form = ItemForm(request.POST, instance=item)
            if form.is_valid():
                ItemMaster.objects.filter(pk=pk).update(
                    item_name=request.POST['item_name'],
                    item_code=request.POST['item_code'],
                    price=request.POST['price'],
                    status=request.POST['status'],
                )
                return redirect('display_items')
        else:
            form = ItemForm(instance=item)
        return render(request, 'update_item.html', {'form': form})

    elif action == "delete":
        item = get_object_or_404(ItemMaster, pk=pk)
        item.delete()
        return redirect('display_items')

    # Adding a default response for unsupported actions
    else:
        return HttpResponse("Invalid action")
    
def add_update_delete_supplier(request, action, pk=None):
    if action == "add":
        if request.method == "POST":
            form = SupplierForm(request.POST)
            if form.is_valid():
                Supplier.objects.create(
                    supplier_name=request.POST['supplier_name'],
                    mobile_no=request.POST['mobile_no'],
                    address=request.POST['address'],
                )
                return redirect('display_suppliers')
        else:
            form = SupplierForm()  # Create an empty form for GET requests
        return render(request, 'add_supplier.html', {'form': form})  # Render the form for GET and POST requests

    # The rest of your code for "update" and "delete" actions...


    elif action == "update":
        item = get_object_or_404(Supplier, pk=str(pk))
        if request.method == "POST":
            form = SupplierForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                return redirect('display_suppliers')
        else:
            form = SupplierForm(instance=item)
            return render(request, 'update_supplier.html', {'form': form})

    elif action == "delete":
    
        pk = int(pk)

        sql = "DELETE FROM tbl_supplier_master WHERE supplier_id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(sql, [pk])

        return redirect('display_suppliers')

    # Adding a default response for unsupported actions
    else:
        return HttpResponse("Invalid action")

############# PURCHASE ########################


def get_item_price(request):
    item_id_str = request.GET.get('item')
    
    # Check if item_id_str is empty or not a valid integer
    if not item_id_str:
        return JsonResponse({'price': 0})
    
    try:
        item_id = int(item_id_str)
    except ValueError:
        return JsonResponse({'price': 0})
    
    try:
        item = ItemMaster.objects.get(id=item_id)
        price = item.price
        id = item.id
        data = {'price': price}
        return JsonResponse(data)
    except ItemMaster.DoesNotExist:
        return JsonResponse({'price': 0})

# To get or fetch deatils of a particular item we need to call this function....

def get_item_details(request):
    if request.method == 'GET':
        item_id_str = request.GET.get('item')

        try:
            item_id = int(item_id_str)  # Convert the item_id_str to an integer
        except (ValueError, TypeError):
            # Handle the case where 'item' is not a valid integer or is None
            return JsonResponse({'error': 'Invalid item ID'}, status=400)

        try:
            purchase_detail_list = PurchaseDetail.objects.filter(
                item__id=item_id)
            total_purchase_quantity = 0
            for purchase_details in purchase_detail_list:
                total_purchase_quantity += purchase_details.quantity
                price = purchase_details.price
            print(total_purchase_quantity)
            print(price)

            sale_detail_list=SaleDetails.objects.filter(item__id=item_id)
            total_sale_quantity = 0
            for sale_detail in sale_detail_list:
                total_sale_quantity += sale_detail.qty
            
            total_quantity=total_purchase_quantity-total_sale_quantity
            print(total_quantity)

            # Construct a JSON response with the item details
            data = {
                'price': price + 2000,
                'quantity': total_quantity,
            }

            return JsonResponse(data)
        except PurchaseDetail.DoesNotExist:
            # Handle the case where the item doesn't exist
            return JsonResponse({'error': 'Item not found'}, status=404)




def purchase_items(request):
    form = PurchaseMasterForm()
    if request.method == 'POST':
        form = PurchaseMasterForm(request.POST)
        if form.is_valid():
            try:
                # Generate invoice number
                invoice_date = request.POST['invoice_date']
                invoice_no = request.POST['invoice_no']

                # Get supplier and total amount from the form
                supplier_id = request.POST['supplier']
                # print(supplier_id)
                total_amount = request.POST['total_amount']

                if PurchaseMaster.objects.filter(invoice_no=invoice_no).exists():
                    form.add_error('invoice_no', 'Invoice number already exists.')
                    raise ValueError('Invoice number already exists.')

                # Continue with the purchase process if the invoice number is unique
                supplier_id = request.POST['supplier']
                total_amount = request.POST['total_amount']

                # Create a new PurchaseMaster instance with the provided data
                purchase_master = PurchaseMaster.objects.create(
                    invoice_no=invoice_no,
                    invoice_date=invoice_date,
                    total_amount=total_amount,
                    supplier=Supplier.objects.get(id=supplier_id)
                )

                # Parse the JSON item list
                item_list_json = request.POST.get('item_list')
                item_list = json.loads(item_list_json)

                # Create PurchaseDetail objects for each item in the list
                for item_data in item_list:
                    item_id = item_data['item_id']
                    quantity = item_data['quantity']
                    price = item_data['price']
                    amount = item_data['amount']

                    PurchaseDetail.objects.create(
                        item=ItemMaster.objects.get(id=item_id),
                        quantity=quantity,
                        price=price,
                        amount=amount,
                        purchase_master=purchase_master #retuning ID from purchase detals because it is foreign key.
                    )

                # Construct the SQL query for retrieving purchase details
                purchase_details_query = """
                SELECT
                    pm.total_amount AS total_purchase_amount,
                    pm.invoice_date AS invoice_date,
                    pm.invoice_no AS invoice_no,
                    sm.supplier_name AS supplier_name,
                    sm.mobile_no,
                    sm.address,
                    im.item_name,
                    pd.quantity,
                    pd.price,
                    pd.amount
                FROM tbl_purchase_mstr AS pm
                JOIN tbl_supplier_mstr AS sm ON pm.supplier_id = sm.id
                JOIN tbl_purchase_details AS pd ON pm.id = pd.purchase_master_id
                JOIN tbl_item_mstr AS im ON pd.item_id = im.id
                WHERE pm.invoice_no = %s;
                """

                # Execute the SQL query
                with connection.cursor() as cursor:
                    cursor.execute(purchase_details_query, [invoice_no])
                    purchase_result = cursor.fetchall()
                    print(type(purchase_result))

                return render(request, 'purchase_details_template.html', {'purchase_details': purchase_result})

            except Exception as e:
                # Handle the exception and return an appropriate error response
                error_message = f"Error: {str(e)}"
                return HttpResponse(error_message)  # You can customize the error message

        else:
            # Form validation failed, return errors as JsonResponse
            errors = form.errors
            return JsonResponse({'errors': errors})

    else:
        form = PurchaseMasterForm()
        form1 = PurchaseDetailForm()
        return render(request, 'purchase_item_form.html', {'form': form, 'form1': form1})

#############sale########################

# To auto generate invoice number for sale


def generate_invoice_sale():
    prefix = "SSPL-SALE"  # Replace with your desired prefix
    last_invoice = SaleMaster.objects.filter(
        invoice_no__startswith=f"{prefix}-"
    ).order_by('-invoice_no').first()

    if last_invoice is None:
        return f"{prefix}-001"

    last_invoice_number = int(last_invoice.invoice_no.split('-')[2])
    next_invoice_number = last_invoice_number + 1

    return f"{prefix}-{next_invoice_number:03d}"


def sale_items(request):
    if request.method == 'POST':
        form = SaleDetailsForm(request.POST)
        form1 = SaleMasterForm(request.POST)

        if form1.is_valid():
            # Generate invoice number
            invoice_no = generate_invoice_sale()

            # Create a SaleMaster instance
            saleMaster = SaleMaster.objects.create(
                invoice_no=invoice_no,
                customer_name=request.POST['customer_name'],
                number=request.POST['number'],
                total_amount=request.POST['total_amount'],
            )

            # Parse the JSON item list
            item_list_json = request.POST.get('item_list')
            item_list = json.loads(item_list_json)

            # Create SaleDetails objects for each item in the list
            for item_data in item_list:
                item_id = item_data['item_id']
                qty = item_data['quantity']
                price = item_data['price']
                amount = item_data['amount']

                SaleDetails.objects.create(
                    item=ItemMaster.objects.get(id=item_id),
                    qty=qty,
                    price=price,
                    amount=amount,
                    sale_mstr=saleMaster
                )
            #print(item_id)
            # Now, retrieve sale details for the current saleMaster
            sale_details = SaleDetails.objects.filter(sale_mstr=saleMaster)

            # Construct the SQL query to retrieve additional details
            sale_details_query = """
              SELECT
                sm.total_amount AS total_sale_amount,
                sm.invoice_date AS invoice_date,
                sm.invoice_no AS invoice_no,
                sm.customer_name AS customer_name,
                sm.number AS customer_number,
                im.item_name,
                sd.qty,
                sd.price,
                sd.amount
            FROM tbl_sale_mstr AS sm
            JOIN tbl_sale_details AS sd ON sm.id = sd.sale_mstr_id
            JOIN tbl_item_mstr AS im ON sd.item_id = im.id
            WHERE sm.invoice_no = %s;
            """

            with connection.cursor() as cursor:
                cursor.execute(sale_details_query, [invoice_no])
                sale_result = cursor.fetchall()

            return render(request, 'sale_details_table.html', {'sale_details': sale_result})

    else:
        form = SaleDetailsForm()
        form1 = SaleMasterForm()

    return render(request, 'sale_items_form.html', {'form': form, 'form1': form1})


##################### Report Date waise #######################

def datewise_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    # Define the SQL queries
    purchase_query = """
        SELECT
            im.item_name,
            SUM(pd.quantity) AS purchase_quantity,
            SUM(pd.amount) AS purchase_amount
        FROM tbl_purchase_mstr AS pm
        JOIN tbl_purchase_details AS pd ON pm.id = pd.purchase_master_id
        JOIN tbl_item_mstr AS im ON pd.item_id = im.id
        WHERE
            pm.invoice_date BETWEEN %s AND %s
        GROUP BY
            im.item_name;
        """

    sale_query = """
        SELECT
            im.item_name,
            SUM(sd.qty) AS sale_quantity,
            SUM(sd.amount) AS sale_amount
        FROM tbl_sale_mstr AS sm
        JOIN tbl_sale_details AS sd ON sm.id = sd.sale_mstr_id
        JOIN tbl_item_mstr AS im ON sd.item_id = im.id
        WHERE
            sm.invoice_date BETWEEN %s AND %s
        GROUP BY
            im.item_name;
    """

    # Execute the purchase SQL query
    with connection.cursor() as cursor:
        cursor.execute(purchase_query, [start_date, end_date])
        purchase_result = cursor.fetchall()

    # Execute the sale SQL query
    with connection.cursor() as cursor:
        cursor.execute(sale_query, [start_date, end_date])
        sale_result = cursor.fetchall()

    # Process the purchase result
    purchase_data = [{'item_name': row[0], 'purchase_quantity': row[1],
                       'purchase_amount': row[2]} for row in purchase_result]
    print(purchase_data)
    
    # Process the sale result
    sale_data = [{'item_name': row[0], 'sale_quantity': row[1], 'sale_amount': row[2]} for row in sale_result]
    print(sale_data)

    datewise_report_data = {}
    for purchase_entry in purchase_data:
        item_name = purchase_entry['item_name']
        purchase_quantity = purchase_entry['purchase_quantity']
        purchase_amount = purchase_entry['purchase_amount']
        if item_name not in datewise_report_data:
            datewise_report_data[item_name] = {'purchase_quantity': 0, 'purchase_amount': Decimal('0.00'),
                                               'sale_quantity': 0, 'sale_amount': Decimal('0.00')}
        datewise_report_data[item_name]['purchase_quantity'] += purchase_quantity
        datewise_report_data[item_name]['purchase_amount'] += purchase_amount

    for sale_entry in sale_data:
        item_name = sale_entry['item_name']
        sale_quantity = sale_entry['sale_quantity']
        sale_amount = sale_entry['sale_amount']
        if item_name not in datewise_report_data:
            datewise_report_data[item_name] = {'purchase_quantity': 0, 'purchase_amount': Decimal('0.00'),
                                               'sale_quantity': 0, 'sale_amount': Decimal('0.00')}
        datewise_report_data[item_name]['sale_quantity'] += sale_quantity
        datewise_report_data[item_name]['sale_amount'] += sale_amount

    # Calculate stock quantity and profit/loss
    for item_name, data in datewise_report_data.items():
        data['stock_quantity'] = data['purchase_quantity'] - data['sale_quantity']
        data['profit_loss'] = data['sale_amount'] - data['purchase_amount']

    return render(request, 'date_wise_report.html', {'datewise_report_data': datewise_report_data})


# Function to generate report for all dates

def datewise_report_all_data(request):
    # Define the SQL queries (remove the date filter)
    purchase_query = """
        SELECT
            im.item_name,
            SUM(pd.quantity) AS purchase_quantity,
            SUM(pd.amount) AS purchase_amount
        FROM tbl_purchase_mstr AS pm
        JOIN tbl_purchase_details AS pd ON pm.id = pd.purchase_master_id
        JOIN tbl_item_mstr AS im ON pd.item_id = im.id
        GROUP BY
            im.item_name;
    """

    sale_query = """
        SELECT
            im.item_name,
            SUM(sd.qty) AS sale_quantity,
            SUM(sd.amount) AS sale_amount
        FROM tbl_sale_mstr AS sm
        JOIN tbl_sale_details AS sd ON sm.id = sd.sale_mstr_id
        JOIN tbl_item_mstr AS im ON sd.item_id = im.id
        GROUP BY
            im.item_name;
    """

    # Execute the purchase SQL query
    with connection.cursor() as cursor:
        cursor.execute(purchase_query)
        purchase_result = cursor.fetchall()

    # Execute the sale SQL query
    with connection.cursor() as cursor:
        cursor.execute(sale_query)
        sale_result = cursor.fetchall()

    # Process the purchase result
    purchase_data = [{'item_name': row[0], 'purchase_quantity': row[1],
                      'purchase_amount': row[2]} for row in purchase_result]

    # Process the sale result
    sale_data = [{'item_name': row[0], 'sale_quantity': row[1], 'sale_amount': row[2]} for row in sale_result]

    datewise_report_data = {}
    for purchase_entry in purchase_data:
        item_name = purchase_entry['item_name']
        purchase_quantity = purchase_entry['purchase_quantity']
        purchase_amount = purchase_entry['purchase_amount']
        if item_name not in datewise_report_data:
            datewise_report_data[item_name] = {'purchase_quantity': 0, 'purchase_amount': Decimal('0.00'),
                                               'sale_quantity': 0, 'sale_amount': Decimal('0.00')}
        datewise_report_data[item_name]['purchase_quantity'] += purchase_quantity
        datewise_report_data[item_name]['purchase_amount'] += purchase_amount

    for sale_entry in sale_data:
        item_name = sale_entry['item_name']
        sale_quantity = sale_entry['sale_quantity']
        sale_amount = sale_entry['sale_amount']
        if item_name not in datewise_report_data:
            datewise_report_data[item_name] = {'purchase_quantity': 0, 'purchase_amount': Decimal('0.00'),
                                               'sale_quantity': 0, 'sale_amount': Decimal('0.00')}
        datewise_report_data[item_name]['sale_quantity'] += sale_quantity
        datewise_report_data[item_name]['sale_amount'] += sale_amount

    # Calculate stock quantity and profit/loss
    for item_name, data in datewise_report_data.items():
        data['stock_quantity'] = data['purchase_quantity'] - data['sale_quantity']
        data['profit_loss'] = data['sale_amount'] - data['purchase_amount']

    return render(request, 'date_wise_report.html', {'datewise_report_data': datewise_report_data})


# Function to handle date-wise filtering and retrieve purchase details


def date_wise_purchase(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if start_date_str and end_date_str:  # Check if both start and end dates are provided
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                # Handle invalid date format or other errors
                return render(request, 'error.html')  

            # Query the database to get data within the date range
            det = PurchaseMaster.objects.filter(invoice_date__range=[start_date, end_date])

            return render(request, 'date_wise_purchase.html', {'det': det})
        else:
            # Handle the case where either start or end date is missing
            return render(request, 'error.html')  
    else:
        # Handle GET request when the page initially loads
        det = PurchaseMaster.objects.all()
        return render(request, 'date_wise_purchase.html', {'det': det})




def date_wise_sale(request):
    if request.method == "POST":
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                return render(request, 'error.html')
            
            # Use the __range lookup to filter by date range
            det = SaleMaster.objects.filter(invoice_date__range=[start_date, end_date])
            return render(request, 'date_wise_sale.html', {'det': det})
        else:
            return render(request, 'error.html')
    else:
        det = SaleMaster.objects.all()
        return render(request, "date_wise_sale.html", {"det": det})



def view_invoice(request, invoice_no):
    try:
        purchase = PurchaseMaster.objects.get(invoice_no=invoice_no)
        purchase_details = PurchaseDetail.objects.filter(purchase_master=purchase)
    except PurchaseMaster.DoesNotExist:
        # Handle the case where the invoice does not exist
        return render(request, 'invoice_not_found.html')  # You can create this template

    context = {
        'purchase': purchase,
        'purchase_details': purchase_details,  # Pass the purchase details to the template
    }
    return render(request, 'view_invoice.html', context)


def view_invoice2(request, invoice_no):
    try:
        sale = SaleMaster.objects.get(invoice_no=invoice_no)
        sale_details = SaleDetails.objects.filter(sale_mstr=sale)
    except SaleMaster.DoesNotExist:
        # Handle the case where the invoice does not exist
        return render(request, 'invoice_not_found.html')  # You can create this template

    context = {
        'sale': sale,
       'sale_details': sale_details,  # Pass the sale details to the template
    }
    return render(request, 'view_invoice2.html', context)


from .models import ItemMaster

def current_stock(request):
    item_names = ['All'] + list(ItemMaster.objects.values_list('item_name', flat=True).distinct())
    
    selected_item = request.POST.get('selected_item')
    
    # Calculate total purchase quantity
    if selected_item == 'All':
        purchase_quantity = PurchaseDetail.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        sale_quantity = SaleDetails.objects.aggregate(Sum('qty'))['qty__sum'] or 0
    else:
        purchase_quantity = PurchaseDetail.objects.filter(item__item_name=selected_item).aggregate(Sum('quantity'))['quantity__sum'] or 0
        sale_quantity = SaleDetails.objects.filter(item__item_name=selected_item).aggregate(Sum('qty'))['qty__sum'] or 0

    current_stock = purchase_quantity - sale_quantity

    items = []

    if selected_item == 'All':
        all_items = ItemMaster.objects.all()
        for item in all_items:
            purchase_quantity = PurchaseDetail.objects.filter(item=item).aggregate(Sum('quantity'))['quantity__sum'] or 0
            sale_quantity = SaleDetails.objects.filter(item=item).aggregate(Sum('qty'))['qty__sum'] or 0
            current_stock = purchase_quantity - sale_quantity

            items.append({
                'item_name': item.item_name,
                'purchase_quantity': purchase_quantity,
                'sale_quantity': sale_quantity,
                'current_stock': current_stock,
            })
    else:
        items.append({
            'item_name': selected_item,
            'purchase_quantity': purchase_quantity,
            'sale_quantity': sale_quantity,
            'current_stock': current_stock,
        })

    context = {
        'item_names': item_names,
        'items': items,
    }

    return render(request, 'current_stock.html', context)
