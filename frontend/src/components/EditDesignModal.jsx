import React, { useState, useEffect } from 'react';

const EditDesignModal = ({ design, materialTypes, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    costo_mano_obra: '',
    tipos_insumo: []
  });

  useEffect(() => {
    if (design) {
      setFormData({
        costo_mano_obra: design.costo_mano_obra.toString(),
        tipos_insumo: design.tipos_insumo.map(tipo => ({
          ...tipo,
          tipo_insumo_id: tipo.tipo_insumo_id.toString(),
          cantidad_por_metro: tipo.cantidad_por_metro.toString()
        }))
      });
    }
  }, [design]);

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

  const handleSubmit = (e) => {
    e.preventDefault();
    const updatedDesign = {
      ...design,
      costo_mano_obra: parseFloat(formData.costo_mano_obra),
      tipos_insumo: formData.tipos_insumo.map(tipo => ({
        ...tipo,
        tipo_insumo_id: parseInt(tipo.tipo_insumo_id),
        cantidad_por_metro: parseFloat(tipo.cantidad_por_metro)
      }))
    };
    onSave(updatedDesign);
  };

  if (!design || !materialTypes) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      overflowY: 'auto',
      padding: '20px',
      zIndex: 1050,
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        width: '100%',
        maxWidth: '800px',
        margin: '20px auto',
        position: 'relative'
      }}
      onClick={e => e.stopPropagation()}>
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Editar Diseño: {design.nombre}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <div className="mb-3">
                <label className="form-label">Costo de Mano de Obra</label>
                <input
                  type="number"
                  className="form-control"
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
                          value={tipo.descripcion || ''}
                          onChange={(e) => handleMaterialTypeChange(index, 'descripcion', e.target.value)}
                        />
                      </div>

                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => removeMaterialType(index)}
                      >
                        Eliminar Material
                      </button>
                    </div>
                  </div>
                ))}

                <button
                  type="button"
                  className="btn btn-secondary w-100"
                  onClick={addMaterialType}
                >
                  Agregar Material
                </button>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary">
                Guardar Cambios
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditDesignModal;