from flask import Flask, jsonify
from Sales.invoice import getSalesInvoiceData
from goods_return import getGoodsReturn
from inventory.stock import getStockData
from item_wise_customer_report import getItemWiseSales
from masters.broker import getBrokerData
from masters.customer import getCustomerData
from purchase.invoice import getPurchaseInvoiceData
from purchase_pending_order import getPurchasePendingOrder
from sales_order_details import getSalesOrderDetails
from sales_pending_order import getSalesPendingOrder
from stock_valuation import getStockValuation

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    stock_valuation = getStockValuation()
    goods_return = getGoodsReturn()
    item_wise_sales = getItemWiseSales()
    sales_pending_order = getSalesPendingOrder()
    sales_order_details = getSalesOrderDetails()
    purchase_pending_order = getPurchasePendingOrder()
    customer_data = getCustomerData()
    broker_data = getBrokerData()
    stock_data = getStockData()
    purchase_invoice_data = getPurchaseInvoiceData()
    sales_invoice_data = getSalesInvoiceData()
    return jsonify({"status": "success", "data": {
        "stock_valuation": stock_valuation,
        "goods_return": goods_return,
        "item_wise_sales": item_wise_sales,
        "sales_pending_order": sales_pending_order,
        "sales_order_details": sales_order_details,
        "purchase_pending_order": purchase_pending_order,
        "customer_data": customer_data,
        "broker_data": broker_data,
        "stock_data": stock_data,
        "purchase_invoice_data": purchase_invoice_data,
        "sales_invoice_data": sales_invoice_data
    }})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
