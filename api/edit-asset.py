# api/edit-asset.py
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
    Manejador para /api/edit-asset - EQUIVALENTE a app.route('/edit-asset') en Flask
    """
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({})
        }
    
    try:
        # Obtener datos
        if hasattr(request, 'body'):
            data = json.loads(request.body)
        else:
            data = request.get_json() if hasattr(request, 'get_json') else {}
        
        # MISMA validación que Flask (no hay validación explícita, pero necesitamos isin)
        if "isin" not in data:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "success": False,
                    "error": "Campo 'isin' requerido"
                })
            }
        
        isin = data["isin"]
        purchase_value = float(data.get("purchase_value", 0))
        amount = float(data.get("amount", 0))
        
        print(f"✏️ Editando activo: {isin}")
        
        # Buscar activo por ISIN (MISMA lógica que Flask)
        investments = db.get_all_investments()
        current_investment = None
        
        for inv in investments:
            if inv.get("isin") == isin:
                current_investment = inv
                break
        
        if not current_investment:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({
                    "success": False,
                    "error": f"Activo {isin} no encontrado"
                })
            }
        
        investment_id = current_investment["id"]
        
        # Si se proporcionan nuevos valores, recalcular
        if purchase_value > 0 or amount > 0:
            new_purchase = purchase_value if purchase_value > 0 else float(current_investment["purchase_value"])
            new_amount = amount if amount > 0 else float(current_investment["amount"])
            
            current_value = get_current_value(isin)
            profit_loss = ((current_value - new_purchase) / new_purchase) * 100 if new_purchase != 0 else 0
            total_money = new_amount + (new_amount * profit_loss / 100)
            
            update_data = {
                "purchase_value": new_purchase,
                "amount": new_amount,
                "current_value": current_value,
                "profit_loss_percentage": profit_loss,
                "total_money": total_money,
                "updated_at": datetime.now().isoformat()
            }
        else:
            # Solo actualizar precio
            current_value = get_current_value(isin)
            current_purchase = float(current_investment["purchase_value"])
            current_amount = float(current_investment["amount"])
            
            profit_loss = ((current_value - current_purchase) / current_purchase) * 100 if current_purchase != 0 else 0
            total_money = current_amount + (current_amount * profit_loss / 100)
            
            update_data = {
                "current_value": current_value,
                "profit_loss_percentage": profit_loss,
                "total_money": total_money,
                "updated_at": datetime.now().isoformat()
            }
        
        # Actualizar en Supabase
        result = db.update_investment(investment_id, update_data)
        
        if result:
            response_data = {
                "success": True,
                "message": f"Activo {isin} actualizado correctamente",
                "data": result[0] if isinstance(result, list) and result else result
            }
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(response_data, default=str, ensure_ascii=False)
            }
        else:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "success": False,
                    "error": "Error al actualizar"
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
                "message": "Error al editar activo"
            })
        }

# Test local
if __name__ == "__main__":
    print("🧪 Testeando API /api/edit-asset...")
    
    # Obtener un ISIN existente
    investments = db.get_all_investments()
    if investments:
        first_isin = investments[0]["isin"]
        
        test_data = {
            "isin": first_isin,
            "purchase_value": 200.00,
            "amount": 1500.00
        }
        
        class MockRequest:
            method = "POST"
            body = json.dumps(test_data)
            
            def get_json(self):
                return json.loads(self.body)
        
        result = handler(MockRequest())
        print(f"Status: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            data = json.loads(result['body'])
            print(f"✅ Success: {data['success']}")
            print(f"📝 Mensaje: {data['message']}")
        else:
            print(f"❌ Error: {result['body']}")
    else:
        print("❌ No hay activos para editar")