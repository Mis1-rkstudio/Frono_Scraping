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


def run_all_reports():
    for location in ["kolkata", "surat"]:
        print(f"\n📍 Running automation for: {location.upper()}")

        results = {
            "Purchase Pending Order This": getPurchasePendingOrderThis(location),
            "Purchase Pending Order Previous": getPurchasePendingOrderPrevious(location),
            "Sales Invoice This": getSalesInvoiceThis(location),
            "Sales Invoice Previous": getSalesInvoicePrevious(location),
            "Sales Order Details Till Date": getSalesOrderDetailsTillDate(location),
            "Sales Pending Order This": getSalesPendingOrderThis(location),
            "Broker": getBroker(location),
            "Customer": getCustomer(location),
            "Goods Return": getGoodsReturn(location),
            "Item Wise Customer": getItemWiseSales(location),
            "Purchase Invoice": getPurchaseInvoice(location),
            "Stock Valuation": getStockValuation(location),
            "Account Payable": getAccountPayable(location),
            "Account Receivable": getAccountReceivable(location),
            "Account Receivable Frono": getAccountReceivableFrono(location),
            "Stock": getStock(location),
        }

        print("\n========== Report Download Results ==========")
        for report, result in results.items():
            print(f"{location.upper()} | {report}: {result}")
        print("=============================================")


