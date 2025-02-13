import React, { useState, useEffect } from 'react';

const CurtainCalculator = () => {
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  
  // Estado principal para controlar todos los datos del formulario
  const [formData, setFormData] = useState({
    diseno_id: '',
    ancho: '',
    alto: '',
    cliente: '',
    telefono: '',
    email: '',
    partida: false,
    multiplicador: 1,
    materiales: [] // Almacenará la selección de materiales para cada tipo requerido
  });

  // Estados para manejar los datos y la interfaz
  const [disenos, setDisenos] = useState([]); // Lista de diseños disponibles
  const [selectedDesign, setSelectedDesign] = useState(null); // Diseño seleccionado actual
  const [referencias, setReferencias] = useState({}); // Referencias por tipo de insumo
  const [colores, setColores] = useState({}); // Colores por referencia
  const [tiposInsumo, setTiposInsumo] = useState({}); // Tipos de insumo por diseño
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [quotationDetails, setQuotationDetails] = useState(null);

  // Cargar la lista de diseños al montar el componente
  useEffect(() => {
    fetchDisenos();
  }, []);

  // Función para cargar los diseños disponibles
  const fetchDisenos = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/disenos/`);
      if (!response.ok) throw new Error('Error al cargar diseños');
      const data = await response.json();
      setDisenos(data);
    } catch (err) {
      setError('Error al cargar los diseños: ' + err.message);
    }
  };

  // Función para obtener los detalles de un diseño específico
  const fetchDisenoDetails = async (disenoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/disenos/${disenoId}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
  
      const result = await response.json();
      
      console.log('Design details:', result);
  
      // Robust error checking
      if (!result || !result.tipos_insumo) {
        throw new Error('Invalid design data structure');
      }
  
      setSelectedDesign(result);
  
      // Updated mapping to match backend response
      setFormData(prev => ({
        ...prev,
        diseno_id: result.id,
        materiales: result.tipos_insumo.map(tipo => ({
          tipo_insumo_id: tipo.tipo_insumo_id,
          referencia_id: '',
          color_id: ''
        }))
      }));
  
    } catch (err) {
      console.error("Error fetching design details:", err);
      setError(`Error al cargar los detalles del diseño: ${err.message}`);
    }
  };

  useEffect(() => {
    const fetchTiposInsumo = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/tipos-insumo/`);
        if (!response.ok) throw new Error('Error al cargar tipos de insumo');
        const data = await response.json();
        // Convertir el array a un objeto para búsqueda más fácil
        const tiposMap = data.reduce((acc, tipo) => {
          acc[tipo.id] = tipo;
          return acc;
        }, {});
        setTiposInsumo(tiposMap);
      } catch (err) {
        setError('Error al cargar los tipos de insumo: ' + err.message);
      }
    };

    fetchTiposInsumo();
  }, []);

  // Manejar el cambio de diseño seleccionado
  const handleDesignChange = async (e) => {
    const disenoId = e.target.value;
    if (!disenoId) {
      setSelectedDesign(null);
      setFormData(prev => ({
        ...prev,
        diseno_id: '',
        materiales: []
      }));
      return;
    }

    setLoading(true);
    await fetchDisenoDetails(disenoId);
    setLoading(false);
  };

  // Cargar referencias para un tipo de insumo específico
  const loadReferencias = async (tipoInsumoId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/referencias/tipo/${tipoInsumoId}`);
      if (!response.ok) throw new Error('Error al cargar referencias');
      const data = await response.json();
      setReferencias(prev => ({
        ...prev,
        [tipoInsumoId]: data
      }));
    } catch (err) {
      setError('Error al cargar referencias: ' + err.message);
    }
  };

  // Cargar colores para una referencia específica
  const loadColores = async (referenciaId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/colores/referencia/${referenciaId}`);
      if (!response.ok) throw new Error('Error al cargar colores');
      const data = await response.json();
      setColores(prev => ({
        ...prev,
        [referenciaId]: data
      }));
    } catch (err) {
      setError('Error al cargar colores: ' + err.message);
    }
  };

  // Manejar cambios en la selección de materiales
  const handleMaterialChange = async (index, field, value) => {
    const newMateriales = [...formData.materiales];
    newMateriales[index] = {
      ...newMateriales[index],
      [field]: value
    };

    // Si se cambió la referencia, cargar sus colores y resetear el color seleccionado
    if (field === 'referencia_id' && value) {
      await loadColores(value);
      newMateriales[index].color_id = '';
    }

    setFormData(prev => ({
      ...prev,
      materiales: newMateriales
    }));
  };

  // Manejar cambios genéricos en el formulario
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Función para validar el formulario antes de enviar
  const validateForm = () => {
    if (!formData.diseno_id || !formData.ancho || !formData.alto) {
      setError('Por favor complete todos los campos requeridos');
      return false;
    }

    // Verificar que todos los materiales tengan referencia y color seleccionados
    if (!formData.materiales.every(mat => mat.referencia_id && mat.color_id)) {
      setError('Por favor seleccione referencias y colores para todos los materiales');
      return false;
    }

    return true;
  };

  // Manejar el envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setQuotationDetails(null);
  
    // Extensive pre-submission validation and logging
    console.group('🔍 Form Submission Debug');
    console.log('Full Form Data:', formData);
  
    // Detailed form data validation
    console.log('Client Name:', formData.cliente);
    console.log('Client Phone:', formData.telefono);
    console.log('Client Email:', formData.email);
  
    if (!validateForm()) {
      console.warn('Form validation failed');
      console.groupEnd();
      return;
    }
  
    setLoading(true);
    try {
      // Comprehensive payload construction with detailed type conversion
      const payload = {
        diseno_id: parseInt(formData.diseno_id),
        ancho: parseFloat(formData.ancho),
        alto: parseFloat(formData.alto),
        cliente: formData.cliente || null,  // Explicitly handle potential undefined
        telefono: formData.telefono || null,
        email: formData.email || null,
        partida: formData.partida,
        multiplicador: parseInt(formData.multiplicador),
        tipos_insumo: formData.materiales.map(material => ({
          tipo_insumo_id: parseInt(material.tipo_insumo_id),
          referencia_id: parseInt(material.referencia_id),
          color_id: parseInt(material.color_id),
          cantidad_por_metro: 1
        })),
        notas: formData.notas || ""
      };
  
      console.log('Payload being sent:', payload);
  
      const response = await fetch(`${API_BASE_URL}/api/v1/cortinas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
  
      console.log('Response status:', response.status);
  
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Error al crear la cortina');
      }
  
      const result = await response.json();
      console.log('Full API Response:', result);
  
      setSuccess('Cortina creada exitosamente');
      
      // Enhanced quotation details setting
      setQuotationDetails({
        ...result,
        design_name: selectedDesign?.nombre || 'Diseño no especificado',
        cliente: result.cliente || 'No especificado',
        telefono: result.telefono || 'No especificado',
        email: result.email || 'No especificado'
      });
  
      console.log('Quotation Details:', {
        ...result,
        design_name: selectedDesign?.nombre || 'Diseño no especificado'
      });
  
    } catch (err) {
      console.error('Submission Error:', err);
      setError(`Error al crear la cortina: ${err.message}`);
    } finally {
      console.groupEnd();
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid">
      <div className="card shadow">
        <div className="card-header bg-primary text-white">
          <h3 className="mb-0">Cotizador de Cortinas</h3>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            {/* Selección de diseño */}
            <div className="mb-4">
              <label htmlFor="diseno" className="form-label">Diseño de Cortina</label>
              <select
                id="diseno"
                name="diseno_id"
                className="form-select"
                value={formData.diseno_id}
                onChange={handleDesignChange}
                required
              >
                <option value="">Seleccione un diseño</option>
                {disenos.map(diseno => (
                  <option key={diseno.id} value={diseno.id}>
                    {diseno.nombre}
                  </option>
                ))}
              </select>
            </div>
  
            {/* Mostrar dimensiones y materiales solo si hay un diseño seleccionado */}
            {selectedDesign && (
              <>
                {/* Dimensiones */}
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label htmlFor="ancho" className="form-label">Ancho (cm)</label>
                    <input
                      type="number"
                      className="form-control"
                      id="ancho"
                      name="ancho"
                      value={formData.ancho}
                      onChange={handleInputChange}
                      required
                      min="20"
                      max="500"
                      step="0.1"
                    />
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="alto" className="form-label">Alto (cm)</label>
                    <input
                      type="number"
                      className="form-control"
                      id="alto"
                      name="alto"
                      value={formData.alto}
                      onChange={handleInputChange}
                      required
                      min="20"
                      max="500"
                      step="0.1"
                    />
                  </div>
                </div>

                {/* Información del Cliente */}
                <div className="card mb-4">
                  <div className="card-header">
                    <h5 className="mb-0">Información del Cliente</h5>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-4 mb-3">
                        <label htmlFor="cliente" className="form-label">Nombre Completo</label>
                        <input
                          type="text"
                          className="form-control"
                          id="cliente"
                          name="cliente"
                          value={formData.cliente}
                          onChange={handleInputChange}
                          placeholder="Nombre del cliente"
                        />
                      </div>
                      <div className="col-md-4 mb-3">
                        <label htmlFor="telefono" className="form-label">Teléfono</label>
                        <input
                          type="tel"
                          className="form-control"
                          id="telefono"
                          name="telefono"
                          value={formData.telefono}
                          onChange={handleInputChange}
                          placeholder="Número de contacto"
                        />
                      </div>
                      <div className="col-md-4 mb-3">
                        <label htmlFor="email" className="form-label">Correo Electrónico</label>
                        <input
                          type="email"
                          className="form-control"
                          id="email"
                          name="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="Correo electrónico"
                        />
                      </div>
                    </div>
                  </div>
                </div>
  
                {/* Materiales requeridos */}
                <div className="card mb-4">
                  <div className="card-header">
                    <h5 className="mb-0">Materiales Requeridos</h5>
                  </div>
                  <div className="card-body">
                    {selectedDesign.tipos_insumo.map((tipoInsumo, index) => {
                      const tipoInsumoData = tiposInsumo[tipoInsumo.tipo_insumo_id];
                      const nombreTipoInsumo = tipoInsumoData ? tipoInsumoData.nombre : 'Tipo de Insumo';
                      
                      return (
                        <div key={index} className="mb-4 border-bottom pb-3">
                          <h6 className="text-primary mb-3">{nombreTipoInsumo}</h6>
                          <div className="ms-3">
                            {/* Selección de referencia */}
                            <div className="mb-2">
                              <select
                                className="form-select"
                                value={formData.materiales[index]?.referencia_id || ''}
                                onChange={(e) => handleMaterialChange(index, 'referencia_id', e.target.value)}
                                onFocus={() => {
                                  if (!referencias[tipoInsumo.tipo_insumo_id]) {
                                    loadReferencias(tipoInsumo.tipo_insumo_id);
                                  }
                                }}
                                required
                              >
                                <option value="">Seleccione {nombreTipoInsumo}</option>
                                {referencias[tipoInsumo.tipo_insumo_id]?.map(ref => (
                                  <option key={ref.id} value={ref.id}>
                                  {ref.codigo} - {ref.nombre}
                                </option>
                                ))}
                              </select>
                            </div>
  
                            {/* Selección de color (solo si hay referencia seleccionada) */}
                            {formData.materiales[index]?.referencia_id && (
                              <div className="mb-2">
                                <select
                                  className="form-select"
                                  value={formData.materiales[index]?.color_id || ''}
                                  onChange={(e) => handleMaterialChange(index, 'color_id', e.target.value)}
                                  required
                                >
                                  <option value="">Seleccione color para {nombreTipoInsumo}</option>
                                  {colores[formData.materiales[index].referencia_id]?.map(color => (
                                    <option key={color.id} value={color.id}>
                                      {color.codigo} - {color.nombre}
                                    </option>
                                  ))}
                                </select>
                              </div>
                            )}
  
                            {/* Información de cantidad requerida */}
                            <div className="form-text text-muted">
                              Cantidad requerida: {tipoInsumo.cantidad_por_metro} por metro de {nombreTipoInsumo.toLowerCase()}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
  
                {/* Opciones adicionales */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <label htmlFor="multiplicador" className="form-label">
                      Multiplicador
                    </label>
                    <input
                      type="number"
                      className="form-control"
                      id="multiplicador"
                      name="multiplicador"
                      value={formData.multiplicador}
                      onChange={handleInputChange}
                      required
                      min="1"
                      max="10"
                    />
                  </div>
  
                  <div className="col-12 mt-2">
                    <div className="form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="partida"
                        name="partida"
                        checked={formData.partida}
                        onChange={handleInputChange}
                      />
                      <label className="form-check-label" htmlFor="partida">
                        Cortina Partida
                      </label>
                    </div>
                  </div>
                </div>
  
                {/* Botón de envío */}
                <button 
                  type="submit" 
                  className="btn btn-primary w-100"
                  disabled={loading}
                >
                  {loading ? 'Calculando...' : 'Calcular Precio'}
                </button>
              </>
            )}
          </form>
  
          {/* Mensajes de error y éxito */}
          {error && (
            <div className="alert alert-danger mt-3">
              {error}
            </div>
          )}
  
          {success && (
            <div className="alert alert-success mt-3">
              {success}
            </div>
          )}
  
          {/* Resumen de cotización */}
          {quotationDetails && (
            <QuotationSummary details={quotationDetails} />
          )}
        </div>
      </div>
    </div>
  );
};

const QuotationSummary = ({ details }) => {
  console.log('QuotationSummary Received Details:', details);
  console.log('Client Name:', details?.cliente);
  console.log('Client Phone:', details?.telefono);
  console.log('Client Email:', details?.email);
  if (!details) return null;

  // Función auxiliar para formatear números como moneda
  const formatCurrency = (value) => {
    if (value == null) return '$0.00';
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 2
    }).format(value);
  };

  return (
    <div className="card mt-3">
      <div className="card-header bg-primary text-white">
        <h4>Resumen de Cotización</h4>
      </div>
      <div className="card-body">
        <div className="row">
          <div className="col-md-6">
            <h5>Detalles de la Cortina</h5>
            <p><strong>Diseño:</strong> {details.design_name}</p>
            <p><strong>Ancho:</strong> {details.ancho} cm</p>
            <p><strong>Alto:</strong> {details.alto} cm</p>
            <p><strong>Multiplicador:</strong> {details.multiplicador}</p>
            <p><strong>Cliente:</strong> {details.cliente || 'No especificado'}</p>
            <p><strong>Teléfono:</strong> {details.telefono || 'No especificado'}</p>
            <p><strong>Email:</strong> {details.email || 'No especificado'}</p>
          </div>
          <div className="col-md-6">
            <h5>Desglose de Costos</h5>
            <table className="table">
              <tbody>
                <tr className="table-success font-weight-bold">
                  <td><strong>Precio Final</strong></td>
                  <td><strong>{formatCurrency(details.costo_total)}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurtainCalculator;