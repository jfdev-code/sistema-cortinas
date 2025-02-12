import React, { useState, useEffect } from 'react';

function ProfitabilityManager() {
    const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
    const orderStates = [
        { 
            value: 'pendiente', 
            label: 'Pendiente', 
            backgroundColor: '#ffc107',  // Amber
            textColor: '#000000'         // Black text
        },
        { 
            value: 'produccion', 
            label: 'En Producción', 
            backgroundColor: '#17a2b8',  // Teal
            textColor: '#ffffff'         // White text
        },
        { 
            value: 'finalizado', 
            label: 'Finalizado', 
            backgroundColor: '#28a745',  // Green
            textColor: '#ffffff'         // White text
        },
        { 
            value: 'entregado', 
            label: 'Entregado', 
            backgroundColor: '#6c757d',  // Gray
            textColor: '#ffffff'         // White text
        }
    ];

    // State for managing orders and profitability calculations
    const [orders, setOrders] = useState([]);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [profitabilityResults, setProfitabilityResults] = useState(null);

    // State for calculator inputs
    const [calculatorInputs, setCalculatorInputs] = useState({
        rentabilidad: 30, // Default profit margin 30%
        costoBase: '',
        margenMinimo: 20, // Minimum acceptable margin
        incluirGastosFijos: false,
        gastosFijos: 0
    });

    // State for statistics and summary data
    const [statistics, setStatistics] = useState({
        promedioRentabilidad: 0,
        ordenMasRentable: null,
        ordenMenosRentable: null
    });

    // Fetch orders when component mounts
    useEffect(() => {
        fetchOrders();
    }, []);

    // Calculate statistics when orders change
    useEffect(() => {
        if (orders.length > 0) {
            calculateStatistics();
        }
    }, [orders]);

    /**
     * Fetches all orders from the backend
     */
    const fetchOrders = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/cortinas/`);
            if (!response.ok) throw new Error('Error al cargar órdenes');
            
            const data = await response.json();
            setOrders(data);
        } catch (err) {
            setError('Error al cargar las órdenes: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Calculates profitability for a specific order
     * @param {number} orderId - The ID of the order to analyze
     */
    const calculateProfitability = async (orderId) => {
        setLoading(true);
        setProfitabilityResults(null);
        setError(null);

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/rentabilidad/calcular-precio/${orderId}?` +
                `rentabilidad=${calculatorInputs.rentabilidad / 100}`
            );

            if (!response.ok) throw new Error('Error al calcular rentabilidad');
            
            const data = await response.json();
            setProfitabilityResults(data);
        } catch (err) {
            setError('Error en el cálculo: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Calculates overall statistics for all orders
     */
    const calculateStatistics = () => {
        if (orders.length === 0) return;

        const rentabilidades = orders.map(order => ({
            id: order.id,
            rentabilidad: ((order.precio_venta - order.costo_total) / order.precio_venta) * 100
        }));

        const promedio = rentabilidades.reduce((acc, curr) => acc + curr.rentabilidad, 0) / rentabilidades.length;
        const masRentable = orders[rentabilidades.indexOf(Math.max(...rentabilidades.map(r => r.rentabilidad)))];
        const menosRentable = orders[rentabilidades.indexOf(Math.min(...rentabilidades.map(r => r.rentabilidad)))];

        setStatistics({
            promedioRentabilidad: promedio,
            ordenMasRentable: masRentable,
            ordenMenosRentable: menosRentable
        });
    };

    /**
     * Handles changes in calculator input fields
     */
    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setCalculatorInputs(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    /**
     * Formats currency values for display
     */
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP'
        }).format(value);
    };

    /**
     * Renders the profitability calculator form
     */
    const renderCalculator = () => (
        <div className="card">
            <div className="card-header bg-primary text-white">
                <h5 className="card-title mb-0">Calculadora de Rentabilidad</h5>
            </div>
            <div className="card-body">
                <form onSubmit={(e) => {
                    e.preventDefault();
                    if (selectedOrder) {
                        calculateProfitability(selectedOrder.id);
                    }
                }}>
                    <div className="mb-3">
                        <label className="form-label">Rentabilidad Deseada (%)</label>
                        <input
                            type="number"
                            className="form-control"
                            name="rentabilidad"
                            value={calculatorInputs.rentabilidad}
                            onChange={handleInputChange}
                            min="0"
                            max="100"
                            required
                        />
                    </div>

                    <div className="mb-3">
                        <label className="form-label">Margen Mínimo Aceptable (%)</label>
                        <input
                            type="number"
                            className="form-control"
                            name="margenMinimo"
                            value={calculatorInputs.margenMinimo}
                            onChange={handleInputChange}
                            min="0"
                            max="100"
                        />
                    </div>

                    <div className="mb-3 form-check">
                        <input
                            type="checkbox"
                            className="form-check-input"
                            id="incluirGastosFijos"
                            name="incluirGastosFijos"
                            checked={calculatorInputs.incluirGastosFijos}
                            onChange={handleInputChange}
                        />
                        <label className="form-check-label" htmlFor="incluirGastosFijos">
                            Incluir Gastos Fijos
                        </label>
                    </div>

                    {calculatorInputs.incluirGastosFijos && (
                        <div className="mb-3">
                            <label className="form-label">Gastos Fijos</label>
                            <input
                                type="number"
                                className="form-control"
                                name="gastosFijos"
                                value={calculatorInputs.gastosFijos}
                                onChange={handleInputChange}
                                min="0"
                            />
                        </div>
                    )}

                    <button 
                        type="submit" 
                        className="btn btn-primary w-100"
                        disabled={!selectedOrder || loading}
                    >
                        {loading ? 'Calculando...' : 'Calcular Rentabilidad'}
                    </button>
                </form>
            </div>
        </div>
    );

    /**
     * Renders the results of profitability calculations
     */
    const renderResults = () => {
        if (!profitabilityResults) return null;

        return (
            <div className="card mt-3">
                <div className="card-header bg-success text-white">
                    <h5 className="card-title mb-0">Resultados del Análisis</h5>
                </div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-6">
                            <div className="mb-3">
                                <h6>Costo de Producción</h6>
                                <p className="h4 text-primary">
                                    {formatCurrency(profitabilityResults.costo_produccion)}
                                </p>
                            </div>

                            <div className="mb-3">
                                <h6>Precio de Venta Sugerido</h6>
                                <p className="h4 text-success">
                                    {formatCurrency(profitabilityResults.precio_venta_sugerido)}
                                </p>
                            </div>
                        </div>
                        <div className="col-md-6">
                            <div className="mb-3">
                                <h6>Margen de Ganancia</h6>
                                <p className="h4 text-info">
                                    {formatCurrency(profitabilityResults.margen_ganancia)}
                                </p>
                            </div>

                            <div className="mb-3">
                                <h6>Rentabilidad Real</h6>
                                <p className="h4 text-warning">
                                    {((profitabilityResults.margen_ganancia / profitabilityResults.precio_venta_sugerido) * 100).toFixed(2)}%
                                </p>
                            </div>
                        </div>
                    </div>

                    {profitabilityResults.recomendaciones && (
                        <div className="alert alert-info mt-3">
                            <h6>Recomendaciones</h6>
                            <ul className="list-unstyled mb-0">
                                {profitabilityResults.recomendaciones.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    /**
     * Renders the orders table
     */
    const renderOrdersTable = () => (
        <div className="card">
            <div className="card-header bg-primary text-white">
                <h5 className="card-title mb-0">Órdenes para Análisis</h5>
            </div>
            <div className="card-body">
                {loading ? (
                    <div className="text-center py-4">
                        <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Cargando...</span>
                        </div>
                    </div>
                ) : error ? (
                    <div className="alert alert-danger">{error}</div>
                ) : orders.length === 0 ? (
                    <div className="alert alert-info">No hay órdenes disponibles</div>
                ) : (
                    <div className="table-responsive">
                        <table className="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Dimensiones</th>
                                    <th>Costo Base</th>
                                    <th>Estado</th>
                                    <th>Fecha</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {orders.map(order => (
                                    <tr 
                                        key={order.id}
                                        className={selectedOrder?.id === order.id ? 'table-primary' : ''}
                                    >
                                        <td>{order.id}</td>
                                        <td>{order.ancho}cm × {order.alto}cm</td>
                                        <td>{formatCurrency(order.costo_total)}</td>
                                        <td>
                                            <span 
                                                style={{
                                                    backgroundColor: orderStates.find(s => s.value === order.estado)?.backgroundColor,
                                                    color: orderStates.find(s => s.value === order.estado)?.textColor,
                                                    padding: '0.25rem 0.5rem',
                                                    borderRadius: '0.25rem',
                                                    display: 'inline-block'
                                                }}
                                            >
                                                {order.estado}
                                            </span>
                                        </td>
                                        <td>{new Date(order.fecha_creacion).toLocaleDateString()}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-outline-primary"
                                                onClick={() => {
                                                    setSelectedOrder(order);
                                                    calculateProfitability(order.id);
                                                }}
                                            >
                                                {selectedOrder?.id === order.id ? 'Seleccionado' : 'Analizar'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );

    /**
     * Main component render
     */
    return (
        <div className="container-fluid">
            <div className="row">
                {/* Left column: Calculator and Results */}
                <div className="col-md-4">
                    {renderCalculator()}
                    {renderResults()}
                </div>

                {/* Right column: Orders Table */}
                <div className="col-md-8">
                    {renderOrdersTable()}
                </div>
            </div>
        </div>
    );
}

export default ProfitabilityManager;