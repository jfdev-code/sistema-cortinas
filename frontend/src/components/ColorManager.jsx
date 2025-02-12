import React, { useState, useEffect } from 'react';


function ColorManager() {
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const [colors, setColors] = useState([]);
  const [references, setReferences] = useState([]);
  const [formData, setFormData] = useState({
    referencia_id: '',
    codigo: '',
    nombre: ''
  });
  const [selectedReference, setSelectedReference] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchReferences();
  }, []);

  useEffect(() => {
    if (selectedReference) {
      fetchColorsByReference(selectedReference);
    }
  }, [selectedReference]);

  const fetchReferences = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/referencias/`);
      if (!response.ok) throw new Error('Error al cargar referencias');
      const data = await response.json();
      setReferences(data);
    } catch (err) {
      setError('Error al cargar las referencias: ' + err.message);
    }
  };

  const fetchColorsByReference = async (referenceId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/colores/referencia/${referenceId}`);
      if (!response.ok) throw new Error('Error al cargar colores');
      const data = await response.json();
      setColors(data);
    } catch (err) {
      setError('Error al cargar los colores: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReferenceChange = (e) => {
    const referenceId = e.target.value;
    setSelectedReference(referenceId);
    setFormData(prev => ({
      ...prev,
      referencia_id: referenceId
    }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/colores/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear color');
      }

      setSuccessMessage('Color creado exitosamente');
      setFormData(prev => ({
        ...prev,
        codigo: '',
        nombre: ''
      }));
      
      if (selectedReference) {
        fetchColorsByReference(selectedReference);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (colorId) => {
    if (!window.confirm('¿Está seguro de eliminar este color? Esta acción no se puede deshacer.')) {
      return;
    }

    setError(null);
    setSuccessMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/colores/${colorId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'No se puede eliminar el color');
      }

      setSuccessMessage('Color eliminado exitosamente');
      
      if (selectedReference) {
        fetchColorsByReference(selectedReference);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getReferenceNameById = (id) => {
    const reference = references.find(ref => ref.id === parseInt(id));
    return reference ? `${reference.codigo} - ${reference.nombre}` : '';
  };

  return (
    <div className="row">
      <div className="col-md-4">
        <div className="card shadow">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">Nuevo Color</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="referencia_id" className="form-label">Referencia</label>
                <select
                  className="form-select"
                  id="referencia_id"
                  name="referencia_id"
                  value={formData.referencia_id}
                  onChange={handleReferenceChange}
                  required
                >
                  <option value="">Seleccione una referencia</option>
                  {references.map(ref => (
                    <option key={ref.id} value={ref.id}>
                      {ref.codigo} - {ref.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <label htmlFor="codigo" className="form-label">Código del Color</label>
                <input
                  type="text"
                  className="form-control"
                  id="codigo"
                  name="codigo"
                  value={formData.codigo}
                  onChange={handleChange}
                  required
                  pattern="[A-Za-z0-9-]+"
                  title="Solo letras, números y guiones"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="nombre" className="form-label">Nombre del Color</label>
                <input
                  type="text"
                  className="form-control"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary w-100"
                disabled={loading}
              >
                {loading ? 'Creando...' : 'Crear Color'}
              </button>
            </form>

            {error && (
              <div className="alert alert-danger mt-3">
                {error}
              </div>
            )}

            {successMessage && (
              <div className="alert alert-success mt-3">
                {successMessage}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="col-md-8">
        <div className="card shadow">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">
              {selectedReference 
                ? `Colores de ${getReferenceNameById(selectedReference)}`
                : 'Seleccione una referencia para ver sus colores'}
            </h3>
          </div>
          <div className="card-body">
            {!selectedReference ? (
              <div className="alert alert-info">
                Seleccione una referencia para ver sus colores disponibles
              </div>
            ) : loading ? (
              <div className="text-center p-4">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
              </div>
            ) : colors.length === 0 ? (
              <div className="alert alert-warning">
                No hay colores registrados para esta referencia
              </div>
            ) : (
              <div className="row row-cols-1 row-cols-md-3 g-4">
                {colors.map(color => (
                  <div key={color.id} className="col">
                    <div className="card h-100">
                      <div className="card-body">
                        <h5 className="card-title">{color.nombre}</h5>
                        <h6 className="card-subtitle mb-2 text-muted">
                          Código: {color.codigo}
                        </h6>
                        <div className="d-flex justify-content-between align-items-center mt-3">
                          <span className="text-muted small">
                            {new Date(color.fecha_creacion).toLocaleDateString()}
                          </span>
                          <div>
                            <button 
                              className="btn btn-sm btn-outline-primary me-2"
                              onClick={() => fetchColorsByReference(selectedReference)}
                            >
                              Actualizar
                            </button>
                            <button 
                              className="btn btn-sm btn-outline-danger"
                              onClick={() => handleDelete(color.id)}
                            >
                              Eliminar
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ColorManager;