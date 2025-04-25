from scripts.broker import getBroker
from scripts.customer import getCustomer
from scripts.goods_return import getGoodsReturn
from scripts.item_wise_customer_report import getItemWiseSales
from scripts.purchase_invoice import getPurchaseInvoice
from scripts.purchase_pending_order import getPurchasePendingOrder
from scripts.sales_invoice import getSalesInvoice
from scripts.sales_order_details import getSalesOrderDetails
from scripts.sales_pending_order import getSalesPendingOrder
from scripts.stock import getStock
from scripts.stock_valuation import getStockValuation


def run_all_reports():
    results = {
        "Purchase Pending Order": getPurchasePendingOrder(),
        "Sales Invoice": getSalesInvoice(),
        "Sales Order Details": getSalesOrderDetails(),
        "Sales Pending Order": getSalesPendingOrder(),
        "Stock": getStock(),
        "Broker": getBroker(),
        "Customer": getCustomer(),
        "Goods Return": getGoodsReturn(),
        "Item Wise Customer": getItemWiseSales(),
        "Purchase Invoice": getPurchaseInvoice(),
        "Stock Valuation": getStockValuation()
    }

    print("\n========== Report Download Results ==========")
    for report, result in results.items():
        print(f"{report}: {result}")

