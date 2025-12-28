# api/pie-chart.py
import json
import sys
import os
import plotly.graph_objects as go
import plotly

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from supabase_client import db
except ImportError:
    from utils.supabase_client import db

def handler(request):
    """
    API para /api/pie-chart - EQUIVALENTE a app.route('/pie-chart') en Flask
    Calcula composición de cartera por categorías
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
        print("🥧 Calculando composición de cartera...")
        
        # Obtener todas las inversiones
        investments = db.get_all_investments()
        
        if not investments:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "message": "No hay inversiones",
                    "categories": {},
                    "total": 0
                })
            }
        
        # Categorizar MISMO que en Flask (líneas 178-197)
        # Pero adaptado para Supabase (no índices, sino campos)
        renta_fija = []
        renta_variable = []
        cryptomonedas = []
        acciones = []
        crowfounding = []
        epsv = []
        capital_riesgo = []
        
        # Nota: En tu Flask original usabas índices fijos [3:6], [6:8], etc.
        # Aquí necesito la lógica exacta basada en investment_type
        for inv in investments:
            inv_type = (inv.get("investment_type") or "").upper()
            
            if "RENTA FIJA" in inv_type:
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
                # Por defecto a renta variable
                renta_variable.append(inv)
        
        # Calcular totales (MISMO cálculo que Flask líneas 199-208)
        total_renta_fija = sum(float(inv.get("total_money", 0)) for inv in renta_fija)
        total_renta_variable = sum(float(inv.get("total_money", 0)) for inv in renta_variable)
        total_crypto = sum(float(inv.get("total_money", 0)) for inv in cryptomonedas)
        total_acciones = sum(float(inv.get("total_money", 0)) for inv in acciones)
        total_crowfounding = sum(float(inv.get("total_money", 0)) for inv in crowfounding)
        total_epsv = sum(float(inv.get("total_money", 0)) for inv in epsv)
        total_capital_riesgo = sum(float(inv.get("total_money", 0)) for inv in capital_riesgo)
        
        overall_total = (
            total_renta_fija + total_renta_variable + total_crypto + 
            total_acciones + total_crowfounding + total_epsv + total_capital_riesgo
        )
        
        # Calcular porcentajes (MISMO cálculo que Flask líneas 211-218)
        perc_renta_fija = (total_renta_fija / overall_total) * 100 if overall_total > 0 else 0
        perc_renta_variable = (total_renta_variable / overall_total) * 100 if overall_total > 0 else 0
        perc_crypto = (total_crypto / overall_total) * 100 if overall_total > 0 else 0
        perc_acciones = (total_acciones / overall_total) * 100 if overall_total > 0 else 0
        perc_crowfounding = (total_crowfounding / overall_total) * 100 if overall_total > 0 else 0
        perc_epsv = (total_epsv / overall_total) * 100 if overall_total > 0 else 0
        perc_capital_riesgo = (total_capital_riesgo / overall_total) * 100 if overall_total > 0 else 0
        
        # MISMA estructura de datos que Flask (líneas 220-222)
        pie_labels = ["RENTA FIJA", "RENTA VARIABLE", "CRYPTOMONEDAS", 
                      "ACCIONES", "CROWFOUNDING", "EPSV", "CAPITAL RIESGO & STARTUPS"]
        pie_values = [perc_renta_fija, perc_renta_variable, perc_crypto, 
                      perc_acciones, perc_crowfounding, perc_epsv, perc_capital_riesgo]
        
        # MISMA paleta de colores que Flask (línea 225)
        custom_colors = ["#FF6B6B", "#48CAE4", "#F9C74F", "#6BCB77", 
                         "#4D96FF", "#BC6FF1", "#FFA500"]
        
        # Crear gráfico de pastel (similar a Flask líneas 228-240)
        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_values,
            marker=dict(colors=custom_colors),
            textinfo='label+percent',
            insidetextorientation='radial',
            textfont=dict(color="#00FF00")
        )])
        
        # Preparar datos para la tabla (similar a Flask línea 266)
        data_list = []
        for label, total, percentage, color in zip(
            pie_labels,
            [total_renta_fija, total_renta_variable, total_crypto, total_acciones, 
             total_crowfounding, total_epsv, total_capital_riesgo],
            [perc_renta_fija, perc_renta_variable, perc_crypto, perc_acciones, 
             perc_crowfounding, perc_epsv, perc_capital_riesgo],
            custom_colors
        ):
            data_list.append({
                "color": color,
                "label": label,
                "total": total,
                "percentage": percentage
            })
        
        response_data = {
            "success": True,
            "categories": {
                "labels": pie_labels,
                "values": pie_values,
                "colors": custom_colors,
                "totals": {
                    "renta_fija": total_renta_fija,
                    "renta_variable": total_renta_variable,
                    "crypto": total_crypto,
                    "acciones": total_acciones,
                    "crowfounding": total_crowfounding,
                    "epsv": total_epsv,
                    "capital_riesgo": total_capital_riesgo,
                    "overall": overall_total
                }
            },
            "table_data": data_list,
            "pie_chart": json.loads(json.dumps(fig_pie.to_dict(), cls=plotly.utils.PlotlyJSONEncoder))
        }
        
        print(f"✅ Composición calculada: {overall_total}€ total")
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error en API pie-chart: {e}")
        
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "details": traceback.format_exc()
            })
        }

# Test local
if __name__ == "__main__":
    print("🧪 Testeando API /api/pie-chart...")
    
    class MockRequest:
        method = "GET"
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"🥧 Categorías: {len(data['categories']['labels'])}")
        print(f"💰 Total general: {data['categories']['totals']['overall']}€")
    else:
        print(f"❌ Error: {result['body'][:200]}...")