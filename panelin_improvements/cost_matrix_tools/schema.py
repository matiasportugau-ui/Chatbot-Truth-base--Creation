from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class CostInfo:
    costo_base_usd_iva: Optional[float] = None
    costo_con_aumento_usd_iva: Optional[float] = None
    costo_proximo_aumento_usd_iva: Optional[float] = None

@dataclass
class MarginInfo:
    porcentaje: str = ""
    ganancia_usd: Optional[float] = None

@dataclass
class PriceInfo:
    venta_iva_usd: Optional[float] = None
    consumidor_iva_inc_usd: Optional[float] = None
    web_venta_iva_usd: Optional[float] = None
    web_venta_iva_inc_usd: Optional[float] = None

@dataclass
class Product:
    codigo: str
    nombre: str
    categoria: str
    espesor_mm: Optional[str] = None
    estado: str = "ACT."
    costos: CostInfo = field(default_factory=CostInfo)
    margen: MarginInfo = field(default_factory=MarginInfo)
    precios: PriceInfo = field(default_factory=PriceInfo)
    precio_metro_lineal: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "espesor_mm": self.espesor_mm,
            "estado": self.estado,
            "costos": {
                "fabrica_directo": {
                    "costo_base_usd_iva": self.costos.costo_base_usd_iva,
                    "costo_con_aumento_usd_iva": self.costos.costo_con_aumento_usd_iva,
                    "costo_proximo_aumento_usd_iva": self.costos.costo_proximo_aumento_usd_iva
                }
            },
            "margen": {
                "porcentaje": self.margen.porcentaje,
                "ganancia_usd": self.margen.ganancia_usd
            },
            "precios": {
                "empresa": {
                    "venta_iva_usd": self.precios.venta_iva_usd,
                    "nota": "Empresas descuentan IVA, usar precio + IVA"
                },
                "particular": {
                    "consumidor_iva_inc_usd": self.precios.consumidor_iva_inc_usd,
                    "nota": "Particulares no descuentan IVA, usar precio IVA incluido"
                },
                "web_stock": {
                    "web_venta_iva_usd": self.precios.web_venta_iva_usd,
                    "web_venta_iva_inc_usd": self.precios.web_venta_iva_inc_usd
                }
            },
            "precio_metro_lineal": self.precio_metro_lineal,
            "metadata": self.metadata
        }
