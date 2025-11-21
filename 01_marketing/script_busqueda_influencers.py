#!/usr/bin/env python3
"""
Script de Búsqueda de Influencers Tech
=======================================

Este script ayuda a organizar y gestionar la búsqueda de influencers de tecnología.
NO hace scraping automático (violaría TOS de redes sociales), pero ayuda a organizar
la búsqueda manual y gestionar los datos encontrados.

Uso:
    python script_busqueda_influencers.py
"""

import csv
import json
from datetime import datetime
from typing import List, Dict, Optional

class InfluencerManager:
    """Gestiona la lista de influencers encontrados"""
    
    def __init__(self, csv_file: str = "influencers_encontrados.csv"):
        self.csv_file = csv_file
        self.influencers = []
        self.load_existing()
    
    def load_existing(self):
        """Carga influencers existentes del CSV"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.influencers = list(reader)
        except FileNotFoundError:
            print(f"Archivo {self.csv_file} no encontrado. Se creará uno nuevo.")
    
    def add_influencer(self, influencer_data: Dict):
        """Agrega un nuevo influencer"""
        influencer_data['fecha_agregado'] = datetime.now().strftime('%Y-%m-%d')
        influencer_data['verificado'] = 'Pendiente'
        self.influencers.append(influencer_data)
        self.save_to_csv()
        print(f"✅ Influencer agregado: {influencer_data.get('nombre', 'N/A')}")
    
    def save_to_csv(self):
        """Guarda influencers en CSV"""
        if not self.influencers:
            return
        
        fieldnames = [
            'nombre', 'usuario_instagram', 'link_instagram', 'usuario_twitter',
            'link_twitter', 'usuario_tiktok', 'link_tiktok', 'usuario_youtube',
            'link_youtube', 'seguidores', 'engagement_rate', 'especialidad',
            'mejor_canal_contacto', 'categoria', 'link_directo_perfil',
            'verificado', 'fecha_agregado', 'notas', 'estado', 'fecha_contacto',
            'respuesta', 'colaboracion'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.influencers)
    
    def filter_by_followers(self, min_followers: int, max_followers: int) -> List[Dict]:
        """Filtra influencers por rango de seguidores"""
        filtered = []
        for inf in self.influencers:
            try:
                seguidores_str = inf.get('seguidores', '0').replace('~', '').replace('K', '000').replace('M', '000000')
                seguidores = int(seguidores_str)
                if min_followers <= seguidores <= max_followers:
                    filtered.append(inf)
            except (ValueError, AttributeError):
                continue
        return filtered
    
    def filter_by_category(self, categoria: str) -> List[Dict]:
        """Filtra influencers por categoría"""
        return [inf for inf in self.influencers if inf.get('categoria', '').lower() == categoria.lower()]
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de la lista"""
        total = len(self.influencers)
        verificados = len([inf for inf in self.influencers if inf.get('verificado') == '✅'])
        contactados = len([inf for inf in self.influencers if inf.get('estado') == 'Contactado'])
        responded = len([inf for inf in self.influencers if inf.get('respuesta') == 'Sí'])
        
        return {
            'total': total,
            'verificados': verificados,
            'contactados': contactados,
            'respondieron': responded,
            'tasa_respuesta': f"{(responded/contactados*100) if contactados > 0 else 0:.1f}%"
        }
    
    def export_to_json(self, filename: str = "influencers_backup.json"):
        """Exporta a JSON para backup"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.influencers, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup guardado en {filename}")


def interactive_add_influencer(manager: InfluencerManager):
    """Interfaz interactiva para agregar influencers"""
    print("\n" + "="*50)
    print("AGREGAR NUEVO INFLUENCER")
    print("="*50)
    
    influencer = {}
    
    influencer['nombre'] = input("Nombre: ").strip()
    influencer['usuario_instagram'] = input("Usuario Instagram (@username): ").strip().replace('@', '')
    influencer['link_instagram'] = input("Link Instagram: ").strip() or f"https://www.instagram.com/{influencer['usuario_instagram']}/"
    
    if input("¿Tiene Twitter? (s/n): ").lower() == 's':
        influencer['usuario_twitter'] = input("Usuario Twitter: ").strip().replace('@', '')
        influencer['link_twitter'] = input("Link Twitter: ").strip() or f"https://twitter.com/{influencer['usuario_twitter']}"
    
    if input("¿Tiene TikTok? (s/n): ").lower() == 's':
        influencer['usuario_tiktok'] = input("Usuario TikTok: ").strip().replace('@', '')
        influencer['link_tiktok'] = input("Link TikTok: ").strip() or f"https://www.tiktok.com/@{influencer['usuario_tiktok']}"
    
    if input("¿Tiene YouTube? (s/n): ").lower() == 's':
        influencer['usuario_youtube'] = input("Usuario YouTube: ").strip()
        influencer['link_youtube'] = input("Link YouTube: ").strip()
    
    influencer['seguidores'] = input("Seguidores (ej: ~25K): ").strip()
    influencer['engagement_rate'] = input("Engagement Rate (ej: ~6%): ").strip()
    influencer['especialidad'] = input("Especialidad: ").strip()
    influencer['categoria'] = input("Categoría (Web Dev, AI, Mobile, etc.): ").strip()
    influencer['mejor_canal_contacto'] = input("Mejor canal contacto (Instagram DM, Email, etc.): ").strip() or "Instagram DM"
    influencer['link_directo_perfil'] = influencer.get('link_instagram', '')
    influencer['notas'] = input("Notas adicionales: ").strip()
    influencer['estado'] = 'Pendiente'
    
    manager.add_influencer(influencer)
    print("\n✅ Influencer agregado exitosamente!")


def show_statistics(manager: InfluencerManager):
    """Muestra estadísticas"""
    stats = manager.get_statistics()
    print("\n" + "="*50)
    print("ESTADÍSTICAS")
    print("="*50)
    print(f"Total influencers: {stats['total']}")
    print(f"Verificados: {stats['verificados']}")
    print(f"Contactados: {stats['contactados']}")
    print(f"Respondieron: {stats['respondieron']}")
    print(f"Tasa de respuesta: {stats['tasa_respuesta']}")


def filter_influencers(manager: InfluencerManager):
    """Filtra y muestra influencers"""
    print("\n" + "="*50)
    print("FILTRAR INFLUENCERS")
    print("="*50)
    print("1. Por rango de seguidores")
    print("2. Por categoría")
    
    choice = input("\nOpción: ").strip()
    
    if choice == '1':
        min_f = int(input("Mínimo seguidores (ej: 1000): ") or "1000")
        max_f = int(input("Máximo seguidores (ej: 10000): ") or "10000")
        filtered = manager.filter_by_followers(min_f, max_f)
        print(f"\n✅ Encontrados: {len(filtered)} influencers")
        for inf in filtered[:10]:  # Mostrar primeros 10
            print(f"  - {inf.get('nombre', 'N/A')}: {inf.get('seguidores', 'N/A')} seguidores")
    
    elif choice == '2':
        categoria = input("Categoría: ").strip()
        filtered = manager.filter_by_category(categoria)
        print(f"\n✅ Encontrados: {len(filtered)} influencers")
        for inf in filtered[:10]:
            print(f"  - {inf.get('nombre', 'N/A')}: {inf.get('categoria', 'N/A')}")


def main():
    """Función principal"""
    manager = InfluencerManager()
    
    while True:
        print("\n" + "="*50)
        print("GESTOR DE INFLUENCERS TECH")
        print("="*50)
        print("1. Agregar influencer")
        print("2. Ver estadísticas")
        print("3. Filtrar influencers")
        print("4. Exportar a JSON (backup)")
        print("5. Salir")
        
        choice = input("\nOpción: ").strip()
        
        if choice == '1':
            interactive_add_influencer(manager)
        elif choice == '2':
            show_statistics(manager)
        elif choice == '3':
            filter_influencers(manager)
        elif choice == '4':
            manager.export_to_json()
        elif choice == '5':
            print("\n¡Hasta luego! 👋")
            break
        else:
            print("\n❌ Opción no válida")


if __name__ == "__main__":
    main()


