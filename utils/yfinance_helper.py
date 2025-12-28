# utils/yfinance_helper.py (versión completa)
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def get_current_value(isin: str) -> float:
    """
    Obtiene el precio actual de un activo desde Yahoo Finance.
    Mantiene exactamente la misma lógica que tu función original en app.py
    """
    try:
        ticker = yf.Ticker(isin)
        
        # 1. Intentar historial intradía
        try:
            hist = ticker.history(period="1d", interval="1m")
            if hist is not None and not hist.empty:
                last_price = hist['Close'].iloc[-1]
                if last_price is not None:
                    logger.debug(f"✅ Precio desde historial: {isin} = {last_price}")
                    return float(last_price)
        except Exception as e_hist:
            logger.debug(f"⚠️ Historial falló para {isin}: {e_hist}")
        
        # 2. Intentar fast_info
        try:
            if hasattr(ticker, 'fast_info'):
                fi = ticker.fast_info
                if isinstance(fi, dict):
                    if 'last_price' in fi and fi['last_price'] is not None:
                        logger.debug(f"✅ Precio desde fast_info (dict): {isin} = {fi['last_price']}")
                        return float(fi['last_price'])
                else:
                    if hasattr(fi, 'last_price') and fi.last_price is not None:
                        logger.debug(f"✅ Precio desde fast_info (obj): {isin} = {fi.last_price}")
                        return float(fi.last_price)
        except Exception as e_fast:
            logger.debug(f"⚠️ fast_info falló para {isin}: {e_fast}")
        
        # 3. Intentar ticker.info
        try:
            info = ticker.info
            if isinstance(info, dict) and 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                logger.debug(f"✅ Precio desde info: {isin} = {info['regularMarketPrice']}")
                return float(info['regularMarketPrice'])
        except Exception as e_info:
            logger.debug(f"⚠️ ticker.info falló para {isin}: {e_info}")
        
        # Si todo falla
        logger.warning(f"⚠️ No se pudo obtener precio para {isin}, devolviendo 0")
        return 0.0
        
    except Exception as e:
        logger.error(f"❌ Error crítico al obtener precio de {isin}: {e}")
        return 0.0

def calculate_profit_loss(purchase_value, current_value):
    """Calcula el porcentaje de ganancia/pérdida (igual que en app.py)"""
    if purchase_value == 0 or purchase_value is None:
        return 0.0
    try:
        return ((float(current_value) - float(purchase_value)) / float(purchase_value)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0