# utils/supabase_client.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SupabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.error("❌ SUPABASE_URL o SUPABASE_KEY no configurados en .env")
            print("⚠️  Configura en .env:")
            print("SUPABASE_URL=https://tu-proyecto.supabase.co")
            print("SUPABASE_KEY=tu_anon_public_key")
            raise ValueError("Variables de entorno no configuradas")
        
        self.client = create_client(self.url, self.key)
        logger.info("✅ Cliente Supabase inicializado")
        print(f"✅ Conectado a Supabase: {self.url[:30]}...")
    
    def get_all_investments(self):
        """Obtiene todas las inversiones ordenadas por ID"""
        try:
            response = self.client.table("investments").select("*").order("id").execute()
            print(f"📊 {len(response.data)} inversiones obtenidas de Supabase")
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener inversiones: {e}")
            return []
    
    def update_investment(self, investment_id, data):
        """Actualiza una inversión existente"""
        try:
            response = self.client.table("investments").update(data).eq("id", investment_id).execute()
            print(f"✅ Inversión {investment_id} actualizada en Supabase")
            return response.data
        except Exception as e:
            print(f"❌ Error al actualizar inversión {investment_id}: {e}")
            return None
    
    def add_investment(self, data):
        """Añade una nueva inversión"""
        try:
            response = self.client.table("investments").insert(data).execute()
            print(f"✅ Nueva inversión añadida: {data.get('asset_name', 'Sin nombre')}")
            return response.data
        except Exception as e:
            print(f"❌ Error al añadir inversión: {e}")
            return None

# ==== ¡IMPORTANTE! Añade estas líneas al final ====
# Singleton para acceso global
db = SupabaseManager()