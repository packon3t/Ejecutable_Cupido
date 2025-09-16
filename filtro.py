#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para filtrar carpetas por fecha de modificación
Solicita al usuario la ruta y criterios de filtrado V0.1 04/09/2025
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path
import re

class FiltrarCarpetas:
    def __init__(self):
        self.ruta_busqueda = ""
        self.carpetas_encontradas = []
        
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_titulo(self):
        """Muestra el título del programa"""
        print("=" * 50)
        print("    FILTRO DE CARPETAS POR FECHA - PYTHON")
        print("=" * 50)
        print()
    
    def solicitar_ruta(self):
        """Solicita y valida la ruta de búsqueda"""
        while True:
            ruta = input("Ingrese la ruta donde buscar (Enter para directorio actual): ").strip()
            
            if not ruta:
                ruta = os.getcwd()
            
            # Expandir rutas relativas y variables de entorno
            ruta = os.path.expanduser(os.path.expandvars(ruta))
            
            if os.path.exists(ruta) and os.path.isdir(ruta):
                self.ruta_busqueda = ruta
                print(f"✓ Ruta válida: {self.ruta_busqueda}")
                return True
            else:
                print("❌ Error: La ruta especificada no existe o no es un directorio.")
                print()
    
    def validar_fecha(self, fecha_str):
        """Valida el formato de fecha dd/mm/aaaa"""
        patron = r'^(\d{2})/(\d{2})/(\d{4})$'
        match = re.match(patron, fecha_str)
        
        if not match:
            return None
        
        try:
            dia, mes, año = map(int, match.groups())
            fecha = date(año, mes, dia)
            return fecha
        except ValueError:
            return None
    
    def solicitar_fecha(self, mensaje):
        """Solicita una fecha al usuario con validación"""
        while True:
            fecha_str = input(f"{mensaje} [dd/mm/aaaa]: ").strip()
            fecha = self.validar_fecha(fecha_str)
            
            if fecha:
                return fecha
            else:
                print("❌ Formato de fecha inválido. Use dd/mm/aaaa (ej: 15/03/2024)")
                print()
    
    def mostrar_menu_opciones(self):
        """Muestra el menú de opciones de filtrado"""
        print("\nOpciones de filtro:")
        print("1. Carpetas modificadas DESPUÉS de una fecha específica")
        print("2. Carpetas modificadas ANTES de una fecha específica")
        print("3. Carpetas modificadas EN una fecha específica")
        print("4. Carpetas modificadas en un RANGO de fechas")
        print("5. Carpetas modificadas en los ÚLTIMOS N días")
        print()
        
        while True:
            try:
                opcion = int(input("Seleccione una opción (1-5): "))
                if 1 <= opcion <= 5:
                    return opcion
                else:
                    print("❌ Opción inválida. Seleccione un número del 1 al 5.")
            except ValueError:
                print("❌ Por favor ingrese un número válido.")
    
    def obtener_fecha_modificacion(self, ruta_carpeta):
        """Obtiene la fecha de modificación de una carpeta"""
        try:
            timestamp = os.path.getmtime(ruta_carpeta)
            return date.fromtimestamp(timestamp)
        except (OSError, ValueError):
            return None
    
    def buscar_carpetas(self, incluir_subcarpetas=True):
        """Busca todas las carpetas en la ruta especificada"""
        carpetas = []
        
        try:
            if incluir_subcarpetas:
                # Búsqueda recursiva
                for root, dirs, files in os.walk(self.ruta_busqueda):
                    for dir_name in dirs:
                        ruta_completa = os.path.join(root, dir_name)
                        fecha_mod = self.obtener_fecha_modificacion(ruta_completa)
                        if fecha_mod:
                            carpetas.append({
                                'ruta': ruta_completa,
                                'nombre': dir_name,
                                'fecha_modificacion': fecha_mod
                            })
            else:
                # Solo carpetas en el directorio actual
                with os.scandir(self.ruta_busqueda) as entries:
                    for entry in entries:
                        if entry.is_dir():
                            fecha_mod = self.obtener_fecha_modificacion(entry.path)
                            if fecha_mod:
                                carpetas.append({
                                    'ruta': entry.path,
                                    'nombre': entry.name,
                                    'fecha_modificacion': fecha_mod
                                })
        except PermissionError:
            print(f"❌ Sin permisos para acceder a: {self.ruta_busqueda}")
        except Exception as e:
            print(f"❌ Error al buscar carpetas: {e}")
        
        return carpetas
    
    def filtrar_por_opcion(self, carpetas, opcion):
        """Filtra carpetas según la opción seleccionada"""
        carpetas_filtradas = []
        
        if opcion == 1:  # Después de una fecha
            fecha_ref = self.solicitar_fecha("Ingrese la fecha de referencia")
            carpetas_filtradas = [c for c in carpetas if c['fecha_modificacion'] > fecha_ref]
            
        elif opcion == 2:  # Antes de una fecha
            fecha_ref = self.solicitar_fecha("Ingrese la fecha de referencia")
            carpetas_filtradas = [c for c in carpetas if c['fecha_modificacion'] < fecha_ref]
            
        elif opcion == 3:  # En una fecha específica
            fecha_ref = self.solicitar_fecha("Ingrese la fecha específica")
            carpetas_filtradas = [c for c in carpetas if c['fecha_modificacion'] == fecha_ref]
            
        elif opcion == 4:  # Rango de fechas
            fecha_inicio = self.solicitar_fecha("Ingrese la fecha de inicio")
            fecha_fin = self.solicitar_fecha("Ingrese la fecha de fin")
            
            if fecha_inicio > fecha_fin:
                print("❌ La fecha de inicio debe ser anterior a la fecha de fin.")
                return []
            
            carpetas_filtradas = [c for c in carpetas 
                                if fecha_inicio <= c['fecha_modificacion'] <= fecha_fin]
            
        elif opcion == 5:  # Últimos N días
            while True:
                try:
                    dias = int(input("Ingrese el número de días: "))
                    if dias > 0:
                        break
                    else:
                        print("❌ El número de días debe ser positivo.")
                except ValueError:
                    print("❌ Por favor ingrese un número válido.")
            
            fecha_limite = date.today()
            from datetime import timedelta
            fecha_inicio = fecha_limite - timedelta(days=dias)
            
            carpetas_filtradas = [c for c in carpetas 
                                if c['fecha_modificacion'] >= fecha_inicio]
        
        return carpetas_filtradas
    
    def mostrar_resultados(self, carpetas_filtradas):
        """Muestra los resultados del filtrado"""
        print("\n" + "=" * 50)
        print("           RESULTADOS DEL FILTRO")
        print("=" * 50)
        print(f"Total de carpetas encontradas: {len(carpetas_filtradas)}")
        print()
        
        if not carpetas_filtradas:
            print("❌ No se encontraron carpetas que cumplan el criterio especificado.")
            return
        
        # Ordenar por fecha de modificación
        carpetas_ordenadas = sorted(carpetas_filtradas, key=lambda x: x['fecha_modificacion'])
        
        print("Carpetas que cumplen el criterio:")
        print("-" * 50)
        
        for i, carpeta in enumerate(carpetas_ordenadas, 1):
            fecha_str = carpeta['fecha_modificacion'].strftime("%d/%m/%Y")
            print(f"{i:3d}. [{fecha_str}] {carpeta['ruta']}")
        
        self.carpetas_encontradas = carpetas_filtradas
    
    def guardar_resultados(self):
        """Permite guardar los resultados en un archivo"""
        if not self.carpetas_encontradas:
            return
        
        print("\n" + "-" * 50)
        guardar = input("¿Desea guardar estos resultados en un archivo? (s/n): ").lower().strip()
        
        if guardar in ['s', 'sí', 'si', 'y', 'yes']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"carpetas_filtradas_{timestamp}.txt"
            
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write("RESULTADOS DEL FILTRO DE CARPETAS POR FECHA\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(f"Ruta de búsqueda: {self.ruta_busqueda}\n")
                    f.write(f"Total de carpetas: {len(self.carpetas_encontradas)}\n\n")
                    
                    carpetas_ordenadas = sorted(self.carpetas_encontradas, 
                                              key=lambda x: x['fecha_modificacion'])
                    
                    for i, carpeta in enumerate(carpetas_ordenadas, 1):
                        fecha_str = carpeta['fecha_modificacion'].strftime("%d/%m/%Y")
                        f.write(f"{i:3d}. [{fecha_str}] {carpeta['ruta']}\n")
                
                print(f"✓ Resultados guardados en: {nombre_archivo}")
                
            except Exception as e:
                print(f"❌ Error al guardar el archivo: {e}")
    
    def preguntar_incluir_subcarpetas(self):
        """Pregunta si incluir subcarpetas en la búsqueda"""
        print()
        incluir = input("¿Incluir subcarpetas en la búsqueda? (s/n) [s]: ").lower().strip()
        return incluir != 'n' and incluir != 'no'
    
    def ejecutar(self):
        """Ejecuta el programa principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_titulo()
            
            # Solicitar ruta de búsqueda
            if not self.solicitar_ruta():
                continue
            
            # Preguntar sobre subcarpetas
            incluir_subcarpetas = self.preguntar_incluir_subcarpetas()
            
            print(f"\n🔍 Buscando carpetas en: {self.ruta_busqueda}")
            if incluir_subcarpetas:
                print("   (incluyendo subcarpetas)")
            else:
                print("   (solo en directorio actual)")
            
            # Buscar carpetas
            carpetas = self.buscar_carpetas(incluir_subcarpetas)
            
            if not carpetas:
                print("❌ No se encontraron carpetas en la ruta especificada.")
                input("\nPresione Enter para continuar...")
                continue
            
            print(f"✓ Se encontraron {len(carpetas)} carpetas")
            
            # Mostrar opciones y filtrar
            opcion = self.mostrar_menu_opciones()
            carpetas_filtradas = self.filtrar_por_opcion(carpetas, opcion)
            
            # Mostrar resultados
            self.mostrar_resultados(carpetas_filtradas)
            
            # Opción para guardar
            self.guardar_resultados()
            
            # Preguntar si continuar
            print("\n" + "-" * 50)
            continuar = input("¿Desea realizar otra búsqueda? (s/n): ").lower().strip()
            if continuar not in ['s', 'sí', 'si', 'y', 'yes']:
                break
        
        print("\n¡Gracias por usar el filtro de carpetas!")

def main():
    """Función principal"""
    try:
        filtrador = FiltrarCarpetas()
        filtrador.ejecutar()
    except KeyboardInterrupt:
        print("\n\n❌ Programa interrumpido por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()