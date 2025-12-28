# api/add-asset.py
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from supabase_client import db
    from yfinance_helper import get_current_value
except ImportError:
    from utils.supabase_client import db
    from utils.yfinance_helper import get_current_value

def handler(request):
    """
    Manejador para /api/add-asset - EQUIVALENTE a app.route('/add-asset') en Flask
    """
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({})
        }
    
    try:
        # Obtener datos del request
        if hasattr(request, 'body'):
            data = json.loads(request.body)
        else:
            # Para testing
            data = request.get_json() if hasattr(request, 'get_json') else {}
        
        # MISMA validación que Flask (líneas 86-92)
        required_fields = ["isin", "asset_name", "purchase_value", "amount"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({
                        "success": False,
                        "error": f"Campo requerido faltante: {field}"
                    })
                }
        
        isin = data["isin"]
        asset_name = data["asset_name"]
        purchase_value = float(data["purchase_value"])
        amount = float(data["amount"])
        
        print(f"➕ Añadiendo activo: {asset_name} ({isin})")
        
        # Obtener precio actual
        current_value = get_current_value(isin)
        
        # Calcular ganancia/pérdida (MISMO cálculo que Flask línea 96)
        profit_loss_percentage = ((current_value - purchase_value) / purchase_value) * 100
        
        # Calcular dinero total (MISMO cálculo que Flask línea 97)
        total_money = amount + (amount * profit_loss_percentage / 100)
        
        # Preparar datos (MISMA estructura que Flask)
        new_investment = {
            "isin": isin,
            "asset_name": asset_name,
            "purchase_value": purchase_value,
            "amount": amount,
            "current_value": current_value,
            "total_money": total_money,
            "profit_loss_percentage": profit_loss_percentage,
            "investment_type": data.get("investment_type", "Otros"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insertar en Supabase
        result = db.add_investment(new_investment)
        
        if result:
            response_data = {
                "success": True,
                "message": f"Activo '{asset_name}' añadido correctamente",
                "data": result[0] if isinstance(result, list) and result else result
            }
            
            return {
                "statusCode": 201,
                "headers": headers,
                "body": json.dumps(response_data, default=str, ensure_ascii=False)
            }
        else:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "success": False,
                    "error": "Error al insertar en la base de datos"
                })
            }
        
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": "JSON inválido"
            })
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "message": "Error al añadir activo"
            })
        }

# Test local
if __name__ == "__main__":
    print("🧪 Testeando API /api/add-asset...")
    
    test_data = {
        "isin": "TSLA",
        "asset_name": "Tesla Inc. (Test)",
        "purchase_value": 250.50,
        "amount": 1000.00,
        "investment_type": "Acciones"
    }
    
    class MockRequest:
        method = "POST"
        body = json.dumps(test_data)
        
        def get_json(self):
            return json.loads(self.body)
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 201:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"📝 Mensaje: {data['message']}")
    else:
        print(f"❌ Error: {result['body']}")