// public/js/main.js
class PortfolioManager {
    constructor() {
        this.investments = [];
        this.totals = {};
        this.init();
    }

    async init() {
        // Cargar datos iniciales
        await this.loadPortfolioData();
        
        // Configurar event listeners
        this.setupEventListeners();
    }

    async loadPortfolioData() {
        try {
            const loadingRow = document.getElementById('investments-body');
            if (loadingRow) {
                loadingRow.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px;">📊 Cargando datos...</td></tr>';
            }

            const data = await InvestmentAPI.getPortfolio();
            
            if (data.success) {
                this.investments = data.investments;
                this.totals = data.totals;
                this.renderTable();
                this.renderTotals();
                this.updateUI();
            } else {
                this.showError('Error al cargar datos: ' + (data.error || 'Desconocido'));
            }
        } catch (error) {
            this.showError('No se pudo conectar con el servidor. Asegúrate de que las APIs están funcionando.');
            console.error('Error:', error);
        }
    }

    renderTable() {
        const tbody = document.getElementById('investments-body');
        if (!tbody) return;

        if (this.investments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px;">📭 No hay inversiones registradas</td></tr>';
            return;
        }

        let html = '';
        
        this.investments.forEach(investment => {
            const profitClass = InvestmentAPI.getProfitLossClass(investment.profit_loss_percentage);
            const profitFormatted = investment.profit_loss_percentage !== undefined 
                ? investment.profit_loss_percentage.toFixed(2) 
                : '0.00';
            
            html += `
                <tr>
                    <td>${investment.isin || ''}</td>
                    <td>${investment.asset_name || ''}</td>
                    <td>${InvestmentAPI.formatCurrency(investment.purchase_value || 0)}</td>
                    <td>${InvestmentAPI.formatCurrency(investment.amount || 0)}</td>
                    <td>${InvestmentAPI.formatCurrency(investment.current_value || 0)}</td>
                    <td>${InvestmentAPI.formatCurrency(investment.total_money || 0)}</td>
                    <td class="${profitClass}">${profitFormatted}%</td>
                    <td>
                        <a href="https://finance.yahoo.com/quote/${investment.isin}" target="_blank" title="Ver en Yahoo Finance">📈</a>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    }

    renderTotals() {
        const totalsRow = document.getElementById('totals-row');
        if (!totalsRow) return;

        totalsRow.innerHTML = `
            <td colspan="3"></td>
            <td><strong>${InvestmentAPI.formatCurrency(this.totals.quantity || 0)}</strong></td>
            <td></td>
            <td><strong>${InvestmentAPI.formatCurrency(this.totals.money || 0)}</strong></td>
            <td colspan="2"></td>
        `;
    }

    async updateAssets() {
        try {
            const updateBtn = document.getElementById('update-assets');
            if (updateBtn) {
                updateBtn.disabled = true;
                updateBtn.textContent = 'Actualizando...';
            }

            const result = await InvestmentAPI.updateAssets();
            
            if (result.success) {
                this.showMessage(`✅ ${result.message}`, 'success');
                // Recargar datos después de actualizar
                setTimeout(() => this.loadPortfolioData(), 1000);
            } else {
                this.showError('Error al actualizar: ' + (result.error || 'Desconocido'));
            }
        } catch (error) {
            this.showError('Error al conectar con el servidor');
        } finally {
            const updateBtn = document.getElementById('update-assets');
            if (updateBtn) {
                updateBtn.disabled = false;
                updateBtn.textContent = 'Actualizar';
            }
        }
    }

    showMessage(message, type = 'info') {
        // Crear o actualizar mensaje
        let messageDiv = document.getElementById('message-container');
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.id = 'message-container';
            messageDiv.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 1000;
                max-width: 300px;
            `;
            document.body.appendChild(messageDiv);
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `message-alert ${type}`;
        alertDiv.innerHTML = `
            <div style="padding: 10px 15px; margin-bottom: 10px; border-radius: 5px;
                background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
                color: ${type === 'success' ? '#155724' : '#721c24'};
                border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};">
                ${message}
            </div>
        `;

        messageDiv.appendChild(alertDiv);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            alertDiv.remove();
            if (messageDiv.children.length === 0) {
                messageDiv.remove();
            }
        }, 5000);
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    setupEventListeners() {
        // Botón de actualizar
        const updateBtn = document.getElementById('update-assets');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.updateAssets());
        }

        // Botón de añadir activo
        const addBtn = document.getElementById('add-asset');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.openAddAssetModal());
        }

        // Botón de editar activo
        const editBtn = document.getElementById('edit-asset');
        if (editBtn) {
            editBtn.addEventListener('click', () => this.openEditAssetModal());
        }
    }

    openAddAssetModal() {
        // Para versión simple, redirigir a la página de añadir
        window.open('/add-asset-window', 'Agregar Activo', 'width=600,height=500');
    }

    openEditAssetModal() {
        window.open('/edit-asset-window', 'Editar Activo', 'width=600,height=400');
    }

    updateUI() {
        // Actualizar cualquier elemento de la UI
        const countElement = document.getElementById('investments-count');
        if (countElement) {
            countElement.textContent = this.investments.length;
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.portfolioManager = new PortfolioManager();
});

// Funciones globales para HTML onclick (compatibilidad)
function updateAssets() {
    if (window.portfolioManager) {
        window.portfolioManager.updateAssets();
    }
}

function openAddAssetWindow() {
    if (window.portfolioManager) {
        window.portfolioManager.openAddAssetModal();
    }
}

function openEditAssetWindow() {
    if (window.portfolioManager) {
        window.portfolioManager.openEditAssetModal();
    }
}