from flask import Flask, jsonify
from stock_valuation import getStockValuation

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    result = getStockValuation()
    return jsonify({"status": result})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
