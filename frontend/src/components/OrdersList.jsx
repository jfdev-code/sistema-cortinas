const fetchOrders = async () => {
    setLoading(true);
    try {
        // Construct query parameters
        const params = new URLSearchParams();
        
        // Add estado filter if selected
        if (filters.estado) {
            params.append('estado', filters.estado);
        }
        
        // // Add client filter with specific handling
        // if (filters.cliente && filters.cliente.trim() !== '') {
        //     // URL encode the client name to handle special characters
        //     params.append('cliente', encodeURIComponent(filters.cliente.trim()));
        // }
        
        // Add date range filters if provided
        if (filters.dateStart) {
            params.append('fecha_inicio', filters.dateStart);
        }
        
        if (filters.dateEnd) {
            params.append('fecha_fin', filters.dateEnd);
        }
        
        // Construct the full URL with query parameters
        const url = `${API_BASE_URL}/api/v1/cortinas/?${params.toString()}`;

        console.log('Fetching orders with URL:', url);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Error al cargar las órdenes');
        }
        const data = await response.json();
        
        // Optional: Log the filtered data for debugging
        console.log('Filtered orders:', data);
        
        setOrders(data);
    } catch (err) {
        console.error('Error en fetchOrders:', err);
        setError('Error al cargar las órdenes: ' + err.message);
    } finally {
        setLoading(false);
    }
};import React, { useState, useEffect } from 'react';

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
    },
    { 
        value: 'cancelado', 
        label: 'Cancelado', 
        backgroundColor: '#c21d1d', // Red  
        textColor: '#ffffff'      // White text
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
        // Construct query parameters
        const params = new URLSearchParams();
        
        // Add estado filter if selected
        if (filters.estado) {
            params.append('estado', filters.estado);
        }
        
        // Add date range filters if provided
        if (filters.dateStart) {
            params.append('fecha_inicio', filters.dateStart);
        }
        
        if (filters.dateEnd) {
            params.append('fecha_fin', filters.dateEnd);
        }
        
        // Construct the full URL with query parameters
        const url = `${API_BASE_URL}/api/v1/cortinas/?${params.toString()}`;

        const response = await fetch(url);
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

        // Prepare the update payload with existing client-related fields
        const updatedOrder = {
            estado: newState,
            cliente: currentOrder.cliente || '',
            telefono: currentOrder.telefono || '',
            email: currentOrder.email || ''
        };

        console.log('Datos enviados:', JSON.stringify(updatedOrder, null, 2));

        const response = await fetch(`${API_BASE_URL}/api/v1/cortinas/${orderId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedOrder)
        });

        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`Error al actualizar el estado: ${errorBody}`);
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
        // Log all keys in the order object to see what's available
        console.log('Order object keys:', Object.keys(order));
        console.log('Full order object:', JSON.stringify(order, null, 2));

        const rentabilidadResponse = await fetch(
            `${API_BASE_URL}/api/v1/rentabilidad/calcular-precio/${order.id}?rentabilidad=0.3`
        );
        if (!rentabilidadResponse.ok) {
            throw new Error('Error al obtener detalles de rentabilidad');
        }
        const rentabilidadData = await rentabilidadResponse.json();
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
                        <div className="col-md-3">
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
                        
                        <div className="col-md-2">
                            <label className="form-label">Fecha Inicio</label>
                            <input
                                type="date"
                                name="dateStart"
                                className="form-control"
                                value={filters.dateStart || ''}
                                onChange={handleFilterChange}
                            />
                        </div>
                        <div className="col-md-2">
                            <label className="form-label">Fecha Fin</label>
                            <input
                                type="date"
                                name="dateEnd"
                                className="form-control"
                                value={filters.dateEnd || ''}
                                onChange={handleFilterChange}
                            />
                        </div>
                        <div className="col-md-2 d-flex align-items-end">
                            <button type="submit" className="btn btn-primary">
                                Aplicar Filtros
                            </button>
                        </div>
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
                                    <th>Cliente</th>
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
                                        <td>{order.cliente || 'N/A'}</td>
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
                                <div className="col-md-12 mt-3">
                                    <h6>Información del Cliente</h6>
                                    <p><strong>Nombre:</strong> {
                                        
                                        selectedOrder.cliente || 
                                        'No disponible'
                                    }</p>
                                    <p><strong>Teléfono:</strong> {selectedOrder.telefono || 'No disponible'}</p>
                                    <p><strong>Email:</strong> {selectedOrder.email || 'No disponible'}</p>
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