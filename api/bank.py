# api/bank.py
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

def handler(request):
    """
    API para /api/bank - EQUIVALENTE a app.route('/bank') en Flask
    Devuelve datos bancarios estáticos (MISMOS datos que Flask)
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
        print("🏦 Obteniendo datos bancarios...")
        
        # MISMO array de bancos que en tu Flask original (líneas 159-167)
        banks = [
            ("Kutxabank Nomina", 6295.94, 0, ""),
            ("Kutxabank Conjunta", 391.74, 0, ""),
            ("Trade Republic", 2050, 1.71, ""),
            ("Revolut", 300, 1.51, ""),
            ("Bit2Me", 800, 0, ""),
            ("My Investor", 900, 0, "")
        ]
        
        # MISMOS cálculos que Flask (líneas 169-170)
        total_inversion = sum(bank[1] for bank in banks)
        total_resultado = sum(bank[1] + (bank[1] * bank[2] / 100) for bank in banks if bank[3] == "")
        
        # Añadir fila de totales (MISMO que Flask línea 172)
        banks.append(("TOTALES", total_inversion, "", total_resultado))
        
        # MISMA estructura de respuesta
        response_data = {
            "success": True,
            "banks": banks,
            "totals": {
                "investment": total_inversion,
                "result": total_resultado,
                "accounts": len(banks) - 1  # Excluir fila TOTALES
            }
        }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str)
        }
        
    except Exception as e:
        print(f"❌ Error en API bank: {e}")
        
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "message": "Error al obtener datos bancarios"
            })
        }

# Test local
if __name__ == "__main__":
    print("🧪 Testeando API /api/bank...")
    
    class MockRequest:
        method = "GET"
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"🏦 Bancos: {len(data['banks'])}")
        print(f"💰 Inversión total: {data['totals']['investment']}€")
    else:
        print(f"❌ Error: {result['body']}")