"""
Exportadores de descripciones de productos a formatos específicos de plataformas.

Soporta exportación a:
- Amazon Seller Central (formato XML/JSON)
- Shopify (formato JSON de API)
- WooCommerce (formato JSON)
- CSV para importación masiva
- HTML para páginas web
"""

import json
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ProductDescriptionExporter:
    """Exportador de descripciones a diferentes formatos."""
    
    @staticmethod
    def export_to_amazon_format(description_data: Dict) -> Dict:
        """
        Exporta descripción al formato requerido por Amazon Seller Central.
        
        Args:
            description_data: Dict con la descripción generada
        
        Returns:
            Dict con formato Amazon
        """
        description = description_data.get('description', '')
        title = description_data.get('title', '')
        keywords = description_data.get('seo_keywords', [])
        
        # Amazon requiere bullets separados
        bullets = []
        if '•' in description:
            bullets = [b.strip().replace('•', '').strip() for b in description.split('\n') if '•' in b]
        else:
            # Convertir párrafos en bullets
            sentences = description.split('. ')
            bullets = [s.strip() for s in sentences[:7] if len(s.strip()) > 20]
        
        # Formato Amazon
        amazon_format = {
            'product_title': title[:200],  # Amazon limita a 200 caracteres
            'bullet_points': bullets[:5],  # Máximo 5 bullets
            'product_description': description[:2000],  # Límite de 2000 caracteres
            'search_terms': ', '.join(keywords[:5])[:250],  # Máximo 250 caracteres
            'generic_keywords': ', '.join(keywords[:10])[:250]
        }
        
        return amazon_format
    
    @staticmethod
    def export_to_shopify_format(description_data: Dict, product_id: Optional[str] = None) -> Dict:
        """
        Exporta descripción al formato JSON de Shopify API.
        
        Args:
            description_data: Dict con la descripción generada
            product_id: ID del producto en Shopify (opcional)
        
        Returns:
            Dict en formato Shopify API
        """
        description = description_data.get('description', '')
        title = description_data.get('title', '')
        meta_description = description_data.get('meta_description', '')
        keywords = description_data.get('seo_keywords', [])
        
        shopify_format = {
            'product': {
                'id': product_id,
                'title': title,
                'body_html': description,
                'metafields_global_title_tag': title,
                'metafields_global_description_tag': meta_description,
                'tags': ', '.join(keywords[:10]),
                'vendor': description_data.get('vendor', ''),
                'product_type': description_data.get('product_type', ''),
                'variants': []
            }
        }
        
        return shopify_format
    
    @staticmethod
    def export_to_woocommerce_format(description_data: Dict, product_id: Optional[int] = None) -> Dict:
        """
        Exporta descripción al formato JSON de WooCommerce API.
        
        Args:
            description_data: Dict con la descripción generada
            product_id: ID del producto en WooCommerce (opcional)
        
        Returns:
            Dict en formato WooCommerce API
        """
        description = description_data.get('description', '')
        title = description_data.get('title', '')
        meta_description = description_data.get('meta_description', '')
        keywords = description_data.get('seo_keywords', [])
        
        woocommerce_format = {
            'id': product_id,
            'name': title,
            'description': description,
            'short_description': meta_description,
            'meta_data': [
                {
                    'key': '_yoast_wpseo_title',
                    'value': title
                },
                {
                    'key': '_yoast_wpseo_metadesc',
                    'value': meta_description
                },
                {
                    'key': '_product_tags',
                    'value': ', '.join(keywords)
                }
            ],
            'categories': [],
            'tags': [{'name': kw} for kw in keywords[:10]]
        }
        
        return woocommerce_format
    
    @staticmethod
    def export_to_csv(descriptions: List[Dict], output_path: str):
        """
        Exporta múltiples descripciones a CSV para importación masiva.
        
        Args:
            descriptions: Lista de dicts con descripciones
            output_path: Ruta del archivo CSV de salida
        """
        if not descriptions:
            raise ValueError("La lista de descripciones no puede estar vacía")
        
        fieldnames = [
            'product_name', 'title', 'description', 'meta_description',
            'keywords', 'platform', 'word_count', 'seo_score'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for desc in descriptions:
                seo_analysis = desc.get('seo_analysis', {})
                writer.writerow({
                    'product_name': desc.get('product_name', ''),
                    'title': desc.get('title', ''),
                    'description': desc.get('description', ''),
                    'meta_description': desc.get('meta_description', ''),
                    'keywords': ', '.join(desc.get('seo_keywords', [])),
                    'platform': desc.get('platform', 'generic'),
                    'word_count': desc.get('word_count', 0),
                    'seo_score': seo_analysis.get('score', 0)
                })
        
        logger.info(f"Exportadas {len(descriptions)} descripciones a {output_path}")
    
    @staticmethod
    def export_to_html(description_data: Dict, include_seo: bool = True) -> str:
        """
        Exporta descripción a formato HTML para páginas web.
        
        Args:
            description_data: Dict con la descripción generada
            include_seo: Incluir meta tags SEO
        
        Returns:
            String con HTML formateado
        """
        title = description_data.get('title', '')
        description = description_data.get('description', '')
        meta_description = description_data.get('meta_description', '')
        keywords = description_data.get('seo_keywords', [])
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
"""
        
        if include_seo:
            html += f"""    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{', '.join(keywords)}">
"""
        
        html += f"""</head>
<body>
    <article>
        <h1>{title}</h1>
        <div class="product-description">
{description}
        </div>
    </article>
</body>
</html>"""
        
        return html
    
    @staticmethod
    def export_to_xml(description_data: Dict) -> str:
        """
        Exporta descripción a formato XML (útil para Amazon y otras plataformas).
        
        Args:
            description_data: Dict con la descripción generada
        
        Returns:
            String con XML formateado
        """
        root = ET.Element('product_description')
        
        ET.SubElement(root, 'title').text = description_data.get('title', '')
        ET.SubElement(root, 'description').text = description_data.get('description', '')
        ET.SubElement(root, 'meta_description').text = description_data.get('meta_description', '')
        
        keywords_elem = ET.SubElement(root, 'keywords')
        for keyword in description_data.get('seo_keywords', []):
            ET.SubElement(keywords_elem, 'keyword').text = keyword
        
        metadata_elem = ET.SubElement(root, 'metadata')
        metadata = description_data.get('metadata', {})
        for key, value in metadata.items():
            ET.SubElement(metadata_elem, key).text = str(value)
        
        # Formatear XML
        ET.indent(root)
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    @staticmethod
    def export_batch_to_platform_format(
        descriptions: List[Dict],
        platform: str,
        format_type: str = 'json'
    ) -> List[Dict]:
        """
        Exporta múltiples descripciones al formato de una plataforma específica.
        
        Args:
            descriptions: Lista de descripciones
            platform: 'amazon', 'shopify', 'woocommerce'
            format_type: 'json' o 'xml'
        
        Returns:
            Lista de descripciones en formato de plataforma
        """
        exported = []
        
        for desc in descriptions:
            if platform.lower() == 'amazon':
                exported_desc = ProductDescriptionExporter.export_to_amazon_format(desc)
            elif platform.lower() == 'shopify':
                exported_desc = ProductDescriptionExporter.export_to_shopify_format(desc)
            elif platform.lower() == 'woocommerce':
                exported_desc = ProductDescriptionExporter.export_to_woocommerce_format(desc)
            else:
                logger.warning(f"Plataforma {platform} no soportada, usando formato genérico")
                exported_desc = desc
            
            exported.append(exported_desc)
        
        return exported






