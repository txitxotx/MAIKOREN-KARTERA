// public/js/api.js
const API_BASE = '/api';  // En local: 'http://localhost:3000/api'

class InvestmentAPI {
    // Obtener toda la cartera
    static async getPortfolio() {
        try {
            const response = await fetch(`${API_BASE}/portfolio`);
            if (!response.ok) throw new Error(`Error ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error al obtener cartera:', error);
            throw error;
        }
    }

    // Actualizar precios de activos
    static async updateAssets() {
        try {
            const response = await fetch(`${API_BASE}/update-assets`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('Error al actualizar activos:', error);
            throw error;
        }
    }

    // Añadir nuevo activo
    static async addAsset(assetData) {
        try {
            const response = await fetch(`${API_BASE}/add-asset`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(assetData)
            });
            return await response.json();
        } catch (error) {
            console.error('Error al añadir activo:', error);
            throw error;
        }
    }

    // Editar activo existente
    static async editAsset(assetId, updateData) {
        try {
            const response = await fetch(`${API_BASE}/edit-asset`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: assetId, ...updateData })
            });
            return await response.json();
        } catch (error) {
            console.error('Error al editar activo:', error);
            throw error;
        }
    }

    // Formatear números como moneda
    static formatCurrency(value, currency = '€') {
        return new Intl.NumberFormat('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value) + currency;
    }

    // Obtener clase CSS para ganancia/pérdida
    static getProfitLossClass(percentage) {
        if (percentage > 0) return 'positive';
        if (percentage < 0) return 'negative';
        return 'neutral';
    }
}