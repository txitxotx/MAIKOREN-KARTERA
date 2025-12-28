# api/update-assets.py
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
    Manejador para /api/update-assets - EQUIVALENTE a app.route('/update-assets') en Flask
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
        print(f"🔄 Iniciando actualización de activos...")
        
        # Obtener todas las inversiones
        investments = db.get_all_investments()
        
        if not investments:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "message": "No hay inversiones para actualizar",
                    "updated_count": 0
                })
            }
        
        updated_count = 0
        errors = []
        
        # Actualizar cada inversión (MISMA lógica que Flask)
        for inv in investments:
            investment_id = inv["id"]
            isin = inv["isin"]
            asset_name = inv["asset_name"]
            purchase_value = float(inv["purchase_value"])
            amount = float(inv["amount"])
            
            # MISMO filtro que Flask (línea 64)
            if "crowfounding" not in isin.lower() and "capital riesgo" not in isin.lower():
                print(f"  📈 Actualizando: {asset_name[:30]}...")
                
                try:
                    # Obtener precio actual
                    current_value = get_current_value(isin)
                    
                    # Calcular ganancia/pérdida (MISMO cálculo que Flask)
                    if purchase_value != 0:
                        profit_loss_percentage = ((current_value - purchase_value) / purchase_value) * 100
                    else:
                        profit_loss_percentage = 0
                    
                    # Calcular dinero total (MISMO cálculo que Flask)
                    total_money = amount + (amount * profit_loss_percentage / 100)
                    
                    # Preparar datos para actualizar
                    update_data = {
                        "current_value": current_value,
                        "total_money": total_money,
                        "profit_loss_percentage": profit_loss_percentage,
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    # Actualizar en Supabase
                    result = db.update_investment(investment_id, update_data)
                    
                    if result:
                        updated_count += 1
                        print(f"    ✅ Actualizado: {current_value}€ ({profit_loss_percentage:.2f}%)")
                    else:
                        errors.append(f"Error al actualizar {asset_name}")
                        
                except Exception as e:
                    error_msg = f"Error con {asset_name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"    ⚠️  {error_msg}")
            else:
                print(f"  ⏭️  Saltando (crowfounding/capital riesgo): {asset_name[:30]}...")
        
        # Preparar respuesta (MISMA estructura que Flask)
        response_data = {
            "success": True,
            "message": f"Actualización completada. {updated_count} activos actualizados.",
            "updated_count": updated_count,
            "errors": errors if errors else None
        }
        
        print(f"✅ {updated_count}/{len(investments)} activos actualizados")
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error crítico: {str(e)}")
        
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "message": "Error al actualizar activos"
            })
        }

# Test local
if __name__ == "__main__":
    print("🧪 Testeando API /api/update-assets...")
    
    class MockRequest:
        method = "POST"
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"📝 Mensaje: {data['message']}")
    else:
        print(f"❌ Error: {result['body']}")