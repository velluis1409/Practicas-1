import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from fpdf import FPDF
import datetime
import os

# Conexión a la base de datos SQLite
def conectar_db():
    conn = sqlite3.connect("gestion_stock.db")
    cursor = conn.cursor()

    # Crear tabla productos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            proveedor TEXT NOT NULL,
            precio_compra REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)

    # Crear tabla ventas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    # Confirmación de que la base de datos y las tablas se han creado correctamente
    if os.path.exists("gestion_stock.db"):
        print("Base de datos 'gestion_stock.db' y tablas creadas correctamente.")
    else:
        print("Hubo un problema al crear la base de datos.")

# Función para guardar un producto
def guardar_producto(nombre, categoria, proveedor, precio):
    conn = sqlite3.connect("gestion_stock.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre, categoria, proveedor, precio_compra) VALUES (?, ?, ?, ?)", 
                   (nombre, categoria, proveedor, precio))
    conn.commit()
    conn.close()

# Función para obtener productos (búsqueda)
def buscar_productos():
    conn = sqlite3.connect("gestion_stock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, categoria, stock, precio_compra FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

# Función para registrar una venta (ahora con hora)
def registrar_venta(producto, cantidad, total):
    conn = sqlite3.connect("gestion_stock.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ventas (fecha, hora, producto, cantidad, total) VALUES (DATE('now'), TIME('now'), ?, ?, ?)", 
                   (producto, cantidad, total))
    cursor.execute("UPDATE productos SET stock = stock - ? WHERE nombre = ?", 
                   (cantidad, producto))
    conn.commit()
    conn.close()

# Función para exportar ventas a PDF
def exportar_ventas_pdf():
    conn = sqlite3.connect("gestion_stock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, hora, producto, cantidad, total FROM ventas ORDER BY fecha DESC")
    ventas = cursor.fetchall()
    conn.close()

    if not ventas:
        messagebox.showinfo("Exportar a PDF", "No hay ventas para exportar.")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Encabezado
    pdf.cell(200, 10, txt="Historial de Ventas - TecPa", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Fecha de generación: {datetime.date.today()}", ln=True, align="C")
    pdf.ln(10)

    # Tabla de Ventas
    pdf.cell(30, 10, txt="Fecha", border=1)
    pdf.cell(30, 10, txt="Hora", border=1)
    pdf.cell(50, 10, txt="Producto", border=1)
    pdf.cell(30, 10, txt="Cantidad", border=1)
    pdf.cell(30, 10, txt="Total", border=1)
    pdf.ln()

    for venta in ventas:
        pdf.cell(30, 10, txt=str(venta[0]), border=1)
        pdf.cell(30, 10, txt=str(venta[1]), border=1)
        pdf.cell(50, 10, txt=venta[2], border=1)
        pdf.cell(30, 10, txt=str(venta[3]), border=1)
        pdf.cell(30, 10, txt=f"${venta[4]:.2f}", border=1)
        pdf.ln()

    # Guardar PDF
    pdf.output("historial_ventas.pdf")
    messagebox.showinfo("Exportar a PDF", "El historial de ventas ha sido exportado como 'historial_ventas.pdf'.")

# Función para mostrar el historial de ventas
def cargar_historial_ventas(table):
    conn = sqlite3.connect("gestion_stock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, hora, producto, cantidad, total FROM ventas ORDER BY fecha DESC LIMIT 10")
    ventas = cursor.fetchall()
    conn.close()

    # Limpiar la tabla existente
    for item in table.get_children():
        table.delete(item)

    # Insertar las nuevas ventas en la tabla
    for venta in ventas:
        table.insert("", "end", values=venta)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Sistema de Gestión de Stock - TecPa")
root.geometry("800x600")
root.resizable(False, False)

# Contenedor principal
container = tk.Frame(root)
container.pack(fill="both", expand=True)

# Diccionario de frames
frames = {}

# Crear frames
for frame_name in ("Home", "IngresoProductos", "GestionStock", "Ventas"):
    frame = tk.Frame(container)
    frames[frame_name] = frame
    frame.grid(row=0, column=0, sticky="nsew")

# Función para cambiar entre frames
def show_frame(frame_name):
    frame = frames[frame_name]
    frame.tkraise()

# Pantalla Home
def create_home_frame():
    home_frame = frames["Home"]
    tk.Label(home_frame, text="Bienvenido al Sistema de Gestión de Stock", font=("Arial", 20)).pack(pady=20)
    tk.Button(home_frame, text="Ingreso de Productos", command=lambda: show_frame("IngresoProductos"), width=30).pack(pady=10)
    tk.Button(home_frame, text="Gestión de Stock", command=lambda: show_frame("GestionStock"), width=30).pack(pady=10)
    tk.Button(home_frame, text="Ventas", command=lambda: show_frame("Ventas"), width=30).pack(pady=10)
    tk.Button(home_frame, text="Salir", command=root.quit, width=30).pack(pady=20)

create_home_frame()

# Pantalla de Ventas
def create_ventas_frame():
    ventas_frame = frames["Ventas"]
    tk.Label(ventas_frame, text="Ventas", font=("Arial", 24)).pack(pady=20)

    # Selección de producto
    tk.Label(ventas_frame, text="Seleccionar Producto").pack(pady=5)
    productos = [p[0] for p in buscar_productos()]
    product_menu = ttk.Combobox(ventas_frame, values=productos, width=30)
    product_menu.pack(pady=5)

    # Cantidad vendida
    tk.Label(ventas_frame, text="Cantidad Vendida").pack(pady=5)
    cantidad_entry = tk.Entry(ventas_frame, width=30)
    cantidad_entry.pack(pady=5)

    # Precio total
    tk.Label(ventas_frame, text="Precio Total (Calculado)").pack(pady=5)
    total_entry = tk.Entry(ventas_frame, width=30, state="readonly")
    total_entry.pack(pady=5)

    # Calcular precio total
    def calcular_total(event):
        producto_seleccionado = product_menu.get()
        conn = sqlite3.connect("gestion_stock.db")
        cursor = conn.cursor()
        cursor.execute("SELECT precio_compra FROM productos WHERE nombre = ?", (producto_seleccionado,))
        precio_unitario = cursor.fetchone()
        conn.close()
        if precio_unitario and cantidad_entry.get().isdigit():
            total = float(precio_unitario[0]) * int(cantidad_entry.get())
            total_entry.config(state="normal")
            total_entry.delete(0, tk.END)
            total_entry.insert(0, f"{total:.2f}")
            total_entry.config(state="readonly")

    cantidad_entry.bind("<KeyRelease>", calcular_total)

    # Registrar la venta
    def registrar():
        producto_seleccionado = product_menu.get()
        if not producto_seleccionado:
            tk.Label(ventas_frame, text="Seleccione un producto", fg="red").pack(pady=10)
            return

        if not cantidad_entry.get().isdigit() or int(cantidad_entry.get()) <= 0:
            tk.Label(ventas_frame, text="Ingrese una cantidad válida", fg="red").pack(pady=10)
            return

        cantidad = int(cantidad_entry.get())
        total = float(total_entry.get())
        registrar_venta(producto_seleccionado, cantidad, total)
        tk.Label(ventas_frame, text="Venta registrada con éxito", fg="green").pack(pady=10)

        # Recargar historial de ventas
        cargar_historial_ventas(ventas_table)
        cantidad_entry.delete(0, tk.END)
        total_entry.config(state="normal")
        total_entry.delete(0, tk.END)
        total_entry.config(state="readonly")

    tk.Button(ventas_frame, text="Registrar Venta", width=20, command=registrar).pack(pady=10)

    # Tabla de historial de ventas
    tk.Label(ventas_frame, text="Historial de Ventas (Últimas 10)").pack(pady=10)
    ventas_table = ttk.Treeview(ventas_frame, columns=("Fecha", "Hora", "Producto", "Cantidad", "Total"), show="headings")
    ventas_table.heading("Fecha", text="Fecha")
    ventas_table.heading("Hora", text="Hora")
    ventas_table.heading("Producto", text="Producto")
    ventas_table.heading("Cantidad", text="Cantidad")
    ventas_table.heading("Total", text="Total")
    ventas_table.pack(pady=10, fill="x")

    # Cargar historial de ventas
    cargar_historial_ventas(ventas_table)

    # Botón para exportar PDF
    tk.Button(ventas_frame, text="Exportar Ventas a PDF", command=exportar_ventas_pdf).pack(pady=10)

    tk.Button(ventas_frame, text="Volver", command=lambda: show_frame("Home")).pack(pady=10)

create_ventas_frame()

# Mostrar pantalla inicial
show_frame("Home")

# Ejecutar aplicación
root.mainloop()
