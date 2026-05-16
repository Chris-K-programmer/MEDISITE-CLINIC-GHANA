/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useRef, useEffect, onWillUnmount, reactive } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

console.log("Medisite VitalsChart JS Loaded");

export class VitalsChart extends Component {
    static template = "medisite_clinic.VitalsChart";

    setup() {
        console.log("Setting up VitalsChart component");
        this.weightTempRef = useRef("weightTempChart");
        this.bpPulseRef = useRef("bpPulseChart");
        this.orm = useService("orm");

        this.state = reactive({
            hasData: false,
        });
        this.charts = [];

        onWillStart(async () => {
            try {
                console.log("VitalsChart onWillStart: loading chartjs_lib");
                await loadBundle("web.chartjs_lib");
                console.log("VitalsChart onWillStart: chartjs_lib loaded, fetching data");
                await this.fetchData();
            } catch (err) {
                console.error("VitalsChart onWillStart error:", err);
            }
        });

        useEffect(() => {
            if (this.state.hasData) {
                console.log("VitalsChart useEffect: rendering charts");
                this.renderCharts();
            }
        });

        onWillUnmount(() => {
            this.destroyCharts();
        });
    }

    async fetchData() {
        const patientId = this.props.record.data.id;
        console.log("VitalsChart: Fetching data for patient ID", patientId);
        if (!patientId) {
            console.warn("VitalsChart: No patient ID found on record");
            return;
        }

        try {
            const data = await this.orm.searchRead("med.consultation",
                [['patient_id', '=', patientId], ['state', '=', 'done']],
                ['date', 'weight', 'temp', 'bp', 'hr'],
                { order: 'date asc' }
            );
            console.log("VitalsChart: Data received:", data);

            if (data && data.length > 0) {
                this.vitalsData = data;
                this.state.hasData = true;
            }
        } catch (err) {
            console.error("VitalsChart: Error fetching data via ORM:", err);
        }
    }

    renderCharts() {
        this.destroyCharts();

        if (typeof Chart === 'undefined') {
            console.error("Chart.js is not loaded!");
            return;
        }

        const labels = this.vitalsData.map(d => d.date);
        const weights = this.vitalsData.map(d => d.weight || null);
        const temps = this.vitalsData.map(d => d.temp || null);
        const hrs = this.vitalsData.map(d => d.hr || null);

        const sys = [];
        const dia = [];
        this.vitalsData.forEach(d => {
            if (d.bp && d.bp.includes('/')) {
                const parts = d.bp.split('/');
                sys.push(parseFloat(parts[0]));
                dia.push(parseFloat(parts[1]));
            } else {
                sys.push(null);
                dia.push(null);
            }
        });

        try {
            // 1. Weight & Temp Chart
            if (this.weightTempRef.el) {
                this.charts.push(new Chart(this.weightTempRef.el, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Weight (kg)',
                                data: weights,
                                borderColor: '#007bff',
                                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                                yAxisID: 'y',
                                tension: 0.3
                            },
                            {
                                label: 'Temp (°C)',
                                data: temps,
                                borderColor: '#ffc107',
                                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                                yAxisID: 'y1',
                                tension: 0.3
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Weight (kg)' } },
                            y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'Temp (°C)' }, grid: { drawOnChartArea: false } }
                        }
                    }
                }));
            }

            // 2. BP & HR Chart
            if (this.bpPulseRef.el) {
                this.charts.push(new Chart(this.bpPulseRef.el, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Systolic',
                                data: sys,
                                borderColor: '#dc3545',
                                backgroundColor: 'transparent',
                                tension: 0.3
                            },
                            {
                                label: 'Diastolic',
                                data: dia,
                                borderColor: '#dc3545',
                                backgroundColor: 'rgba(220, 53, 69, 0.2)',
                                fill: '-1',
                                tension: 0.3
                            },
                            {
                                label: 'Heart Rate (bpm)',
                                data: hrs,
                                borderColor: '#28a745',
                                backgroundColor: 'transparent',
                                borderDash: [5, 5],
                                tension: 0.3
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { title: { display: true, text: 'Value' } }
                        }
                    }
                }));
            }
        } catch (err) {
            console.error("VitalsChart: Error rendering charts:", err);
        }
    }

    destroyCharts() {
        this.charts.forEach(c => c.destroy());
        this.charts = [];
    }
}

// Register as a Field Widget (for Odoo 19)
export const vitalsChartField = {
    component: VitalsChart,
    supportedTypes: ["integer"],
};

registry.category("fields").add("medisite_vitals_chart", vitalsChartField);
