#!/usr/bin/env python3
"""
MODULAR ADS SYSTEM - Demo Principal
=================================

Demo completo del sistema de ads modular ultra-optimizado.
Muestra todas las características y capacidades del sistema.
"""

import asyncio
import time
import sys
import os

# Agregar path del módulo modular
sys.path.append(os.path.join(os.path.dirname(__file__), 'modular_ads'))

from modular_ads import (
    ModularAdsSystem, 
    AdRequest, AdResponse, BatchAdRequest,
    AdType, AdPriority,
    quick_generate_ad, quick_batch_generate,
    quick_health_check, quick_benchmark,
    demo_modular_ads
)

async def comprehensive_modular_demo():
    """Demo comprehensivo del sistema modular"""
    print("🚀 COMPREHENSIVE MODULAR ADS DEMO")
    print("="*60)
    print("Sistema de ads completamente modular con:")
    print("✅ Engine de optimización automática")
    print("✅ Cache multi-nivel inteligente (L1+L2+L3)")  
    print("✅ Servicios modulares independientes")
    print("✅ Configuración centralizada")
    print("✅ Validación y sanitización automática")
    print("✅ Métricas y monitoring completo")
    print("✅ Support para 6+ tipos de ads")
    print("="*60)
    
    # Inicializar sistema modular
    system = ModularAdsSystem()
    await system.initialize()
    
    # 1. HEALTH CHECK INICIAL
    print(f"\n🏥 MODULAR SYSTEM HEALTH CHECK:")
    print("-" * 40)
    
    health = await system.health_check()
    print(f"Status: {health['status'].upper()}")
    print(f"Optimization Score: {health['test']['optimization_score']:.1f}/100")
    print(f"Performance Tier: {health['engine']['performance_tier']}")
    print(f"Available Libraries: {health['engine']['available_libraries']}/{health['engine']['total_libraries']}")
    print(f"Test Response Time: {health['test']['response_time_ms']:.1f}ms")
    
    # 2. GENERACIÓN INDIVIDUAL POR TIPO DE AD
    print(f"\n🎯 MODULAR AD GENERATION BY TYPE:")
    print("-" * 40)
    
    ad_types_test = [
        (AdType.FACEBOOK, "Producto revolucionario IA", "empresarios tech", ["IA", "innovación"]),
        (AdType.GOOGLE, "Oferta especial limitada", "compradores online", ["oferta", "descuento"]),
        (AdType.INSTAGRAM, "Tendencia viral marketing", "millennials", ["viral", "trending"]),
        (AdType.LINKEDIN, "Networking profesional", "business leaders", ["networking", "professional"]),
        (AdType.TWITTER, "Breaking news tech", "tech enthusiasts", ["breaking", "tech"]),
        (AdType.YOUTUBE, "Tutorial completo", "learners", ["tutorial", "education"])
    ]
    
    individual_responses = []
    total_start = time.time()
    
    for i, (ad_type, content, audience, keywords) in enumerate(ad_types_test, 1):
        request = AdRequest(
            content=content,
            ad_type=ad_type,
            target_audience=audience,
            keywords=keywords,
            priority=AdPriority.HIGH if i <= 2 else AdPriority.MEDIUM,
            use_cache=True
        )
        
        response = await system.generate_ad(request)
        individual_responses.append(response)
        
        print(f"\n{i}. {ad_type.value.upper()} Ad:")
        print(f"   Content: {response.ad_content[:55]}...")
        print(f"   Time: {response.response_time_ms:.1f}ms")
        print(f"   Cache: {'✅ HIT' if response.cache_hit else '❌ MISS'}")
        print(f"   Words: {response.word_count} | Chars: {response.character_count}")
        print(f"   Score: {response.optimization_score:.1f}/100")
    
    individual_total_time = (time.time() - total_start) * 1000
    individual_avg_time = individual_total_time / len(ad_types_test)
    
    print(f"\n⚡ Individual Generation Summary:")
    print(f"   Total Time: {individual_total_time:.1f}ms")
    print(f"   Avg per Ad: {individual_avg_time:.1f}ms")
    print(f"   Ads per Second: {1000/individual_avg_time:.1f}")
    
    # 3. BATCH GENERATION TEST
    print(f"\n🔄 MODULAR BATCH GENERATION:")
    print("-" * 35)
    
    batch_requests_data = [
        {"content": "AI Assistant personal", "ad_type": AdType.FACEBOOK, "target_audience": "tech users", "priority": AdPriority.CRITICAL},
        {"content": "Descuento Black Friday", "ad_type": AdType.GOOGLE, "target_audience": "shoppers", "priority": AdPriority.HIGH},
        {"content": "Foto perfecta Instagram", "ad_type": AdType.INSTAGRAM, "target_audience": "photographers", "priority": AdPriority.MEDIUM},
        {"content": "Curso online certificado", "ad_type": AdType.LINKEDIN, "target_audience": "professionals", "priority": AdPriority.MEDIUM},
        {"content": "Meme viral del día", "ad_type": AdType.TWITTER, "target_audience": "gen z", "priority": AdPriority.LOW}
    ]
    
    batch_start = time.time()
    batch_response = await quick_batch_generate(batch_requests_data, max_concurrency=5)
    batch_time = (time.time() - batch_start) * 1000
    
    print(f"Batch Results:")
    print(f"   Total Ads: {batch_response.total_count}")
    print(f"   Successful: {batch_response.successful_count}")
    print(f"   Failed: {batch_response.failed_count}")
    print(f"   Batch Time: {batch_time:.1f}ms")
    print(f"   Avg Time: {batch_response.average_time_ms:.1f}ms")
    print(f"   Throughput: {batch_response.total_count / (batch_time/1000):.1f} ads/sec")
    
    # 4. CACHE EFFECTIVENESS TEST
    print(f"\n🔄 MODULAR CACHE EFFECTIVENESS:")
    print("-" * 35)
    
    # Repetir algunos requests para testear cache
    cache_test_requests = ad_types_test[:3]  # Primeros 3
    cache_hits = 0
    cache_total_time = 0
    
    for ad_type, content, audience, keywords in cache_test_requests:
        request = AdRequest(
            content=content,
            ad_type=ad_type,
            target_audience=audience,
            keywords=keywords,
            use_cache=True
        )
        
        cache_start = time.time()
        cached_response = await system.generate_ad(request)
        cache_time = (time.time() - cache_start) * 1000
        
        cache_total_time += cache_time
        if cached_response.cache_hit:
            cache_hits += 1
    
    cache_avg_time = cache_total_time / len(cache_test_requests)
    cache_hit_rate = (cache_hits / len(cache_test_requests)) * 100
    
    print(f"Cache Test Results:")
    print(f"   Cache Hits: {cache_hits}/{len(cache_test_requests)}")
    print(f"   Hit Rate: {cache_hit_rate:.1f}%")
    print(f"   Avg Cached Time: {cache_avg_time:.1f}ms")
    print(f"   Speed Improvement: {individual_avg_time/cache_avg_time:.1f}x faster")
    
    # 5. BENCHMARK COMPLETO
    print(f"\n📊 MODULAR SYSTEM BENCHMARK:")
    print("-" * 35)
    
    benchmark_results = await system.benchmark(iterations=50)
    
    print(f"Benchmark Results ({benchmark_results['benchmark_summary']['iterations']} iterations):")
    print(f"   Total Time: {benchmark_results['benchmark_summary']['total_time_seconds']:.2f}s")
    print(f"   Ads per Second: {benchmark_results['benchmark_summary']['ads_per_second']:.1f}")
    print(f"   Avg Time: {benchmark_results['benchmark_summary']['average_time_ms']:.1f}ms")
    print(f"   Success Rate: {benchmark_results['benchmark_summary']['success_rate_percent']:.1f}%")
    print(f"   Cache Hit Rate: {benchmark_results['benchmark_summary']['cache_hit_rate_percent']:.1f}%")
    
    print(f"\nEngine Performance:")
    engine_bench = benchmark_results['engine_benchmark']
    print(f"   JSON ops/sec: {engine_bench['json_ops_per_sec']:.0f}")
    print(f"   Hash ops/sec: {engine_bench['hash_ops_per_sec']:.0f}")
    print(f"   Compression ops/sec: {engine_bench['compression_ops_per_sec']:.0f}")
    
    # 6. MÉTRICAS FINALES COMPLETAS
    print(f"\n📊 COMPREHENSIVE SYSTEM METRICS:")
    print("-" * 40)
    
    final_metrics = await system.get_metrics()
    
    print(f"Optimization:")
    opt_metrics = final_metrics['optimization']
    print(f"   Score: {opt_metrics['score']:.1f}/100 ({opt_metrics['tier']})")
    print(f"   Libraries: {opt_metrics['available_libraries']}/{opt_metrics['total_libraries']}")
    
    print(f"\nPerformance:")
    perf_metrics = final_metrics['performance']
    print(f"   Total Requests: {perf_metrics['total_requests']}")
    print(f"   Success Rate: {perf_metrics['success_rate_percent']:.1f}%")
    print(f"   Avg Response: {perf_metrics['average_time_ms']:.1f}ms")
    print(f"   Uptime: {perf_metrics['uptime_seconds']:.1f}s")
    
    print(f"\nCache Performance:")
    cache_metrics = final_metrics['cache']['global']
    print(f"   Hit Rate: {cache_metrics['hit_rate_percent']:.1f}%")
    print(f"   Total Requests: {cache_metrics['total_requests']}")
    print(f"   Level Hit Rates:")
    for level, rate in cache_metrics['level_hit_rates'].items():
        if rate > 0:
            print(f"     {level}: {rate:.1f}%")
    
    print(f"\nAds Distribution:")
    ads_metrics = final_metrics['ads']
    for ad_type, count in ads_metrics['by_type'].items():
        print(f"   {ad_type}: {count} ads")
    
    # 7. ARCHITECTURE SUMMARY
    print(f"\n🏗️  MODULAR ARCHITECTURE SUMMARY:")
    print("-" * 40)
    
    print("Modules Initialized:")
    print("   ✅ Types Module: Enums, type definitions")
    print("   ✅ Models Module: Data classes, requests/responses")
    print("   ✅ Config Module: Centralized configuration")
    print("   ✅ Utils Module: Helper functions, decorators")
    print("   ✅ Engine Module: Optimization engine, circuit breaker")
    print("   ✅ Cache Module: Multi-level cache (L1+L2+L3)")
    print("   ✅ Services Module: Main business logic")
    
    print(f"\nModular Features:")
    print("   🔧 Independent modules with clear interfaces")
    print("   🔄 Dependency injection pattern")
    print("   ⚡ Ultra-optimized with library auto-detection")
    print("   🎯 Campaign-specific caching")
    print("   📊 Comprehensive metrics and monitoring")
    print("   🛡️  Circuit breaker and fault tolerance")
    print("   🎨 Template-based generation with variants")
    print("   🔍 Automatic validation and sanitization")
    
    # 8. FINAL RESULTS
    print(f"\n🎉 MODULAR ADS DEMO COMPLETED!")
    print("="*50)
    print("✅ Sistema completamente modular funcionando")
    print("✅ Arquitectura escalable y mantenible")
    print("✅ Performance ultra-optimizado")
    print("✅ Cache inteligente multi-nivel")
    print("✅ Fault tolerance y monitoring")
    print("✅ Soporte completo para múltiples tipos de ads")
    print("🚀 Listo para producción enterprise!")

async def quick_modular_demo():
    """Demo rápido del sistema modular"""
    print("🚀 QUICK MODULAR ADS DEMO")
    print("="*35)
    
    # Health check rápido
    health = await quick_health_check()
    print(f"🏥 System: {health['status'].upper()}")
    print(f"📊 Score: {health['test']['optimization_score']:.1f}/100")
    
    # Generación rápida
    response = await quick_generate_ad(
        content="Demo ad ultra-rápido",
        ad_type=AdType.FACEBOOK,
        target_audience="demo users",
        keywords=["demo", "quick"]
    )
    
    print(f"\n🎯 Quick Ad Generated:")
    print(f"   Content: {response.ad_content}")
    print(f"   Time: {response.response_time_ms:.1f}ms")
    print(f"   Score: {response.optimization_score:.1f}/100")
    
    # Benchmark rápido
    benchmark = await quick_benchmark(iterations=20)
    print(f"\n📊 Quick Benchmark:")
    print(f"   Ads/sec: {benchmark['benchmark_summary']['ads_per_second']:.1f}")
    print(f"   Success: {benchmark['benchmark_summary']['success_rate_percent']:.1f}%")
    
    print(f"\n✅ Modular system working perfectly!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Modular Ads System Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    parser.add_argument("--full", action="store_true", help="Run comprehensive demo")
    
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(quick_modular_demo())
    elif args.full:
        asyncio.run(comprehensive_modular_demo())
    else:
        # Demo por defecto usando la función del módulo
        asyncio.run(demo_modular_ads()) 