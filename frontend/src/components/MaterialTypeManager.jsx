import React, { useState, useEffect } from 'react';

function MaterialTypeManager() {
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const [materialTypes, setMaterialTypes] = useState([]);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: ''
  });
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchMaterialTypes();
  }, []);

  const fetchMaterialTypes = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/tipos-insumo/`);
      if (!response.ok) throw new Error('Error al cargar tipos de insumo');
      const data = await response.json();
      setMaterialTypes(data);
    } catch (err) {
      setError('Error al cargar los tipos de insumo: ' + err.message);
    }
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

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/tipos-insumo/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Error al crear tipo de insumo');

      setFormData({ nombre: '', descripcion: '' });
      setSuccessMessage('Tipo de insumo creado exitosamente');
      fetchMaterialTypes();
    } catch (err) {
      setError('Error al crear el tipo de insumo: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar este tipo de insumo? Esta acción no se puede deshacer.')) {
      return;
    }

    setError(null);
    setSuccessMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/tipos-insumo/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'No se puede eliminar el tipo de insumo');
      }

      setSuccessMessage('Tipo de insumo eliminado exitosamente');
      fetchMaterialTypes();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="row">
      <div className="col-md-4">
        <div className="card">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">Nuevo Tipo de Insumo</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="nombre" className="form-label">Nombre</label>
                <input
                  type="text"
                  className="form-control"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                  minLength="3"
                  maxLength="100"
                />
              </div>
              <div className="mb-3">
                <label htmlFor="descripcion" className="form-label">Descripción</label>
                <textarea
                  className="form-control"
                  id="descripcion"
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleChange}
                  rows="3"
                  maxLength="500"
                />
              </div>
              <button type="submit" className="btn btn-primary w-100">
                Crear Tipo de Insumo
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
        <div className="card">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">Tipos de Insumo Existentes</h3>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    <th>Fecha Creación</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {materialTypes.map(type => (
                    <tr key={type.id}>
                      <td>{type.id}</td>
                      <td>{type.nombre}</td>
                      <td>{type.descripcion}</td>
                      <td>{new Date(type.fecha_creacion).toLocaleDateString()}</td>
                      <td>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(type.id)}
                        >
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MaterialTypeManager;