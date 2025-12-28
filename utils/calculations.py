# utils/calculations.py
def calculate_total_money(amount, profit_loss_percentage):
    """Calcula dinero total basado en cantidad y porcentaje de ganancia"""
    return amount + (amount * profit_loss_percentage / 100)

def format_currency(value):
    """Formatea valor como moneda"""
    return f"{value:,.2f}€"

def calculate_category_totals(investments, category_field="investment_type"):
    """Calcula totales por categoría"""
    categories = {}
    for inv in investments:
        category = inv.get(category_field, "Sin categoría")
        if category not in categories:
            categories[category] = {
                "total_value": 0,
                "total_money": 0,
                "count": 0,
                "avg_profit_loss": 0
            }
        
        categories[category]["total_value"] += float(inv.get("purchase_value", 0))
        categories[category]["total_money"] += float(inv.get("total_money", 0))
        categories[category]["count"] += 1
    
    # Calcular promedio de ganancia/pérdida
    for category, data in categories.items():
        if data["count"] > 0 and data["total_value"] > 0:
            data["avg_profit_loss"] = (
                (data["total_money"] - data["total_value"]) / data["total_value"]
            ) * 100
    
    return categories