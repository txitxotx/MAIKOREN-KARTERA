# api/tables.py
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from supabase_client import db
except ImportError:
    from utils.supabase_client import db

def handler(request):
    """
    Manejador para /api/tables - EQUIVALENTE a app.route('/tables') en Flask
    Devuelve inversiones categorizadas por investment_type
    """
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({})
        }
    
    try:
        print("📊 Obteniendo inversiones para /tables...")
        
        # Obtener todas las inversiones (MISMA lógica que Flask)
        investments = db.get_all_investments()
        
        if not investments:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "categories": {},
                    "counts": {"total": 0}
                })
            }
        
        # Categorizar EXACTAMENTE como en tu Flask original
        # Basado en investment_type (índice 8 en Flask, campo en Supabase)
        dca = []
        renta_fija = []
        renta_variable = []
        cryptomonedas = []
        acciones = []
        crowfounding = []
        epsv = []
        capital_riesgo = []
        
        for inv in investments:
            inv_type = (inv.get("investment_type") or "").upper()
            
            # MISMA lógica de categorización que en tu app.py
            if "DCA" in inv_type and ("RENTA FIJA" in inv_type or "RENTA VARIABLE" in inv_type):
                dca.append(inv)
            elif "RENTA FIJA" in inv_type:
                renta_fija.append(inv)
            elif "RENTA VARIABLE" in inv_type:
                renta_variable.append(inv)
            elif "CRYPTO" in inv_type:
                cryptomonedas.append(inv)
            elif "ACCIONES" in inv_type:
                acciones.append(inv)
            elif "CROWFOUNDING" in inv_type:
                crowfounding.append(inv)
            elif "EPSV" in inv_type:
                epsv.append(inv)
            elif "CAPITAL RIESGO" in inv_type:
                capital_riesgo.append(inv)
            else:
                # Por defecto a renta variable (MISMO que Flask)
                renta_variable.append(inv)
        
        # Contar totales
        counts = {
            "total": len(investments),
            "dca": len(dca),
            "renta_fija": len(renta_fija),
            "renta_variable": len(renta_variable),
            "cryptomonedas": len(cryptomonedas),
            "acciones": len(acciones),
            "crowfounding": len(crowfounding),
            "epsv": len(epsv),
            "capital_riesgo": len(capital_riesgo)
        }
        
        print(f"✅ Categorizadas {len(investments)} inversiones")
        
        # MISMA estructura de respuesta que Flask
        response_data = {
            "success": True,
            "categories": {
                "dca": dca,
                "renta_fija": renta_fija,
                "renta_variable": renta_variable,
                "cryptomonedas": cryptomonedas,
                "acciones": acciones,
                "crowfounding": crowfounding,
                "epsv": epsv,
                "capital_riesgo": capital_riesgo
            },
            "counts": counts
        }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error en API tables: {str(e)}")
        
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "message": "Error al obtener datos categorizados"
            })
        }

# Para testing local
if __name__ == "__main__":
    print("🧪 Testeando API /api/tables...")
    
    class MockRequest:
        method = "GET"
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"📊 Totales: {data['counts']}")
    else:
        print(f"❌ Error: {result['body']}")