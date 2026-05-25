/**
 * MED-INTELLIGENCE: Gestor de Visualización Gráfica (Chart.js)
 * Maneja la inicialización y actualización dinámica del gráfico bayesiano.
 * CORREGIDO: Construye el gráfico dinámicamente desde la respuesta del servidor,
 * usando los nombres exactos de las enfermedades del motor bayesiano.
 */

class LiveChartManager {
    constructor(canvasId) {
        this.canvasId = canvasId;
        this.chart = null;
        this.initChart();
    }

    // Mapa de color por nivel de alerta basado en nombre de enfermedad
    // Se usa el prefijo/sufijo de la enfermedad para clasificarla
    _getColorForDisease(name) {
        // Enfermedades Rojas (emergencia crítica)
        const redDiseases = [
            'Exacerbación Aguda de EPOC',
            'Infarto Agudo de Miocardio',
            'Miocarditis',
            'Encefalitis',
            'Accidente Cerebrovascular',
            'COVID-19 Grave',
            'Tromboembolismo Pulmonar'
        ];
        // Enfermedades Amarillas (urgencia moderada)
        const yellowDiseases = [
            'Neumonía',
            'Crisis Asmática Aguda',
            'Insuficiencia Cardíaca',
            'Dengue',
            'COVID-19'
        ];

        for (const red of redDiseases) {
            if (name.includes(red.split(' ')[0]) && redDiseases.some(r => name.includes(r.split('(')[0].trim()))) {
                return { bg: 'rgba(239, 68, 68, 0.75)', border: '#ef4444' };
            }
        }
        for (const y of yellowDiseases) {
            if (name.startsWith(y.split(' ')[0]) && yellowDiseases.some(d => name.includes(d.split('(')[0].trim()))) {
                return { bg: 'rgba(245, 158, 11, 0.75)', border: '#f59e0b' };
            }
        }
        return { bg: 'rgba(16, 185, 129, 0.75)', border: '#10b981' };
    }

    _getColorsFromMetadata(labels, alertMap) {
        return labels.map(label => {
            const level = (alertMap[label] || '').toLowerCase();
            if (level === 'rojo')     return { bg: 'rgba(239, 68, 68, 0.75)',  border: '#ef4444' };
            if (level === 'amarillo') return { bg: 'rgba(245, 158, 11, 0.75)', border: '#f59e0b' };
            return { bg: 'rgba(16, 185, 129, 0.75)', border: '#10b981' };
        });
    }

    initChart(labels = [], values = [], alertMap = {}) {
        const ctx = document.getElementById(this.canvasId);
        if (!ctx) return;

        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }

        const colors = labels.length > 0
            ? this._getColorsFromMetadata(labels, alertMap)
            : [];

        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Probabilidad Posterior (%)',
                    data: values,
                    backgroundColor: colors.map(c => c.bg),
                    borderColor: colors.map(c => c.border),
                    borderWidth: 1.5,
                    borderRadius: 6,
                    barPercentage: 0.68
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` Probabilidad: ${context.parsed.x.toFixed(2)}%`;
                            }
                        },
                        backgroundColor: '#131c31',
                        titleFont: { family: 'Outfit', size: 13 },
                        bodyFont:  { family: 'Inter',  size: 12 },
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        padding: 10
                    }
                },
                scales: {
                    x: {
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.04)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 11 },
                            callback: function(value) { return value + '%'; }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            color: '#f8fafc',
                            font: { family: 'Outfit', size: 11, weight: '500' }
                        }
                    }
                },
                animation: {
                    duration: 500,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Actualiza el gráfico con los datos de probabilidades del servidor.
     * @param {Object} probabilidades - Mapa {nombre_enfermedad: probabilidad (0-1)}
     * @param {Object} alertMap       - Mapa {nombre_enfermedad: nivel_alerta} para color
     */
    actualizar(probabilidades, alertMap = {}) {
        if (!probabilidades || Object.keys(probabilidades).length === 0) return;

        // Ordenar enfermedades de mayor a menor probabilidad para mejor legibilidad
        const sorted = Object.entries(probabilidades)
            .sort((a, b) => b[1] - a[1]);

        const labels = sorted.map(([name]) => name);
        const values = sorted.map(([, p])  => parseFloat((p * 100).toFixed(2)));

        // Reconstruir el gráfico con los nuevos labels (puede variar en número)
        this.initChart(labels, values, alertMap);
    }
}
