from scripts.account_payable import getAccountPayable
from scripts.account_receivable import getAccountReceivable
from scripts.account_receivable_frono import getAccountReceivableFrono
from scripts.broker import getBroker
from scripts.customer import getCustomer
from scripts.goods_return import getGoodsReturn
from scripts.item_wise_customer_report import getItemWiseSales
from scripts.purchase_invoice import getPurchaseInvoice
from scripts.purchase_pending_order import getPurchasePendingOrderThis
from scripts.purchase_pending_order2 import getPurchasePendingOrderPrevious
from scripts.sales_invoice import getSalesInvoicePrevious, getSalesInvoiceThis
from scripts.sales_order_details import getSalesOrderDetailsTillDate
from scripts.sales_pending_order import getSalesPendingOrderThis
from scripts.stock_valuation import getStockValuation
from scripts.stock import getStock


def run_once_a_day_reports(location):
    print(f"\n📍 Running ONCE A DAY reports for: {location.upper()}")
    reports = {
        "Purchase Pending Order This": getPurchasePendingOrderThis(location),
        "Purchase Pending Order Previous": getPurchasePendingOrderPrevious(location),
        "Purchase Invoice": getPurchaseInvoice(location),
        "Goods Return": getGoodsReturn(location),
        "Account Payable": getAccountPayable(location),
        "Account Receivable": getAccountReceivable(location),
        # "Account Receivable Frono": getAccountReceivableFrono(location),  # Uncomment if needed
    }
    for report, result in reports.items():
        print(f"{location.upper()} | {report}: {result}")

def run_once_in_2_days_reports(location):
    print(f"\n📍 Running ONCE IN 2 DAYS reports for: {location.upper()}")
    reports = {
        "Broker": getBroker(location),
        "Customer": getCustomer(location),
    }
    for report, result in reports.items():
        print(f"{location.upper()} | {report}: {result}")

def run_every_4_hours_reports(location):
    print(f"\n📍 Running EVERY 4 HOURS reports for: {location.upper()}")
    reports = {
        "Sales Invoice This": getSalesInvoiceThis(location),
        "Sales Invoice Previous": getSalesInvoicePrevious(location),
        "Sales Order Details Till Date": getSalesOrderDetailsTillDate(location),
        "Sales Pending Order This": getSalesPendingOrderThis(location),
        "Stock Valuation": getStockValuation(location),
    }
    for report, result in reports.items():
        print(f"{location.upper()} | {report}: {result}")

def run_every_2_hours_reports(location):
    print(f"\n📍 Running EVERY 2 HOURS reports for: {location.upper()}")
    reports = {
        "Stock": getStock(location),
        "Item Wise Customer": getItemWiseSales(location),
    }
    for report, result in reports.items():
        print(f"{location.upper()} | {report}: {result}")



if __name__ == "__main__":
    for location in ["kolkata", "surat"]:
        run_once_a_day_reports(location)
        run_once_in_2_days_reports(location)
        run_every_4_hours_reports(location)
        run_every_2_hours_reports(location)


