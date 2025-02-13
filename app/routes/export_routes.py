from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import pandas as pd
import io

from ..database import get_db
from ..crud.cortina_crud import get_cortinas
from ..crud.diseno_crud import get_diseno

router = APIRouter(
    prefix="/export",
    tags=["exportar"]
)

@router.get("/cortinas/excel")
async def export_cortinas_to_excel(
    estado: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Exporta los datos de las cortinas a un archivo Excel.
    Permite filtrar por estado y rango de fechas.
    """
    # Obtener las cortinas con los filtros aplicados
    cortinas = await get_cortinas(
        db,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

    # Preparar los datos para el Excel
    data = []
    for cortina in cortinas:
        diseno = await get_diseno(db, cortina.diseno_id)
        
        data.append({
            'ID': cortina.id,
            'Cliente': cortina.cliente or 'N/A',
            'Teléfono': cortina.telefono or 'N/A',
            'Email': cortina.email or 'N/A',
            'Diseño': diseno.nombre if diseno else 'N/A',
            'Ancho (cm)': float(cortina.ancho),
            'Alto (cm)': float(cortina.alto),
            'Estado': cortina.estado,
            'Costo Materiales': float(cortina.costo_materiales),
            'Costo Mano de Obra': float(cortina.costo_mano_obra),
            'Costo Total': float(cortina.costo_total),
            'Fecha Creación': cortina.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'Fecha Actualización': cortina.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        })

    # Crear DataFrame y exportar a Excel
    df = pd.DataFrame(data)
    
    # Crear el archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Cortinas', index=False)
        
        # Obtener el objeto workbook y worksheet
        workbook = writer.book
        worksheet = writer.sheets['Cortinas']
        
        # Definir formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#007bff',
            'font_color': 'white',
            'border': 1
        })
        
        # Formato para moneda
        money_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        # Formato para fechas
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd hh:mm:ss',
            'border': 1
        })
        
        # Formato general para celdas
        cell_format = workbook.add_format({
            'border': 1
        })
        
        # Aplicar formatos
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
            # Configurar ancho de columnas
            worksheet.set_column(col_num, col_num, 15)
            
            # Aplicar formatos específicos por columna
            if value in ['Costo Materiales', 'Costo Mano de Obra', 'Costo Total']:
                worksheet.set_column(col_num, col_num, 15, money_format)
            elif value in ['Fecha Creación', 'Fecha Actualización']:
                worksheet.set_column(col_num, col_num, 20, date_format)
            else:
                worksheet.set_column(col_num, col_num, 15, cell_format)

    # Preparar la respuesta
    output.seek(0)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"cortinas_export_{timestamp}.xlsx"
    
    # Devolver el archivo
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    return Response(
        content=output.getvalue(),
        headers=headers,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )