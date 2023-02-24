QueryListCompanies = """
SELECT codigo_empresa as codeCompany, 
    nombre_razon_social as legalNameCompany, 
    nombre_corto  as shortNameCompany
FROM db_admon.empresa;
"""

QueryListStateEmployee = """
SELECT codigo_estado_empleado as codeStateEmployee, 
   nombre as description 
FROM systesoreria.db_rrhh.estado_empleado;
"""
QueryGetPhoto = """ 
SELECT cui, foto FROM systesoreria.db_rrhh.persona  WHERE foto IS NOT NULL 
"""

QueryEmployee ="""
SELECT
    empresa.codigo_empresa codeCompany,
    empresa.nombre_corto as shortNameCompany,
    empresa.nombre_razon_social as legalNameCompany,
    empresa.nombre_comercial comericalName,
    persona.cui as documentId, 
    persona.nombre_completo as fullNamePerson, 
    persona.direccion_residencia as addressPerson,
    empleado.codigo_empresa codeCompanyEmployee,
    empleado.codigo_estado as codeState,
    estado.nombre as stateDescription,
    empleado.codigo_empleado as codeEmployee,
    area.nombre as areaDescription,
    seccion.nombre as sectionDescription,
    ubicacion.nombre as ubicationDescription,
    puesto.nombre as jobDescription,
    jornada.nombre as workDayDescription,
    empleado.fecha_ingreso as dateEntry,
    empleado.fecha_egreso as dateEgress
    --persona.foto as photoEmployee
    
FROM systesoreria.db_rrhh.empleado empleado
    LEFT JOIN systesoreria.db_admon.empresa empresa
    ON empleado.codigo_empresa = empresa.codigo_empresa
    
    LEFT JOIN systesoreria.db_rrhh.estado_empleado estado
    ON empleado.codigo_estado = estado.codigo_estado_empleado
    
    LEFT JOIN systesoreria.db_rrhh.persona persona
    ON empleado.cui = persona.cui
    
    LEFT JOIN systesoreria.db_rrhh.area area
    ON empleado.codigo_area = area.codigo_area
    
    LEFT JOIN systesoreria.db_rrhh.seccion seccion
    ON empleado.codigo_seccion = seccion.codigo_seccion
    
    LEFT JOIN systesoreria.db_rrhh.ubicacion ubicacion
    ON empleado.codigo_ubicacion = ubicacion.codigo_ubicacion

    LEFT JOIN systesoreria.db_rrhh.puesto puesto
    ON empleado.codigo_puesto = puesto.codigo_puesto

    LEFT JOIN systesoreria.db_rrhh.jornada jornada
    ON empleado.codigo_jornada = jornada.codigo_jornada

    ORDER BY persona.nombre_completo            
        """