#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Iterable


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def write_lines(path: str, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_csv(path: str, rows: Iterable[list[str]], header: list[str]) -> None:
    import csv

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def trim_to_length(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    trimmed = text[: limit - 1].rstrip()
    # avoid cutting last word too ugly
    if " " in trimmed:
        trimmed = trimmed.rsplit(" ", 1)[0]
    return trimmed + "…"


def generate_variants(
    base_hooks: list[str],
    benefits: list[str],
    ctas: list[str],
    emojis: list[str],
    offer_hashtags: list[str],
    tone_mods: list[str],
    niches: list[str],
    proofs: list[str],
    url_template: str,
    max_variants: int = 1000,
    char_limit: int = 150,
) -> tuple[list[str], list[list[str]]]:
    templates = [
        "{emoji} {hook}. {benefit}. {cta}. {tags} {tone}",
        "{emoji} {hook}: {benefit}. {cta} {tags} {tone}",
        "{emoji} {hook} | {benefit} | {cta} {tags} {tone}",
        "{emoji} {hook} {proof}. {benefit}. {cta} {tags}",
        "{emoji} {niche}: {hook}. {benefit}. {cta} {tags}",
        "{emoji} {hook} — {benefit}. {cta} · {tone} {tags}",
        "{emoji} {hook}. {benefit}. {cta} → {url} {tags}",
        "{emoji} {hook}? {benefit}. {cta}! {tags} {tone}",
        "{emoji} {hook}. {benefit} ({niche}). {cta} {tags}",
    ]

    seen: set[str] = set()
    lines: list[str] = []
    csv_rows: list[list[str]] = []

    i = 0
    while len(lines) < max_variants:
        hook = base_hooks[i % len(base_hooks)]
        benefit = benefits[i % len(benefits)]
        cta = ctas[i % len(ctas)]
        emoji = emojis[i % len(emojis)]
        tags = offer_hashtags[i % len(offer_hashtags)]
        tone = tone_mods[i % len(tone_mods)]
        niche = niches[i % len(niches)]
        proof = proofs[i % len(proofs)]
        url = url_template.format(slug="campana")

        template = templates[i % len(templates)]
        raw = template.format(
            emoji=emoji,
            hook=hook,
            benefit=benefit,
            cta=cta,
            tags=tags,
            tone=tone,
            niche=niche,
            proof=proof,
            url=url,
        ).strip()
        line = trim_to_length(raw, char_limit)

        if line not in seen:
            seen.add(line)
            lines.append(line)
            csv_rows.append([hook, benefit, cta, emoji, tags, tone, niche, proof, url, line])
        i += 1

    return lines, csv_rows


def curso_ia_content() -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    hooks = [
        "Domina IA desde cero en 4 semanas",
        "Aprende IA práctica con sesiones en vivo",
        "Curso intensivo de IA + webinars exclusivos",
        "DALE superpoderes a tu trabajo con IA",
        "De principiante a pro en IA aplicada",
        "Tu primera automatización con IA esta semana",
        "IA para negocio: de teoría a resultados",
        "Certifícate en IA con proyectos reales",
        "Aprende prompts efectivos paso a paso",
        "Lleva IA a tu rutina diaria hoy",
    ]

    benefits = [
        "plantillas listas para usar",
        "proyectos reales guiados",
        "soporte de mentores",
        "comunidad activa",
        "grabaciones disponibles",
        "diploma al finalizar",
        "casos de uso por industria",
        "checklists descargables",
        "recursos actualizados cada semana",
        "resultados medibles desde el día 1",
    ]

    ctas = [
        "Inscríbete hoy",
        "Reserva tu cupo",
        "Únete ahora",
        "Empieza gratis",
        "Accede al taller",
        "Solicita info",
        "Mira el temario",
        "Asegura tu lugar",
        "Aplica al programa",
        "Comienza ahora",
    ]

    emojis = ["🚀", "✨", "🧠", "📚", "⚡", "✅", "🎯", "📈", "🛠️", "🏁"]
    hashtags = [
        "#CursoIA #Webinar #AprendeIA",
        "#InteligenciaArtificial #Capacitación #Live",
        "#IAAplicada #Formación #TrabajoReal",
        "#Automatización #Skills #Carrera",
        "#Productividad #Digital #Futuro",
        "#Aprendizaje #Mentoría #Proyectos",
        "#Prompts #IAparaTodos #Negocios",
        "#Comunidad #Grabaciones #Diploma",
        "#CasosDeUso #Resultados #Taller",
        "#Actualizado #Práctico #4Semanas",
    ]

    tones = [
        "Plazas limitadas",
        "Sin experiencia previa",
        "Certificado incluido",
        "En español",
        "Aplica a tu industria",
        "100% práctico",
        "Soporte en vivo",
        "Material descargable",
        "Comienza hoy",
        "Cupos reducidos",
    ]

    niches = [
        "Marketing", "Ventas", "RRHH", "Operaciones", "Producto",
        "Ecommerce", "Educación", "Finanzas", "Salud", "Turismo",
    ]
    proofs = [
        "+5,000 alumnos",
        "NPS 9.2",
        "4.8/5 en reseñas",
        "Metodología probada",
        "Casos reales",
        "Top instructores",
        "Alianzas con empresas",
        "Decenas de cohortes",
        "+100 plantillas",
        "Resultados verificables",
    ]

    return hooks, benefits, ctas, emojis, hashtags, tones, niches, proofs


def sass_marketing_content() -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    hooks = [
        "Convierte ideas en campañas con IA",
        "Tu asistente de marketing 24/7",
        "Genera copys y artes en minutos",
        "Acelera tu embudo con IA",
        "Contenido, ads y email en un clic",
        "Escala tu producción creativa",
        "Optimiza CTR y CPA con IA",
        "Brief in, campañas out",
        "IA que entiende tu marca",
        "Duplica output, no tu equipo",
    ]

    benefits = [
        "copys listos para publicar",
        "variantes A/B automáticas",
        "templates por canal",
        "assets on-brand",
        "ideas basadas en datos",
        "integración con tus herramientas",
        "pautas optimizadas",
        "workflows sin fricción",
        "recomendaciones en tiempo real",
        "reportes accionables",
    ]

    ctas = [
        "Pruébalo gratis",
        "Solicita demo",
        "Empieza ahora",
        "Crea tu primera campaña",
        "Activa tu prueba",
        "Ver planes",
        "Conéctalo hoy",
        "Lanza en minutos",
        "Optimiza ya",
        "Descubre cómo",
    ]

    emojis = ["🤖", "📣", "✍️", "🎨", "📊", "⚙️", "🧩", "🚀", "🔁", "💡"]
    hashtags = [
        "#MarketingAI #SaaS #Growth",
        "#Contenido #Automatización #Ads",
        "#Creatividad #Rendimiento #ABTesting",
        "#Branding #OnBrand #Campañas",
        "#CRM #Email #Social",
        "#Performance #DataDriven #Insights",
        "#Workflows #Eficiencia #Herramientas",
        "#Demostración #PruebaGratis #Planes",
        "#Escala #Equipos #Productividad",
        "#MarTech #IA #Innovación",
    ]

    tones = [
        "Sin tarjetas en prueba",
        "Listo en 5 minutos",
        "Seguro y privado",
        "Para pymes y equipos",
        "Multimarca",
        "Soporte en español",
        "Resultados rápidos",
        "GUI simple",
        "Listo para escalar",
        "Integraciones clave",
    ]

    niches = [
        "D2C", "B2B SaaS", "Agencias", "Retail", "Fintech",
        "Edtech", "Salud", "Inmobiliario", "Automotriz", "Turismo",
    ]
    proofs = [
        "+30% en CTR",
        "-25% en CPA",
        "ROI en 14 días",
        "+10K campañas generadas",
        "Benchmarks líderes",
        "Caso unicornio",
        "Preferido por agencias",
        "Uptime 99.9%",
        "SOC2 en progreso",
        "Soporte <2h",
    ]

    return hooks, benefits, ctas, emojis, hashtags, tones, niches, proofs


def ia_bulk_docs_content() -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    hooks = [
        "Crea documentos completos con 1 consulta",
        "Brief adentro, documento afuera",
        "Estandariza documentos al instante",
        "Documentación masiva con IA",
        "De idea a documento en minutos",
        "Genera PDFs y DOCX en lote",
        "Plantillas inteligentes a escala",
        "Automatiza propuestas y reportes",
        "Ahorra horas creando documentos",
        "Controla formato y tono al instante",
    ]

    benefits = [
        "estructuras consistentes",
        "formatos personalizables",
        "secciones auto-completadas",
        "tablas y resúmenes",
        "apéndices automáticos",
        "exportación multi-formato",
        "metadatos y numeración",
        "glosarios generados",
        "versionado simple",
        "revisiones rápidas",
    ]

    ctas = [
        "Genera tu primer documento",
        "Prueba en lote",
        "Carga tu plantilla",
        "Configura en minutos",
        "Empieza gratis",
        "Solicita acceso",
        "Ver ejemplos",
        "Exporta ahora",
        "Estandariza hoy",
        "Automatiza ya",
    ]

    emojis = ["📄", "🧠", "⚡", "📦", "🛠️", "📝", "📌", "📂", "⏱️", "✅"]
    hashtags = [
        "#Documentos #IA #Automatización",
        "#Estandarización #Plantillas #PDF",
        "#Reportes #Propuestas #DOCX",
        "#Escala #Consistencia #Lote",
        "#Operaciones #Productividad #Tiempo",
        "#Flujos #Calidad #Formato",
        "#Empresas #Procesos #Compliance",
        "#Exportación #Versionado #Revisión",
        "#Eficiencia #Bulk #Generación",
        "#Docs #AI #PlantillasInteligentes",
    ]

    tones = [
        "Configurable por rol",
        "Seguridad empresarial",
        "Logs y trazabilidad",
        "Sin código",
        "API disponible",
        "Plantillas listas",
        "Colaboración simple",
        "Control de calidad",
        "Listo para escalar",
        "Ahorra costos",
    ]

    niches = [
        "Legal", "Ventas", "Compras", "Operaciones", "TI",
        "Finanzas", "RRHH", "Consultoría", "Construcción", "Salud",
    ]
    proofs = [
        "Reduce 80% del tiempo",
        "Miles de docs al mes",
        "Errores mínimos",
        "Estandarización total",
        "Auditable",
        "Aprobado por compliance",
        "Plantillas validadas",
        "SLAs claros",
        "Tasa de adopción alta",
        "Onboarding en 1 hora",
    ]

    return hooks, benefits, ctas, emojis, hashtags, tones, niches, proofs


def main() -> None:
    out_dir = os.path.join(os.getcwd(), "copy_canva")
    ensure_dir(out_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Curso de IA + webinars
    c_hooks, c_benefits, c_ctas, c_emojis, c_tags, c_tones, c_niches, c_proofs = curso_ia_content()
    curso_lines, curso_csv = generate_variants(
        c_hooks, c_benefits, c_ctas, c_emojis, c_tags, c_tones, c_niches, c_proofs,
        url_template="https://tusitio.com/curso-ia?utm_source=canva&utm_campaign={slug}",
        max_variants=1000,
        char_limit=150,
    )
    curso_path = os.path.join(out_dir, f"curso_ia_variantes_{timestamp}.txt")
    write_lines(curso_path, curso_lines)
    curso_csv_path = os.path.join(out_dir, f"curso_ia_variantes_{timestamp}.csv")
    write_csv(curso_csv_path, curso_csv, header=[
        "hook","benefit","cta","emoji","hashtags","tone","niche","proof","url","copy"
    ])

    # SaaS de IA aplicado a marketing
    s_hooks, s_benefits, s_ctas, s_emojis, s_tags, s_tones, s_niches, s_proofs = sass_marketing_content()
    sass_lines, sass_csv = generate_variants(
        s_hooks, s_benefits, s_ctas, s_emojis, s_tags, s_tones, s_niches, s_proofs,
        url_template="https://tusitio.com/saas-marketing-ia?utm_source=canva&utm_campaign={slug}",
        max_variants=1000,
        char_limit=150,
    )
    sass_path = os.path.join(out_dir, f"sass_marketing_variantes_{timestamp}.txt")
    write_lines(sass_path, sass_lines)
    sass_csv_path = os.path.join(out_dir, f"sass_marketing_variantes_{timestamp}.csv")
    write_csv(sass_csv_path, sass_csv, header=[
        "hook","benefit","cta","emoji","hashtags","tone","niche","proof","url","copy"
    ])

    # IA bulk de documentos con una consulta
    b_hooks, b_benefits, b_ctas, b_emojis, b_tags, b_tones, b_niches, b_proofs = ia_bulk_docs_content()
    bulk_lines, bulk_csv = generate_variants(
        b_hooks, b_benefits, b_ctas, b_emojis, b_tags, b_tones, b_niches, b_proofs,
        url_template="https://tusitio.com/ia-bulk-docs?utm_source=canva&utm_campaign={slug}",
        max_variants=1000,
        char_limit=150,
    )
    bulk_path = os.path.join(out_dir, f"ia_bulk_docs_variantes_{timestamp}.txt")
    write_lines(bulk_path, bulk_lines)
    bulk_csv_path = os.path.join(out_dir, f"ia_bulk_docs_variantes_{timestamp}.csv")
    write_csv(bulk_csv_path, bulk_csv, header=[
        "hook","benefit","cta","emoji","hashtags","tone","niche","proof","url","copy"
    ])

    print("Generación completada:")
    print(f"- {curso_path}")
    print(f"- {curso_csv_path}")
    print(f"- {sass_path}")
    print(f"- {sass_csv_path}")
    print(f"- {bulk_path}")
    print(f"- {bulk_csv_path}")


if __name__ == "__main__":
    main()


