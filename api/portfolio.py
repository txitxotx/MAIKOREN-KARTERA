# api/portfolio.py
import json
import sys
import os

# Añadir utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

def handler(request):
    """
    Manejador para la ruta /api/portfolio
    Devuelve todas las inversiones con totales calculados
    """
    # Configurar headers CORS
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    # Manejar preflight CORS
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({})
        }
    
    try:
        # Importar según lo que tengas en supabase_client.py
        try:
            from supabase_client import db
            supabase = db
        except ImportError:
            from supabase_client import SupabaseManager
            supabase = SupabaseManager()
        
        # Obtener todas las inversiones
        investments = supabase.get_all_investments()
        
        if not investments:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"success": False, "error": "No se encontraron inversiones"})
            }
        
        # Calcular totales
        total_quantity = sum(float(inv.get("amount", 0)) for inv in investments)
        total_money = sum(float(inv.get("total_money", 0)) for inv in investments)
        total_purchase_value = sum(float(inv.get("purchase_value", 0)) for inv in investments)
        
        # Preparar respuesta
        response_data = {
            "success": True,
            "investments": investments,
            "totals": {
                "quantity": total_quantity,
                "money": total_money,
                "purchase_value": total_purchase_value
            }
        }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "details": traceback.format_exc()
            })
        }

# Para testing local
if __name__ == "__main__":
    print("🧪 Testeando API /api/portfolio localmente...")
    
    # Simular un request
    class MockRequest:
        method = "GET"
    
    result = handler(MockRequest())
    
    print(f"📤 Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"📊 Total inversiones: {len(data['investments'])}")
        print(f"💰 Total dinero: {data['totals']['money']}€")
        
        if data['investments']:
            print("\n📋 Primeras 3 inversiones:")
            for i, inv in enumerate(data['investments'][:3], 1):
                name = inv.get('asset_name', 'Sin nombre')
                print(f"  {i}. {name[:40]}... - {inv.get('purchase_value', 0)}€")
    else:
        print(f"❌ Error: {result['body'][:200]}...")