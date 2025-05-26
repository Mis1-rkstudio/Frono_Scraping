from account_payable import getAccountPayable
from account_receivable import getAccountReceivable
from account_receivable_frono import getAccountReceivableFrono
from broker import getBroker
from customer import getCustomer
from goods_return import getGoodsReturn
from item_wise_customer_report import getItemWiseSales
from purchase_invoice import getPurchaseInvoice
from purchase_pending_order import getPurchasePendingOrderThis
from purchase_pending_order2 import getPurchasePendingOrderPrevious
from sales_invoice import getSalesInvoice
from sales_order_details import getSalesOrderDetails
from sales_pending_order import getSalesPendingOrder
from stock import getStock
from stock_valuation import getStockValuation


def run_all_reports():
    for location in ["kolkata", "surat"]:
        print(f"\n📍 Running automation for: {location.upper()}")

        results = {
            "Purchase Pending Order": getPurchasePendingOrderThis(location),
            "Purchase Pending Order": getPurchasePendingOrderPrevious(location),
            "Sales Invoice": getSalesInvoice(location),
            "Sales Order Details": getSalesOrderDetails(location),
            "Sales Pending Order": getSalesPendingOrder(location),
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


