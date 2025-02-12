import React, { useState, useEffect } from 'react';

function MaterialReferenceManager() {
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const [references, setReferences] = useState([]);
  const [materialTypes, setMaterialTypes] = useState([]);
  const [formData, setFormData] = useState({
    tipo_insumo_id: '',
    codigo: '',
    nombre: '',
    precio_unitario: ''
  });
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    fetchReferences();
    fetchMaterialTypes();
  }, []);

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

  const resetForm = () => {
    setFormData({
      tipo_insumo_id: '',
      codigo: '',
      nombre: '',
      precio_unitario: ''
    });
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage('');

    const referenceData = {
      ...formData,
      tipo_insumo_id: parseInt(formData.tipo_insumo_id),
      precio_unitario: parseFloat(formData.precio_unitario)
    };

    try {
      const url = editingId 
        ? `${API_BASE_URL}/api/v1/referencias/${editingId}`
        : `${API_BASE_URL}/api/v1/referencias/`;
      
      const response = await fetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(referenceData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar la referencia');
      }

      setSuccessMessage(`Referencia ${editingId ? 'actualizada' : 'creada'} exitosamente`);
      resetForm();
      fetchReferences();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (reference) => {
    setFormData({
      tipo_insumo_id: reference.tipo_insumo_id.toString(),
      codigo: reference.codigo,
      nombre: reference.nombre,
      precio_unitario: reference.precio_unitario.toString()
    });
    setEditingId(reference.id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar esta referencia? Esta acción no se puede deshacer.')) {
      return;
    }

    setError(null);
    setSuccessMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/referencias/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'No se puede eliminar la referencia');
      }

      setSuccessMessage('Referencia eliminada exitosamente');
      fetchReferences();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="row">
      <div className="col-md-4">
        <div className="card shadow">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">
              {editingId ? 'Editar Referencia' : 'Nueva Referencia'}
            </h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="tipo_insumo_id" className="form-label">Tipo de Insumo</label>
                <select
                  className="form-select"
                  id="tipo_insumo_id"
                  name="tipo_insumo_id"
                  value={formData.tipo_insumo_id}
                  onChange={handleChange}
                  required
                >
                  <option value="">Seleccione un tipo</option>
                  {materialTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <label htmlFor="codigo" className="form-label">Código</label>
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
                <label htmlFor="nombre" className="form-label">Nombre</label>
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

              <div className="mb-3">
                <label htmlFor="precio_unitario" className="form-label">Precio Unitario</label>
                <input
                  type="number"
                  className="form-control"
                  id="precio_unitario"
                  name="precio_unitario"
                  value={formData.precio_unitario}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="d-grid gap-2">
                <button type="submit" className="btn btn-primary">
                  {editingId ? 'Actualizar' : 'Crear'} Referencia
                </button>
                {editingId && (
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={resetForm}
                  >
                    Cancelar Edición
                  </button>
                )}
              </div>
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
            <h3 className="card-title mb-0">Referencias Existentes</h3>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nombre</th>
                    <th>Tipo</th>
                    <th>Precio</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {references.map(reference => (
                    <tr key={reference.id}>
                      <td>{reference.codigo}</td>
                      <td>{reference.nombre}</td>
                      <td>
                        {materialTypes.find(t => t.id === reference.tipo_insumo_id)?.nombre}
                      </td>
                      <td>${reference.precio_unitario.toLocaleString()}</td>
                      <td>
                        <button
                          className="btn btn-sm btn-warning me-2"
                          onClick={() => handleEdit(reference)}
                        >
                          Editar
                        </button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDelete(reference.id)}
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

export default MaterialReferenceManager;