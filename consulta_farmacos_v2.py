import flet as ft
from coneccion_xamp import conectar_db

def main(page: ft.Page):
    page.title = "Sistema de Fármacos"
    page.theme_mode = "light"
    page.window_width = 1200
    page.window_height = 800
    page.padding = 20
    page.scroll = "adaptive"
    
    
    # AppBar
    page.appbar = ft.AppBar(
        leading=ft.Icon("medical_services"),
        title=ft.Text("Consulta de farmacos"),
        bgcolor="green",
        color="white"
    )

    # ========== FUNCIONES COMPARTIDAS ==========
    def mostrar_mensaje(mensaje, tipo):
        color = {
            "success": "green",
            "error": "red",
            "info": "blue"
        }.get(tipo, "blue")
        
        snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color="white"),
            bgcolor=color,
            duration=2000
        )
        page.snack_bar = snack_bar
        snack_bar.open = True
        page.update()

    # ========== PESTAÑA DE ALTA ==========
    # Controles del formulario de alta
    nombre_farmaco_field = ft.TextField(label="Nombre del Fármaco*", width=400)
    descripcion_field = ft.TextField(label="Descripción*", multiline=True, min_lines=3, max_lines=5, width=600)
    categoria_field = ft.TextField(label="Categoría*", width=400)
    interacciones_field = ft.TextField(label="Interacciones", multiline=True, min_lines=3, max_lines=5, width=600)

    # Mensaje de confirmación en pantalla
    mensaje_confirmacion = ft.Container(
        content=ft.Text("", size=16, weight="bold", color="green"),
        padding=10,
        visible=False,
        bgcolor=ft.colors.GREEN_100,
        border_radius=5,
        alignment=ft.alignment.center
    )

    def limpiar_formulario():
        nombre_farmaco_field.value = ""
        descripcion_field.value = ""
        categoria_field.value = ""
        interacciones_field.value = ""
        mensaje_confirmacion.visible = False
        mensaje_confirmacion.content.value = ""
        page.update()

    def guardar_farmaco(e):
        # Validación
        if not all([nombre_farmaco_field.value, descripcion_field.value, categoria_field.value]):
            mostrar_mensaje("Complete los campos obligatorios (marcados con *)", "error")
            return
            
        try:
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                query = """
                INSERT INTO farmaco 
                (nombre_farmaco, descripcion, categoria, interacciones) 
                VALUES (%s, %s, %s, %s)
                """
                valores = (
                    nombre_farmaco_field.value,
                    descripcion_field.value,
                    categoria_field.value,
                    interacciones_field.value or None
                )
                cursor.execute(query, valores)
                conexion.commit()
                
                # Mostrar mensaje en pantalla
                mensaje_confirmacion.content.value = "✓ Fármaco guardado exitosamente!"
                mensaje_confirmacion.visible = True
                mostrar_mensaje("Fármaco registrado exitosamente!", "success")
                limpiar_formulario()
                # Actualizar la tabla de consulta
                cargar_farmacos()
        except Exception as err:
            mostrar_mensaje(f"Error al guardar: {str(err)}", "error")
        finally:
            if conexion:
                conexion.close()

    # ========== PESTAÑA DE CONSULTA ==========
    # Controles de consulta
    search_field = ft.TextField(
        label="Buscar fármaco", 
        width=400,
        suffix_icon=ft.icons.SEARCH,
        on_change=lambda e: cargar_farmacos()
    )
    
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre", weight="bold")),
            ft.DataColumn(ft.Text("Descripción", weight="bold")),
            ft.DataColumn(ft.Text("Categoría", weight="bold")),
            ft.DataColumn(ft.Text("Interacciones", weight="bold")),
        ],
        rows=[],
        width=1000,
        column_spacing=20,
        vertical_lines=ft.border.BorderSide(1, "grey300"),
        horizontal_lines=ft.border.BorderSide(1, "grey300"),
    )
    
    def cargar_farmacos():
        try:
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT nombre_farmaco, descripcion, categoria, interacciones 
                FROM farmaco 
                WHERE nombre_farmaco LIKE %s
                ORDER BY nombre_farmaco
                """
                cursor.execute(query, (f"%{search_field.value}%",))
                resultados = cursor.fetchall()
                
                data_table.rows.clear()
                for farmaco in resultados:
                    # Función para crear celdas con texto que se expande
                    def crear_celda(texto):
                        return ft.DataCell(
                            ft.Container(
                                ft.Text(
                                    texto or "-",
                                    size=12,
                                    selectable=True,
                                    overflow=ft.TextOverflow.VISIBLE,
                                ),
                                padding=5,
                                expand=True,
                                width=200,  # Ancho mínimo
                            ),
                            on_tap=None
                        )
                    
                    data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                crear_celda(farmaco['nombre_farmaco']),
                                crear_celda(farmaco['descripcion']),
                                crear_celda(farmaco['categoria']),
                                crear_celda(farmaco['interacciones']),
                            ],
                        )
                    )
                page.update()
        except Exception as err:
            mostrar_mensaje(f"Error al cargar fármacos: {str(err)}", "error")
        finally:
            if conexion:
                conexion.close()

    # ========== INTERFAZ CON PESTAÑAS ==========
    alta_tab = ft.Tab(
        text="Alta de Fármacos",
        content=ft.Column(
            controls=[
                ft.Text("Registrar Nuevo Fármaco", size=20, weight="bold"),
                ft.Divider(),
                nombre_farmaco_field,
                categoria_field,
                descripcion_field,
                interacciones_field,
                mensaje_confirmacion,  # Mensaje visible en pantalla
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Guardar",
                            icon="save",
                            color="white",
                            bgcolor="green",
                            on_click=guardar_farmaco
                        ),
                        ft.ElevatedButton(
                            "Limpiar",
                            icon="cleaning_services",
                            on_click=lambda e: limpiar_formulario()
                        )
                    ],
                    spacing=20
                )
            ],
            spacing=20,
            scroll="adaptive"
        )
    )
    
    consulta_tab = ft.Tab(
        text="Consulta de Fármacos",
        content=ft.Column(
            controls=[
                ft.Text("Consultar Fármacos Registrados", size=20, weight="bold"),
                ft.Divider(),
                search_field,
                ft.Container(
                    content=ft.Column(
                        [data_table],
                        scroll="always",
                        expand=True
                    ),
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                    expand=True,
                    height=500  # Altura fija con scroll interno
                )
            ],
            spacing=20,
            expand=True
        )
    )
    
    tabs = ft.Tabs(
        tabs=[alta_tab, consulta_tab],
        expand=True
    )

    # Cargar datos iniciales
    cargar_farmacos()
    page.add(tabs)

# Ejecutar la aplicación
if __name__ == "__main__":
    ft.app(target=main)