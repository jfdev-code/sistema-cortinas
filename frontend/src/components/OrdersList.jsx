import React, { useState, useEffect } from 'react';

function OrdersList() {
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

    const [orders, setOrders] = useState([]);
    const [designs, setDesigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedOrder, setSelectedOrder] = useState(null);
    
    const [filters, setFilters] = useState({
        estado: '',
        dateStart: '',
        dateEnd: ''
    });

    useEffect(() => {
        const style = document.createElement('style');
        style.innerHTML = `
            select option {
                background-color: white !important;
                color: black !important;
            }
            select option:checked {
                background-color: inherit !important;
                color: inherit !important;
            }
        `;
        document.head.appendChild(style);

        fetchOrders();
        fetchDesigns();

        return () => {
            document.head.removeChild(style);
        };
    }, []);

    const fetchDesigns = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/disenos/`);
            if (!response.ok) {
                throw new Error('Error al cargar los diseños');
            }
            const data = await response.json();
            setDesigns(data);
        } catch (err) {
            setError('Error al cargar los diseños: ' + err.message);
        }
    };

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/cortinas/`);
            if (!response.ok) {
                throw new Error('Error al cargar las órdenes');
            }
            const data = await response.json();
            setOrders(data);
        } catch (err) {
            setError('Error al cargar las órdenes: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleFilterSubmit = (e) => {
        e.preventDefault();
        fetchOrders();
    };

    const handleStateChange = async (orderId, newState) => {
        try {
            setLoading(true);
            
            const getResponse = await fetch(`${API_BASE_URL}/api/v1/cortinas/${orderId}`);
            if (!getResponse.ok) {
                throw new Error('Error al obtener la orden');
            }
            const currentOrder = await getResponse.json();
    
            const updatedOrder = {
                id: orderId,
                diseno_id: parseInt(currentOrder.diseno_id),
                ancho: parseFloat(currentOrder.ancho),
                alto: parseFloat(currentOrder.alto),
                partida: Boolean(currentOrder.partida),
                multiplicador: parseInt(currentOrder.multiplicador || 1),
                estado: newState,
                costo_total: parseFloat(currentOrder.costo_total),
                materiales: currentOrder.materiales?.map(material => ({
                    tipo_insumo_id: parseInt(material.tipo_insumo_id),
                    referencia_id: parseInt(material.referencia_id),
                    color_id: parseInt(material.color_id)
                })) || []
            };
    
            console.log('Datos enviados:', JSON.stringify(updatedOrder, null, 2));
    
            const response = await fetch(`${API_BASE_URL}/api/v1/cortinas/${orderId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedOrder)
            });
    
            const responseData = await response.json();
            console.log('Respuesta del servidor:', responseData);
    
            if (!response.ok) {
                throw new Error(responseData.detail || 'Error al actualizar el estado');
            }
    
            fetchOrders();
        } catch (err) {
            console.error('Error completo:', err);
            setError('Error al actualizar el estado: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const getDesignName = (designId) => {
        const design = designs.find(d => d.id === designId);
        return design ? design.nombre : 'Diseño no encontrado';
    };

    const handleViewDetails = async (order) => {
        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/rentabilidad/calcular-precio/${order.id}?rentabilidad=0.3`
            );
            if (!response.ok) {
                throw new Error('Error al obtener detalles de rentabilidad');
            }
            const rentabilidadData = await response.json();
            setSelectedOrder({
                ...order,
                rentabilidad: rentabilidadData
            });
        } catch (err) {
            setError('Error al cargar detalles: ' + err.message);
        }
    };

    return (
        <div className="container-fluid">
            <div className="card mb-4">
                <div className="card-header">
                    <h5 className="mb-0">Filtros de Búsqueda</h5>
                </div>
                <div className="card-body">
                    <form onSubmit={handleFilterSubmit}>
                        <div className="row g-3">
                            <div className="col-md-4">
                                <label className="form-label">Estado</label>
                                <select 
                                    name="estado" 
                                    className="form-select"
                                    value={filters.estado}
                                    onChange={handleFilterChange}
                                >
                                    <option value="">Todos</option>
                                    {orderStates.map(state => (
                                        <option 
                                            key={state.value} 
                                            value={state.value}
                                            style={{
                                                backgroundColor: state.backgroundColor,
                                                color: state.textColor
                                            }}
                                        >
                                            {state.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-md-4">
                                <label className="form-label">Fecha Inicio</label>
                                <input
                                    type="date"
                                    name="dateStart"
                                    className="form-control"
                                    value={filters.dateStart}
                                    onChange={handleFilterChange}
                                />
                            </div>
                            <div className="col-md-4">
                                <label className="form-label">Fecha Fin</label>
                                <input
                                    type="date"
                                    name="dateEnd"
                                    className="form-control"
                                    value={filters.dateEnd}
                                    onChange={handleFilterChange}
                                />
                            </div>
                        </div>
                        <div className="mt-3">
                            <button type="submit" className="btn btn-primary">
                                Aplicar Filtros
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div className="card">
                <div className="card-header">
                    <h5 className="mb-0">Listado de Órdenes</h5>
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
                        <div className="alert alert-info">No se encontraron órdenes</div>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Diseño</th>
                                        <th>Dimensiones</th>
                                        <th>Estado</th>
                                        <th>Costo Total</th>
                                        <th>Fecha</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {orders.map(order => (
                                        <tr key={order.id}>
                                            <td>{order.id}</td>
                                            <td>{getDesignName(order.diseno_id)}</td>
                                            <td>{order.ancho}cm × {order.alto}cm</td>
                                            <td>
                                                <select
                                                    className="form-select form-select-sm"
                                                    value={order.estado}
                                                    onChange={(e) => handleStateChange(order.id, e.target.value)}
                                                    style={{
                                                        width: 'auto',
                                                        display: 'inline-block',
                                                        fontWeight: 'bold',
                                                        backgroundColor: orderStates.find(s => s.value === order.estado)?.backgroundColor,
                                                        color: orderStates.find(s => s.value === order.estado)?.textColor,
                                                        cursor: 'pointer',
                                                        padding: '0.25rem 2rem 0.25rem 0.5rem'
                                                    }}
                                                >
                                                    {orderStates.map(state => (
                                                        <option 
                                                            key={state.value} 
                                                            value={state.value}
                                                            style={{
                                                                backgroundColor: state.backgroundColor,
                                                                color: state.textColor
                                                            }}
                                                        >
                                                            {state.label}
                                                        </option>
                                                    ))}
                                                </select>
                                            </td>
                                            <td>${order.costo_total?.toLocaleString()}</td>
                                            <td>{new Date(order.fecha_creacion).toLocaleDateString()}</td>
                                            <td>
                                                <button
                                                    className="btn btn-sm btn-info"
                                                    onClick={() => handleViewDetails(order)}
                                                    data-bs-toggle="modal"
                                                    data-bs-target="#orderDetailsModal"
                                                >
                                                    Ver Detalles
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

            {selectedOrder && (
                <div className="modal fade" id="orderDetailsModal" tabIndex="-1">
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Detalles de la Orden #{selectedOrder.id}</h5>
                                <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div className="modal-body">
                                <div className="row">
                                    <div className="col-md-6">
                                        <h6>Información General</h6>
                                        <p><strong>Diseño:</strong> {getDesignName(selectedOrder.diseno_id)}</p>
                                        <p><strong>Dimensiones:</strong> {selectedOrder.ancho}cm × {selectedOrder.alto}cm</p>
                                        <p><strong>Estado:</strong> {selectedOrder.estado}</p>
                                        <p><strong>Fecha:</strong> {new Date(selectedOrder.fecha_creacion).toLocaleString()}</p>
                                    </div>
                                    <div className="col-md-6">
                                        <h6>Información de Costos</h6>
                                        <p><strong>Costo Total:</strong> ${selectedOrder.costo_total?.toLocaleString()}</p>
                                        {selectedOrder.rentabilidad && (
                                            <>
                                                <p><strong>Precio Sugerido:</strong> ${selectedOrder.rentabilidad.precio_venta_sugerido?.toLocaleString()}</p>
                                                <p><strong>Margen:</strong> ${selectedOrder.rentabilidad.margen_ganancia?.toLocaleString()}</p>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">
                                    Cerrar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default OrdersList;