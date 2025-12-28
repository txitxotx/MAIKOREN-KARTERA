# api/graphs.py
import json
import sys
import os
import base64
import io
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from supabase_client import db
except ImportError:
    from utils.supabase_client import db

import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def create_graph(ticker):
    """EXACTAMENTE la misma función que en tu app.py Flask (líneas 20-36)"""
    try:
        # Descargar datos
        data = yf.download(ticker, period="1mo")
        
        if data.empty:
            return None
            
        # Crear figura
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Configurar estilo
        sns.set(style="whitegrid")
        
        # Graficar (MISMA configuración que Flask)
        data['Close'].plot(ax=ax, color='#000000', linewidth=2.5, linestyle='-')
        ax.set_facecolor('#B0B0B0')
        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.tick_params(axis='x', colors='none')
        ax.tick_params(axis='y', colors='none')
        
        # Configurar ejes (MISMO que Flask)
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.yaxis.set_major_locator(plt.MaxNLocator(10))
        ax.grid(color='#FFFFFF', linestyle='-', linewidth=0.5)
        
        # Convertir a base64
        img = io.BytesIO()
        plt.savefig(img, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        
        return plot_url
        
    except Exception as e:
        print(f"❌ Error creando gráfico para {ticker}: {e}")
        return None

def handler(request):
    """
    API para /api/graphs - EQUIVALENTE a app.route('/graphs') en Flask
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
        print("📈 Generando gráficas...")
        
        # Obtener inversiones
        investments = db.get_all_investments()
        
        if not investments:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "success": True,
                    "images": [],
                    "count": 0,
                    "total": 0,
                    "timestamp": datetime.now().isoformat()
                })
            }
        
        images = []
        generated = 0
        
        # Generar gráfica para cada inversión (MISMA lógica que Flask)
        for inv in investments:
            ticker = inv.get("isin", "")
            asset_name = inv.get("asset_name", "Sin nombre")
            
            # Excluir crowfounding y capital riesgo (MISMO que Flask)
            if ticker and ticker not in ["Crowfounding", "CAPITAL RIESGO"]:
                print(f"  📊 Generando gráfica para: {asset_name[:30]}...")
                
                plot_url = create_graph(ticker)
                
                if plot_url:
                    images.append({
                        "url": plot_url,
                        "name": asset_name,
                        "isin": ticker
                    })
                    generated += 1
        
        print(f"✅ {generated} gráficas generadas exitosamente")
        
        # MISMA estructura de respuesta que Flask
        response_data = {
            "success": True,
            "count": generated,
            "total": len(investments),
            "images": images,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, default=str)
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error en API graphs: {e}")
        
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
    print("🧪 Testeando API /api/graphs...")
    
    class MockRequest:
        method = "GET"
    
    result = handler(MockRequest())
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"✅ Success: {data['success']}")
        print(f"📊 Gráficas generadas: {data['count']}/{data['total']}")
    else:
        print(f"❌ Error: {result['body'][:200]}...")