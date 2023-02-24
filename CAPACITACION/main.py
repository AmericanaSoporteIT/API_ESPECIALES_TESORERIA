import os
import json
from flask import request, Response, jsonify
from constantes import *
from importlib_metadata import method_cache
from odbc import *
from serialization import *

from AppContext import app, cors


@app.route('/')
def index():
    html = '<a href="mssql">MSSQLSERVER</a><br><a href="mysql">MYSQL</a>'
    return html

@app.route('/api/especiales2/consultatrasladospordia', methods=['GET'])
def consulta_traslados_por_dia():
    try:
        fecha =  request.args.get('fecha')
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute(f"""
            SELECT  x.codigo_traslado, 
                DATE_FORMAT(x.fecha_operacion,'%d/%m/%Y') AS fecha_operacion,
                x.fecha_traslado,
                IFNULL((SELECT count(*) from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS numero_pedidos,
                IFNULL((SELECT sum(monto)  from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS monto_total,
                x.observaciones_traslado,
                x.codigo_estado,
                y.nombre AS estado,
                x.usuario_ing,
                DATE_FORMAT(x.fecha_ing,'%d/%m/%Y %H:%i:%s') AS fecha_ing,
                1 AS permiso_imprimir

            FROM inf_traslado_especiales2 x
                INNER JOIN inf_estado_traslado_especiales2 y
                ON x.codigo_estado = y.codigo_estado_traslado 
            WHERE x.codigo_estado <> {CODIGO_ESTADO_ANULADO}
              AND x.fecha_operacion = '{fecha}'
        """)

        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"observaciones_traslado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()          

    return jsonify(res)    

@app.route('/api/especiales2/trasladosgenerados', methods=['GET'])
def consulta_traslados_generados():
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute(f"""
            SELECT  x.codigo_traslado, 
                DATE_FORMAT(x.fecha_operacion,'%d/%m/%Y') AS fecha_operacion,
                x.fecha_traslado,
                IFNULL((SELECT count(*) from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS numero_pedidos,
                IFNULL((SELECT sum(monto)  from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS monto_total,
                x.observaciones_traslado,
                x.codigo_estado,
                y.nombre AS estado,
                x.usuario_ing,
                DATE_FORMAT(x.fecha_ing,'%d/%m/%Y %H:%i:%s') AS fecha_ing,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_anular,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_traslado,
                CASE
                    WHEN x.codigo_estado NOT IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_imprimir,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_editar,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_POR_RECEPCIONAR})  THEN 1
                    ELSE 0
                END AS permiso_actualizar,
                (SELECT sum(monto) AS monto_total_dia 
                 FROM inf_traslado_detalle_especiales2 
                 WHERE codigo_traslado IN ( SELECT codigo_traslado 
                                            FROM inf_traslado_especiales2  
                                            WHERE fecha_operacion = x.fecha_operacion) 
                                              AND estado = 1) AS monto_total_dia
                FROM inf_traslado_especiales2 x
                INNER JOIN inf_estado_traslado_especiales2 y
                ON x.codigo_estado = y.codigo_estado_traslado 
                WHERE x.codigo_estado IN ({CODIGO_ESTADO_GENERADO},{CODIGO_ESTADO_POR_RECEPCIONAR})
                  AND x.fecha_operacion >= CURDATE()
        """)

        cursor.commit()
        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"observaciones_traslado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()          

    return jsonify(res)    


@app.route('/api/especiales2/trasladosgeneradosconta', methods=['GET'])
def consulta_traslados_generados_contabilidad():
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute(f"""
        SELECT  x.codigo_traslado, 
                DATE_FORMAT(x.fecha_operacion,'%d/%m/%Y') AS fecha_operacion,
                x.fecha_traslado,
                IFNULL((SELECT count(*) from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS numero_pedidos,
                IFNULL((SELECT sum(monto)  from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS monto_total,
                x.observaciones_traslado,
                x.codigo_estado,
                y.nombre AS estado,
                x.usuario_ing,
                DATE_FORMAT(x.fecha_ing,'%d/%m/%Y %H:%i:%s') AS fecha_ing,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_anular,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_traslado,
                CASE
                    WHEN x.codigo_estado NOT IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_imprimir,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_GENERADO})  THEN 1
                    ELSE 0
                END AS permiso_editar,
                CASE
                    WHEN x.codigo_estado IN ({CODIGO_ESTADO_POR_RECEPCIONAR})  THEN 1
                    ELSE 0
                END AS permiso_actualizar

        FROM inf_traslado_especiales2 x
        INNER JOIN inf_estado_traslado_especiales2 y
        ON x.codigo_estado = y.codigo_estado_traslado
        WHERE x.codigo_estado IN ({CODIGO_ESTADO_GENERADO},{CODIGO_ESTADO_POR_RECEPCIONAR})
        """)

        cursor.commit()
        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"observaciones_traslado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()          

    return jsonify(res)        

@app.route('/api/especiales2/generar', methods=['POST'])
def generar_traslado_especiales2():
    res = None
    fecha = request.form.get('fecha')
    usuario = request.form.get('usuario')
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()

        numeroRegistros =  cursor.execute(f"""
            SELECT 
                count(*) AS registros
            FROM inf_pedido x
            LEFT JOIN inf_traslado_detalle_especiales2 y
                ON x.empresa = y.empresa AND x.serie = y.serie AND x.pedido = y.pedido
            WHERE x.qsys_vendedor = {332}
                AND x.fecha =  '{fecha}'
                AND x.credito = 0
                AND x.estado <> 9
                AND (y.empresa IS NULL AND y.serie IS NULL AND y.pedido IS NULL)
            """
        ).fetchone()[0]

        if numeroRegistros > 0:
            insertEncabezado = cursor.execute(f"""
                INSERT INTO inf_traslado_especiales2(
                    fecha_operacion,
                    fecha_traslado,
                    observaciones_traslado,
                    fecha_recepcion,
                    usuario_recepcion,
                    observaciones_recepcion,
                    codigo_estado,
                    usuario_ing,
                    fecha_ing,
                    usuario_act,
                    fecha_act
                )
                VALUES(
                    '{fecha}',
                    DEFAULT,
                    NULL,
                    DEFAULT,
                    NULL,
                    NULL,
                    1, 
                    '{usuario}',
                    NOW(),
                    NULL,
                    DEFAULT
                )
            """)

            codigoTraslado = cursor.execute("""SELECT LAST_INSERT_ID()""").fetchone()[0]

            insertDetalle = cursor.execute("""
                INSERT INTO inf_traslado_detalle_especiales2(
                    empresa,
                    serie,
                    pedido,
                    codigo_traslado,
                    codigo_cliente,
                    nombre_cliente,
                    nombre_cliente_depurado,
                    monto,
                    fecha_grabado,
                    estado,
                    usuario_ing,
                    fecha_ing,
                    usuario_act
                )
                SELECT
                    x.empresa,
                    x.serie,
                    x.pedido,
                    {0} AS codigo_traslado,
                    x.cliente AS codigo_cliente,
                    CASE
                      WHEN x.cliente = '000001' THEN UPPER(REPLACE(REPLACE(REPLACE(x.nombre,' ','<>'),'><',''),'<>',' '))
                      ELSE UPPER(REPLACE(REPLACE(REPLACE(z.nombre,' ','<>'),'><',''),'<>',' '))
    				END AS nombre_cliente,
                    CASE
                      WHEN x.cliente = '000001' THEN UPPER(REPLACE(REPLACE(REPLACE(x.nombre,' ','<>'),'><',''),'<>',' '))
                      ELSE UPPER(REPLACE(REPLACE(REPLACE(z.nombre,' ','<>'),'><',''),'<>',' '))
    				END AS nombre_cliente_depurado,
                    x.monto,
                    x.fecha_grabado,
                    1 AS estado,
                    '{1}' AS usuario_ing,
                    NOW() AS fecha_ing,
                    NULL AS usuario_act
                FROM inf_pedido x
                LEFT JOIN inf_traslado_detalle_especiales2 y
                    ON x.empresa = y.empresa AND x.serie = y.serie AND x.pedido = y.pedido
                LEFT JOIN cxc_cliente z
                    ON x.cliente = z.cliente AND x.empresa = z.empresa
                WHERE x.qsys_vendedor = {2}
                    AND x.fecha =  '{3}'
                    AND x.credito = 0
                    AND x.estado <> 9
                    AND (y.empresa IS NULL 
                            AND y.serie IS NULL 
                                AND y.pedido IS NULL
                    )
            """)
            
            cursor.commit()
            
            res = "GENERADO"
        else:
            res = "VACIO" 

    except pyodbc.Error as err:
        res = "Error [0]: " + err.args[1]
    except pyodbc.IntegrityError as e:
        res = "Error [1]: {}".format(e)
    except:     
        res = "Error [2]: "        
    finally:
        cursor.close()
        conn.close()     
    return res


@app.route('/api/especiales2/importaciones', methods=['GET'])
def consulta_traslados_para_importacion():
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute(f"""
            SELECT  x.codigo_traslado, 
                DATE_FORMAT(x.fecha_operacion,'%d/%m/%Y') AS fecha_operacion,
                x.fecha_traslado,
                IFNULL((SELECT count(*) FROM inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS numero_pedidos,
                IFNULL((SELECT sum(monto) FROM inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS monto_total,
                x.observaciones_traslado,
                x.codigo_estado,
                y.nombre AS estado,
                x.usuario_ing,
                DATE_FORMAT(x.fecha_ing,'%d/%m/%Y %H:%i:%s') AS fecha_ing,
                CASE
                    WHEN x.codigo_estado = {CODIGO_ESTADO_POR_RECEPCIONAR} THEN 1
                    ELSE 0
                END AS permiso_importar,
                CASE
                    WHEN (x.codigo_estado = {CODIGO_ESTADO_RECEPCIONADO} OR x.codigo_estado = {CODIGO_ESTADO_DEPURADO}) THEN 1
                    ELSE 0
                END AS permiso_depurar,
                CASE
                    WHEN x.codigo_estado = {CODIGO_ESTADO_DEPURADO} THEN 1
                    ELSE 0
                END AS permiso_registrar,
                CASE
                    WHEN (x.codigo_estado = {CODIGO_ESTADO_RECEPCIONADO} OR x.codigo_estado = {CODIGO_ESTADO_DEPURADO}) THEN 1
                    ELSE 0
                END AS permiso_editar,
                1 AS permiso_informacion
            FROM inf_traslado_especiales2 x
                INNER JOIN inf_estado_traslado_especiales2 y
                ON x.codigo_estado = y.codigo_estado_traslado
            WHERE x.codigo_estado in (
                {CODIGO_ESTADO_POR_RECEPCIONAR},
                    {CODIGO_ESTADO_RECEPCIONADO},
                        {CODIGO_ESTADO_DEPURADO}
            )
        """)

        cursor.commit()
        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"observaciones_traslado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()
        
    return jsonify(res)    


@app.route('/api/especiales2/importacionesporfecha', methods=['GET'])
def consulta_traslados_para_importacion_por_fecha():
    try:
        fecha =  request.args.get('fecha')
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute("""
        SELECT  x.codigo_traslado, 
                DATE_FORMAT(x.fecha_operacion,'%d/%m/%Y') AS fecha_operacion,
                x.fecha_traslado,
                IFNULL((SELECT count(*) from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS numero_pedidos,
                IFNULL((SELECT sum(monto)  from inf_traslado_detalle_especiales2 WHERE estado = 1 AND codigo_traslado = x.codigo_traslado GROUP BY codigo_traslado),0) AS monto_total,
                x.observaciones_traslado,
                x.codigo_estado,
                y.nombre AS estado,
                x.usuario_ing,
                DATE_FORMAT(x.fecha_ing,'%d/%m/%Y %H:%i:%s') AS fecha_ing,
                CASE
                    WHEN x.codigo_estado = {0} THEN 1
                    ELSE 0
                END AS permiso_importar,
                CASE
                    WHEN (x.codigo_estado = {1} OR x.codigo_estado = {2}) THEN 1
                    ELSE 0
                END AS permiso_depurar,
                CASE
                    WHEN x.codigo_estado = {2} THEN 1
                    ELSE 0
                END AS permiso_registrar,
                CASE
                    WHEN (x.codigo_estado = {1} OR x.codigo_estado = {2}) THEN 1
                    ELSE 0
                END AS permiso_editar,
                1 AS permiso_informacion
        FROM inf_traslado_especiales2 x
        INNER JOIN inf_estado_traslado_especiales2 y
        ON x.codigo_estado = y.codigo_estado_traslado
        WHERE x.codigo_estado in ({0},{1},{2})
          AND x.fecha_operacion = '{3}'""".format(CODIGO_ESTADO_POR_RECEPCIONAR, CODIGO_ESTADO_RECEPCIONADO, CODIGO_ESTADO_DEPURADO, fecha))

        cursor.commit()
        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"observaciones_traslado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"observaciones_traslado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()
        
    return jsonify(res)        


@app.route('/api/especiales2/detalletraslado', methods=['GET'])
def consulta_detalle_traslados():
    codigo =  request.args.get('codigo')
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute("""
        SELECT  empresa,
		        serie,
                pedido,
                codigo_traslado,
                codigo_cliente,
                nombre_cliente,
                nombre_cliente_depurado,
                monto,
                fecha_grabado
        FROM inf_traslado_detalle_especiales2
        WHERE codigo_traslado = {0}
          AND estado = 1""".format(codigo));

        cursor.commit()
        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"nombre_cliente_depurado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"nombre_cliente_depurado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"nombre_cliente_depurado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()        

    return jsonify(res)        

@app.route('/api/especiales2/detalletrasladoedicion', methods=['GET'])
def consulta_detalle_traslados_edicion():
    codigo =  request.args.get('codigo')
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute("""
        SELECT  empresa,
		        serie,
                pedido,
                codigo_traslado,
                codigo_cliente,
                nombre_cliente,
                nombre_cliente_depurado,
                monto,
                fecha_grabado,
                1 AS permiso_anular
        FROM inf_traslado_detalle_especiales2
        WHERE codigo_traslado = {0}
          AND estado = 1 
        ORDER BY fecha_grabado DESC""".format(codigo));

        cursor.commit()
        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"codigo_traslado": 0,"nombre_cliente_depurado": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"codigo_traslado": 0,"nombre_cliente_depurado": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"codigo_traslado": 0,"nombre_cliente_depurado": "Error 2"}]
    finally:
        cursor.close()
        conn.close()        

    return jsonify(res)            

@app.route('/api/especiales2/cambiarestado', methods=['PUT'])
def traslado_especiales2_cambiar_estado():
    codigo = request.form['codigo']
    estado = request.form['estado']
    res = None
    try:

        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute("""UPDATE inf_traslado_especiales2 SET codigo_estado = {0} WHERE codigo_traslado = {1}""".format(estado, codigo))
        cursor.commit()
        res = "OK"

    except pyodbc.Error as err:
        res = "Error [0]: " + err.args[1]
    except pyodbc.IntegrityError as e:
        res = "Error [1]: {}".format(e)
    except:     
        res = "Error [2]: "        
    finally:
        cursor.close()
        conn.close()                
     
    return res     


@app.route('/api/especiales2/eliminartraslado/<int:codigo>', methods=['DELETE'])
def eliminar_traslado_especiales2(codigo):
    res = None
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result1 = cursor.execute("""DELETE FROM inf_traslado_detalle_especiales2 WHERE codigo_traslado = {0}""".format(codigo))
        result2 = cursor.execute("""DELETE FROM inf_traslado_especiales2 WHERE codigo_traslado = {0}""".format(codigo))
        cursor.commit()
        res = "OK"

    except pyodbc.Error as err:
        res = "Error [0]: " + err.args[1]
    except pyodbc.IntegrityError as e:
        res = "Error [1]: {}".format(e)
    except:     
        res = "Error [2]: "        
    finally:
        cursor.close()
        conn.close()           

    return res     


@app.route('/api/especiales2/eliminardetalletraslado/<string:codigo>', methods=['DELETE'])
def eliminar_detalle_especiales2(codigo):
    res = None
    parametros = codigo.split(',')
    empresa = parametros[0]
    serie = parametros[1]
    pedido = parametros[2]
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result1 = cursor.execute("""DELETE FROM inf_traslado_detalle_especiales2 WHERE empresa = '{0}' AND serie = '{1}' AND pedido = {2}""".format(empresa,serie,pedido))
        cursor.commit()
        res = "OK"

    except pyodbc.Error as err:
        res = "Error [0]: " + err.args[1]
    except pyodbc.IntegrityError as e:
        res = "Error [1]: {}".format(e)
    except:     
        res = "Error [2]: "        
    finally:
        cursor.close()
        conn.close()           

    return res         


@app.route('/api/especiales2/modificaciondetalletrasladado', methods=['POST'])
def modificacion_detalle_trasladado():
    res = None
    codigo = request.form.get('codigo')
    usuario = request.form.get('usuario')
    try:
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()

        insertHistorialModificaciones =  cursor.execute(f"""
        INSERT INTO inf_traslado_especiales2_hist(empresa,serie,pedido,monto_modificado,monto_correcto,descripcion,estado,usuario_ing,fecha_ing)
        SELECT x.empresa, 
	           x.serie, 
	           x.pedido, 
	           x.monto AS monto_modificado,
	           cast(y.monto as decimal(18,2)) AS monto_correcto,
               CASE 
                 WHEN y.estado = 9 THEN 'Pedido anulado'
                 ELSE 'Monto modificado'
               END AS descripion,
	           1 AS estado,
	           '{usuario}' AS usuario_ing,
	           NOW() AS fecha_ing
        FROM inf_traslado_detalle_especiales2 x
        INNER JOIN inf_pedido y
        ON x.empresa = y.empresa AND x.serie = y.serie AND x.pedido = y.pedido
        WHERE x.codigo_traslado = {codigo}
          AND x.estado = 1
          AND ((x.monto - cast(y.monto as decimal(18,2))) <> 0 OR y.estado = 9 OR y.qsys_vendedor <> {332} OR y.credito <> 0)""")

        updateCambios =  cursor.execute(f"""
        UPDATE inf_traslado_detalle_especiales2 a
        INNER JOIN ( SELECT x.empresa, 
			 	            x.serie, 
				            x.pedido, 
					        cast(y.monto as decimal(18,2)) AS monto_actualizado,
                            CASE
                                WHEN (y.estado = 9 OR y.qsys_vendedor <> {332} OR y.credito <> 0) THEN 0
                                ELSE 1
                            END AS codigo_estado
			         FROM inf_traslado_detalle_especiales2 x
			         INNER JOIN inf_pedido y
			         ON x.empresa = y.empresa AND x.serie = y.serie AND x.pedido = y.pedido
			         WHERE x.codigo_traslado = {codigo}
                      AND x.estado = 1
			          AND ((x.monto - cast(y.monto as decimal(18,2))) <> 0 OR y.estado = 9 OR y.qsys_vendedor <> {1} OR y.credito <> 0)
		           ) b 
        ON a.empresa = b.empresa AND a.serie = b.serie AND a.pedido = b.pedido
        SET a.monto = b.monto_actualizado, a.estado = b.codigo_estado
        """)

        cursor.commit()
        res = "OK"

    except pyodbc.Error as err:
        res = "Error [0]: " + err.args[1]
    except pyodbc.IntegrityError as e:
        res = "Error [1]: {}".format(e)
    except:     
        res = "Error [2]: "        
    finally:
        cursor.close()
        conn.close()     
    return res


@app.route('/api/pedidos/ventascredito', methods=['GET'])
def consulta_ventas_al_credito_por_fecha():
    try:
        fecha =  request.args.get('fecha')
        mysql = Odbc("MYSQL")
        conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
        cursor = conn.cursor()
        result = cursor.execute(f"""
            SELECT empresa,
	           serie,
	           pedido, 
               DATE_FORMAT(fecha,'%d/%m/%Y') AS fecha_pedido,
	           monto, 
               vale,
               qsys_codigo_cliente AS codigo_cliente,
               nombre AS nombre_cliente,
               factura_serie,
               factura,
               qsys_pedido,
               observaciones,
               1 AS permiso_select
            FROM inf_pedido 
            WHERE credito = 1
            AND fecha = '{fecha}'
            AND estado <> {CODIGO_ESTADO_ANULADO}
        """)

        res = toJsonDump(result) # All values return of consult convert to string

    except pyodbc.Error as err:
        res = [{"pedido": 0,"observaciones": err.args[1]}]
    except pyodbc.IntegrityError as e:
        res = [{"pedido": 0,"observaciones": "Error 1"}]
        #res = "Error [1]: {}".format(e)
    except:     
        res = [{"pedido": 0,"observaciones": "Error 2"}]
    finally:
        cursor.close()
        conn.close()          

    return jsonify(res)

