import React, { useState, useEffect } from 'react';
import EditDesignModal from './EditDesignModal';

function DesignManager() {
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const [designs, setDesigns] = useState([]);
  const [materialTypes, setMaterialTypes] = useState([]);
  const [formData, setFormData] = useState({
    id_diseno: '',
    nombre: '',
    descripcion: '',
    costo_mano_obra: '',
    tipos_insumo: [{ tipo_insumo_id: '', cantidad_por_metro: '', descripcion: '' }]
  });
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [editingDesign, setEditingDesign] = useState(null);

  useEffect(() => {
    fetchDesigns();
    fetchMaterialTypes();
  }, []);

  const fetchDesigns = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/disenos/`);
      if (!response.ok) throw new Error('Error al cargar diseños');
      const data = await response.json();
      setDesigns(data);
    } catch (err) {
      setError('Error al cargar los diseños: ' + err.message);
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

  const handleMaterialTypeChange = (index, field, value) => {
    setFormData(prev => {
      const newTiposInsumo = [...prev.tipos_insumo];
      newTiposInsumo[index] = {
        ...newTiposInsumo[index],
        [field]: value
      };
      return { ...prev, tipos_insumo: newTiposInsumo };
    });
  };

  const addMaterialType = () => {
    setFormData(prev => ({
      ...prev,
      tipos_insumo: [
        ...prev.tipos_insumo,
        { tipo_insumo_id: '', cantidad_por_metro: '', descripcion: '' }
      ]
    }));
  };

  const removeMaterialType = (index) => {
    setFormData(prev => ({
      ...prev,
      tipos_insumo: prev.tipos_insumo.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage('');

    try {
      const designData = {
        ...formData,
        costo_mano_obra: parseFloat(formData.costo_mano_obra),
        tipos_insumo: formData.tipos_insumo.map(tipo => ({
          ...tipo,
          tipo_insumo_id: parseInt(tipo.tipo_insumo_id),
          cantidad_por_metro: parseFloat(tipo.cantidad_por_metro)
        }))
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/disenos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(designData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear diseño');
      }

      setSuccessMessage('Diseño creado exitosamente');
      setFormData({
        id_diseno: '',
        nombre: '',
        descripcion: '',
        costo_mano_obra: '',
        tipos_insumo: [{ tipo_insumo_id: '', cantidad_por_metro: '', descripcion: '' }]
      });
      fetchDesigns();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (design) => {
    console.log('Diseño a editar:', design); // Para depuración
    setEditingDesign({
      ...design,
      tipos_insumo: design.tipos_insumo.map(tipo => ({
        ...tipo,
        tipo_insumo_id: tipo.tipo_insumo_id.toString() // Aseguramos que sea string para los selects
      }))
    });
  };

  const handleSaveEdit = async (updatedDesign) => {
    setError(null);
    setSuccessMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/disenos/${updatedDesign.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedDesign)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al actualizar diseño');
      }

      setSuccessMessage('Diseño actualizado exitosamente');
      setEditingDesign(null);
      fetchDesigns();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="row">
      <div className="col-md-5">
        <div className="card shadow">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">Nuevo Diseño</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="id_diseno" className="form-label">Código del Diseño</label>
                <input
                  type="text"
                  className="form-control"
                  id="id_diseno"
                  name="id_diseno"
                  value={formData.id_diseno}
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
                <label htmlFor="descripcion" className="form-label">Descripción</label>
                <textarea
                  className="form-control"
                  id="descripcion"
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleChange}
                  rows="3"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="costo_mano_obra" className="form-label">Costo de Mano de Obra</label>
                <input
                  type="number"
                  className="form-control"
                  id="costo_mano_obra"
                  name="costo_mano_obra"
                  value={formData.costo_mano_obra}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Materiales Necesarios</label>
                {formData.tipos_insumo.map((tipo, index) => (
                  <div key={index} className="card mb-3">
                    <div className="card-body">
                      <div className="mb-2">
                        <label className="form-label">Tipo de Insumo</label>
                        <select
                          className="form-select"
                          value={tipo.tipo_insumo_id}
                          onChange={(e) => handleMaterialTypeChange(index, 'tipo_insumo_id', e.target.value)}
                          required
                        >
                          <option value="">Seleccione un tipo</option>
                          {materialTypes.map(mt => (
                            <option key={mt.id} value={mt.id}>
                              {mt.nombre}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="mb-2">
                        <label className="form-label">Cantidad por Metro</label>
                        <input
                          type="number"
                          className="form-control"
                          value={tipo.cantidad_por_metro}
                          onChange={(e) => handleMaterialTypeChange(index, 'cantidad_por_metro', e.target.value)}
                          required
                          min="0"
                          step="0.01"
                        />
                      </div>

                      <div className="mb-2">
                        <label className="form-label">Descripción</label>
                        <input
                          type="text"
                          className="form-control"
                          value={tipo.descripcion}
                          onChange={(e) => handleMaterialTypeChange(index, 'descripcion', e.target.value)}
                        />
                      </div>

                      {index > 0 && (
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => removeMaterialType(index)}
                        >
                          Eliminar Material
                        </button>
                      )}
                    </div>
                  </div>
                ))}

                <button
                  type="button"
                  className="btn btn-secondary w-100 mb-3"
                  onClick={addMaterialType}
                >
                  Agregar Material
                </button>
              </div>

              <button type="submit" className="btn btn-primary w-100">
                Crear Diseño
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

      <div className="col-md-7">
        <div className="card shadow">
          <div className="card-header bg-primary text-white">
            <h3 className="card-title mb-0">Diseños Existentes</h3>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    <th>Costo MO</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {designs.map(design => (
                    <tr key={design.id}>
                      <td>{design.id_diseno}</td>
                      <td>{design.nombre}</td>
                      <td>{design.descripcion}</td>
                      <td>${design.costo_mano_obra.toLocaleString()}</td>
                      <td>
                        <button
                          type="button"
                          className="btn btn-sm btn-warning me-2"
                          onClick={() => handleEdit(design)}
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          className="btn btn-sm btn-info"
                          data-bs-toggle="modal"
                          data-bs-target={`#materialsModal${design.id}`}
                        >
                          Ver Materiales
                        </button>

                        <div className="modal fade" id={`materialsModal${design.id}`} tabIndex="-1">
                          <div className="modal-dialog">
                            <div className="modal-content">
                              <div className="modal-header">
                                <h5 className="modal-title">Materiales - {design.nombre}</h5>
                                <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
                              </div>
                              <div className="modal-body">
                                <table className="table table-sm">
                                  <thead>
                                    <tr>
                                      <th>Material</th>
                                      <th>Cantidad/m</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {design.tipos_insumo.map((tipo, idx) => (
                                      <tr key={idx}>
                                        <td>{materialTypes.find(mt => mt.id === tipo.tipo_insumo_id)?.nombre}</td>
                                        <td>{tipo.cantidad_por_metro}</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Edición */}
      {editingDesign && (
        <EditDesignModal
          design={editingDesign}
          materialTypes={materialTypes}
          onSave={handleSaveEdit}
          onClose={() => setEditingDesign(null)}
        />
      )}
    </div>
  );
}

export default DesignManager;