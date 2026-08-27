"""API para interactuar con Coto Digital."""
from __future__ import annotations

import logging
import sqlite3
import re
from datetime import datetime
from typing import Any
import urllib.request
import urllib.parse
import json

from .const import COTO_SEARCH_URL

_LOGGER = logging.getLogger(__name__)


class CotoDigitalAPI:
    """Clase para manejar la API de Coto Digital y la base de datos local."""

    def __init__(self, db_path: str):
        """Initialize the API."""
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Inicializar la base de datos SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabla de carrito
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carrito (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id TEXT UNIQUE,
                    nombre TEXT,
                    precio REAL,
                    imagen_url TEXT,
                    cantidad INTEGER DEFAULT 1,
                    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla de historial de búsquedas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_busquedas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    resultados_count INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            _LOGGER.info("Base de datos inicializada: %s", self.db_path)
        except Exception as err:
            _LOGGER.error("Error inicializando base de datos: %s", err)

    def buscar_productos(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """Buscar productos en Coto Digital."""
        try:
            # Preparar parámetros de búsqueda
            params = {
                "_dyncharset": "UTF-8",
                "_dynSessConf": "-8780680307969995766",
                "/atg/commerce/search/catalog/ProductCatalogSearchFormHandler.searchTerms": query,
                "/atg/commerce/search/catalog/ProductCatalogSearchFormHandler.search": "Buscar",
                "format": "json",
            }

            # Construir URL
            url = f"{COTO_SEARCH_URL}?{urllib.parse.urlencode(params)}"

            # Realizar petición
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
            }

            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            # Parsear resultados
            productos = []
            
            if "contents" in data and len(data["contents"]) > 0:
                for item in data["contents"][0].get("mainContent", []):
                    if item.get("@type") == "ProductDetails":
                        record = item.get("records", [{}])[0]
                        attributes = record.get("attributes", {})
                        
                        producto = {
                            "producto_id": attributes.get("product.repositoryId", [""])[0],
                            "nombre": attributes.get("product.displayName", ["Sin nombre"])[0],
                            "precio": self._parse_precio(
                                attributes.get("sku.listPrice", ["0"])[0]
                            ),
                            "imagen_url": attributes.get("product.largeImage.url", [""])[0],
                            "marca": attributes.get("product.brand", [""])[0],
                        }
                        
                        if producto["producto_id"]:
                            productos.append(producto)

            # Guardar en historial
            self._guardar_busqueda(query, len(productos))

            _LOGGER.info("Búsqueda '%s': %d productos encontrados", query, len(productos))
            
            return productos[:limit]

        except Exception as err:
            _LOGGER.error("Error buscando productos: %s", err)
            return []

    def _parse_precio(self, precio_str: str) -> float:
        """Parsear precio desde string."""
        try:
            # Eliminar símbolos y convertir
            precio_clean = re.sub(r"[^\d,\.]", "", precio_str)
            precio_clean = precio_clean.replace(",", ".")
            return float(precio_clean)
        except (ValueError, AttributeError):
            return 0.0

    def _guardar_busqueda(self, query: str, count: int) -> None:
        """Guardar búsqueda en historial."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO historial_busquedas (query, resultados_count) VALUES (?, ?)",
                (query, count)
            )
            
            conn.commit()
            conn.close()
        except Exception as err:
            _LOGGER.error("Error guardando búsqueda: %s", err)

    def obtener_carrito(self) -> list[dict[str, Any]]:
        """Obtener contenido del carrito."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM carrito ORDER BY fecha_agregado DESC"
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            productos = []
            for row in rows:
                productos.append({
                    "id": row["id"],
                    "producto_id": row["producto_id"],
                    "nombre": row["nombre"],
                    "precio": row["precio"],
                    "imagen_url": row["imagen_url"],
                    "cantidad": row["cantidad"],
                    "fecha_agregado": row["fecha_agregado"],
                })
            
            return productos

        except Exception as err:
            _LOGGER.error("Error obteniendo carrito: %s", err)
            return []

    def agregar_al_carrito(self, producto: dict[str, Any]) -> bool:
        """Agregar producto al carrito."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute(
                "SELECT cantidad FROM carrito WHERE producto_id = ?",
                (producto["producto_id"],)
            )
            
            row = cursor.fetchone()
            
            if row:
                # Actualizar cantidad
                nueva_cantidad = row[0] + producto.get("cantidad", 1)
                cursor.execute(
                    "UPDATE carrito SET cantidad = ? WHERE producto_id = ?",
                    (nueva_cantidad, producto["producto_id"])
                )
            else:
                # Insertar nuevo
                cursor.execute(
                    """
                    INSERT INTO carrito (producto_id, nombre, precio, imagen_url, cantidad)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        producto["producto_id"],
                        producto["nombre"],
                        producto["precio"],
                        producto.get("imagen_url", ""),
                        producto.get("cantidad", 1),
                    )
                )
            
            conn.commit()
            conn.close()
            
            _LOGGER.info("Producto agregado: %s", producto["nombre"])
            return True

        except Exception as err:
            _LOGGER.error("Error agregando al carrito: %s", err)
            return False

    def eliminar_del_carrito(self, producto_id: str) -> bool:
        """Eliminar producto del carrito."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM carrito WHERE producto_id = ?",
                (producto_id,)
            )
            
            conn.commit()
            conn.close()
            
            _LOGGER.info("Producto eliminado: %s", producto_id)
            return True

        except Exception as err:
            _LOGGER.error("Error eliminando del carrito: %s", err)
            return False

    def vaciar_carrito(self) -> bool:
        """Vaciar todo el carrito."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM carrito")
            
            conn.commit()
            conn.close()
            
            _LOGGER.info("Carrito vaciado")
            return True

        except Exception as err:
            _LOGGER.error("Error vaciando carrito: %s", err)
            return False

    def obtener_estadisticas(self) -> dict[str, Any]:
        """Obtener estadísticas del carrito."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cantidad de productos
            cursor.execute("SELECT COUNT(*) FROM carrito")
            count = cursor.fetchone()[0]
            
            # Total de unidades
            cursor.execute("SELECT SUM(cantidad) FROM carrito")
            total_unidades = cursor.fetchone()[0] or 0
            
            # Total en pesos
            cursor.execute("SELECT SUM(precio * cantidad) FROM carrito")
            total_precio = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                "productos_count": count,
                "total_unidades": total_unidades,
                "total_precio": round(total_precio, 2),
            }

        except Exception as err:
            _LOGGER.error("Error obteniendo estadísticas: %s", err)
            return {
                "productos_count": 0,
                "total_unidades": 0,
                "total_precio": 0.0,
            }
