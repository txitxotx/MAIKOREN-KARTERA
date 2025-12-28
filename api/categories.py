# api/categories.py
import json
import sys
import os
import plotly.graph_objects as go
import plotly
import seaborn as sns

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from supabase_client import db
except ImportError:
    from utils.supabase_client import db

def handler(request):
    """
    API para /api/categories - EQUIVALENTE a app.route('/investment-categories') en Flask
    Gráfico de barras por activo individual
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
        print("📊 Generando gráfico por activo individual...")
        
        # Obtener todas las inversiones
        investments = db.get_all_investments()
        
        if not investments:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "message": "No hay inversiones",
                    "graph_data": None,
                    "table_data": []
                })
            }
        
        # Ordenar por total_money descendente (MISMO que Flask línea 145)
        investments_sorted = sorted(investments, key=lambda x: float(x.get("total_money", 0)), reverse=True)
        
        # Preparar datos para el gráfico (MISMO que Flask líneas 146-149)
        labels = [row["asset_name"] for row in investments_sorted]
        sizes = [float(row["total_money"]) for row in investments_sorted]
        total_money_sum = sum(sizes)
        percentages = [(size / total_money_sum) * 100 for size in sizes]
        
        # Generar colores (MISMA paleta que Flask líneas 151-152)
        colors = sns.color_palette("husl", len(labels))
        color_hex = [f'#{int(c[0]*255):02x}{int(c[1]*255):02x}{int(c[2]*255):02x}' for c in colors]
        
        # Crear gráfico de barras (MISMA lógica que Flask líneas 154-176)
        fig = go.Figure()
        
        for label, percentage, color in zip(labels, percentages, color_hex):
            fig.add_trace(go.Bar(
                x=[label],
                y=[percentage],
                text=f"{percentage:.1f}%",
                textposition='outside',
                textfont=dict(
                    size=16,
                    color='#00FF00'  # Mismo color verde que Flask
                ),
                marker=dict(color=color, line=dict(width=2, color="white")),
                hoverinfo='text',
                hovertext=f"<b>{label}</b>: {percentage:.2f}%",
            ))
        
        # MISMA configuración de layout que Flask (líneas 178-186)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showticklabels=False),
            yaxis=dict(tickfont=dict(color="#00FF00")),
            hovermode='x',
            margin=dict(l=40, r=40, t=20, b=20),
        )
        
        # Preparar datos para la tabla (MISMO que Flask línea 188)
        color_data = []
        for color, label, size, percentage in zip(color_hex, labels, sizes, percentages):
            color_data.append({
                "color": color,
                "label": label,
                "size": size,
                "percentage": percentage
            })
        
        # Convertir gráfico a JSON (MISMO que Flask línea 189)
        graph_json = json.loads(json.dumps(fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder))
        
        response_data = {
            "success": True,
            "graph_data": graph_json,
            "table_data": color_data,
            "total_money_sum": total_money_sum,
            "count": len(investments)
        }
        
        print(f"✅ Gráfico generado para {len(investments)} activos")
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error en API categories: {e}")
        
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
                "message": "Error al generar gráfico por activo"
            })
        }

# Test local
if __name__ == "__main__":
    print("🧪 Testeando API /api/categories...")
    
    class MockRequest:
        method = "GET"
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"📊 Activos: {data['count']}")
        print(f"💰 Total: {data['total_money_sum']}€")
    else:
        print(f"❌ Error: {result['body'][:200]}...")