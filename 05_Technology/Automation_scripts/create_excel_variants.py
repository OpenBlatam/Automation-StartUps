import pandas as pd
import numpy as np

# Create comprehensive data for 1000 variants
data = []

# Categories and their ranges
categories = [
    ('Urgencia Temporal', 1, 100, 'Urgencia'),
    ('Beneficio', 101, 200, 'Beneficio'),
    ('Curiosidad', 201, 300, 'Curiosidad'),
    ('Autoridad', 301, 400, 'Autoridad'),
    ('Problema', 401, 500, 'Problema'),
    ('Storytelling', 501, 600, 'Storytelling'),
    ('Contraste', 601, 700, 'Contraste'),
    ('Pregunta', 701, 800, 'Pregunta'),
    ('Estadistica', 801, 900, 'Estadistica'),
    ('Emocion', 901, 1000, 'Emocion')
]

# Sample titles, subtitles, and CTAs for each category
titles = {
    'Urgencia': [
        'Solo quedan 24 horas! Descubre el secreto que cambio la vida de 10,000+ emprendedores',
        'Solo 3 personas mas pueden unirse a este webinar privado',
        'Por tiempo limitado: Acceso GRATIS al webinar que vale $5,000',
        'Este webinar se cierra en 48 horas - No te lo pierdas',
        'ULTIMA OPORTUNIDAD: Webinar que nunca se repetira'
    ],
    'Beneficio': [
        'Como generar $10,000 en tu primer mes (sin experiencia previa)',
        'De empleado a emprendedor exitoso en 90 dias',
        'Cansado de trabajar 12 horas y ganar poco? Aqui esta la solucion',
        'Mientras otros luchan, tu puedes triunfar con este metodo',
        'De $0 a $50,000 en 6 meses - Historia real de Maria'
    ],
    'Curiosidad': [
        'El secreto que los millonarios no quieren que sepas',
        'El metodo prohibido que genera millones',
        'La tecnica oculta que usan los top 1%',
        'La formula secreta de los emprendedores exitosos',
        'La estrategia interna que usan las empresas Fortune 500'
    ],
    'Autoridad': [
        'El CEO de $100M te ensena su metodo',
        'El emprendedor del ano 2023 comparte sus secretos',
        '20 anos de experiencia condensados en 60 minutos',
        'El metodo que genero $50M en ventas',
        'Metodo avalado por 1,000+ emprendedores exitosos'
    ],
    'Problema': [
        'Cansado de trabajar 12 horas y ganar $3,000 al mes?',
        'Frustrado porque nada funciona para generar ingresos?',
        'Preocupado por tu futuro financiero?',
        'Desesperado por cambiar tu situacion financiera?',
        'Confundido por toda la informacion contradictoria?'
    ],
    'Storytelling': [
        'De la quiebra a los $10M: Mi historia real',
        'Como pase de $0 a $100,000 en 6 meses',
        'El error de $50,000 que me enseno a triunfar',
        'El dia que decidi cambiar mi vida para siempre',
        'Como supere el obstaculo que casi me destruye'
    ],
    'Contraste': [
        'De $3,000 a $30,000 al mes: La transformacion completa',
        'De 5 negocios fallidos a 1 imperio exitoso',
        'De empleado frustrado a emprendedor exitoso',
        'De la pobreza a la riqueza en 2 anos',
        'De la confusion total a la claridad absoluta'
    ],
    'Pregunta': [
        'Quieres generar $10,000 este mes?',
        'Por que algunos emprendedores triunfan mientras otros fallan?',
        'Estas listo para cambiar tu vida para siempre?',
        'Te sientes atrapado en tu situacion actual?',
        'Suenas con la libertad financiera?'
    ],
    'Estadistica': [
        'El 90% de los emprendedores fallan en el primer ano',
        '1,247 emprendedores ya cambiaron su vida con este metodo',
        'El 95% de exito con este metodo probado',
        'Crecimiento del 300% en solo 6 meses',
        'Resultados en 30 dias o menos'
    ],
    'Emocion': [
        'Despierta el emprendedor que llevas dentro',
        'La motivacion que necesitas para triunfar',
        'La esperanza que estabas buscando',
        'Recupera la confianza en ti mismo',
        'Reaviva la pasion por tu negocio'
    ]
}

subtitles = {
    'Urgencia': [
        'Unete a este webinar exclusivo antes de que sea demasiado tarde',
        'El metodo que genero $2M en 6 meses - Revelado por primera vez',
        'Normalmente $5,000 - Hoy GRATIS para los primeros 100',
        'La estrategia que usan los top 1% para generar ingresos pasivos',
        'El experto #1 en marketing digital revela sus secretos'
    ],
    'Beneficio': [
        'El metodo paso a paso que funciona para cualquiera',
        'La guia completa para hacer la transicion',
        'Descubre como trabajar menos y ganar mas',
        'La diferencia entre el exito y el fracaso',
        'Descubre exactamente como lo logro'
    ],
    'Curiosidad': [
        'Por primera vez, revelado al publico',
        'Lo que las grandes corporaciones no quieren que sepas',
        'Nunca antes ensenada publicamente',
        'Revelada por primera vez en este webinar',
        'Ahora disponible para emprendedores'
    ],
    'Autoridad': [
        'Lecciones de 20 anos construyendo imperios',
        'La metodologia que lo llevo al reconocimiento',
        'Todo lo que necesitas saber para triunfar',
        'Comprobado en 100+ empresas',
        'Sus resultados hablan por si solos'
    ],
    'Problema': [
        'Hay una mejor manera de vivir',
        'El problema no eres tu, es el metodo',
        'Toma control de tu destino hoy',
        'La solucion esta aqui',
        'Aqui esta la claridad que necesitas'
    ],
    'Storytelling': [
        'Los errores que cometi y como los corrigi',
        'El momento que cambio todo',
        'La leccion que cambio mi perspectiva',
        'Y como puedes hacer lo mismo',
        'Y como puedes superar el tuyo'
    ],
    'Contraste': [
        'Descubre exactamente como lo logre',
        'La diferencia que marco todo',
        'El cambio que cambio todo',
        'El metodo que lo hizo posible',
        'El momento que cambio mi perspectiva'
    ],
    'Pregunta': [
        'Te muestro exactamente como hacerlo',
        'La respuesta te sorprendera',
        'Porque esto es lo que va a pasar',
        'Hay una salida, y te la muestro',
        'Hagamos que ese sueno sea realidad'
    ],
    'Estadistica': [
        'Descubre como ser parte del 10% que triunfa',
        'Seras el siguiente?',
        'Las estadisticas no mienten',
        'Con este metodo comprobado',
        'Garantizado o te devuelvo tu dinero'
    ],
    'Emocion': [
        'Es hora de vivir la vida que mereces',
        'Transforma tu mentalidad hoy',
        'Tu futuro brillante comienza aqui',
        'Eres mas capaz de lo que crees',
        'Descubre el proposito que te mueve'
    ]
}

ctas = {
    'Urgencia': [
        'Reserva tu lugar AHORA - Solo 50 cupos disponibles',
        'Acceso inmediato - Ultimos cupos',
        'Obtener acceso GRATIS ahora',
        'Inscribete antes del cierre',
        'Asegura tu lugar YA'
    ],
    'Beneficio': [
        'Quiero generar $10,000 este mes',
        'Iniciar mi transformacion',
        'Quiero la solucion',
        'Elegir el exito',
        'Quiero replicar su exito'
    ],
    'Curiosidad': [
        'Revelar el secreto',
        'Descubrir el metodo',
        'Aprender la tecnica',
        'Obtener la formula',
        'Acceder a la estrategia'
    ],
    'Autoridad': [
        'Aprender del experto',
        'Aprender del ganador',
        'Aprovechar la experiencia',
        'Aplicar el metodo',
        'Unirme a los exitosos'
    ],
    'Problema': [
        'Descubrir la mejor manera',
        'Encontrar el metodo correcto',
        'Tomar control ahora',
        'Encontrar la solucion',
        'Obtener claridad'
    ],
    'Storytelling': [
        'Escuchar mi historia',
        'Conocer el momento',
        'Aprender la leccion',
        'Hacer el cambio',
        'Superar mi obstaculo'
    ],
    'Contraste': [
        'Lograr la transformacion',
        'Conocer la diferencia',
        'Hacer el cambio',
        'Aplicar el metodo',
        'Obtener claridad'
    ],
    'Pregunta': [
        'Si, quiero generar $10,000',
        'Descubrir la respuesta',
        'Si, estoy listo',
        'Mostrarme la salida',
        'Hacer realidad mi sueno'
    ],
    'Estadistica': [
        'Ser parte del 10%',
        'Ser el siguiente',
        'Probar el metodo',
        'Lograr el crecimiento',
        'Garantizar mis resultados'
    ],
    'Emocion': [
        'Despertar mi potencial',
        'Transformar mi mentalidad',
        'Comenzar mi futuro',
        'Recuperar mi confianza',
        'Reavivar mi pasion'
    ]
}

# Generate 1000 variants
for cat_name, start, end, hook_type in categories:
    for i in range(start, end + 1):
        title_list = titles[hook_type]
        subtitle_list = subtitles[hook_type]
        cta_list = ctas[hook_type]
        
        # Use modulo to cycle through the lists
        title_idx = (i - start) % len(title_list)
        subtitle_idx = (i - start) % len(subtitle_list)
        cta_idx = (i - start) % len(cta_list)
        
        # Add some variation to make each unique
        variation = (i - start) // len(title_list)
        
        data.append({
            'ID': i,
            'Categoria': cat_name,
            'Titulo': title_list[title_idx] + (f' - Variante {variation + 1}' if variation > 0 else ''),
            'Subtitulo': subtitle_list[subtitle_idx] + (f' (Version {variation + 1})' if variation > 0 else ''),
            'CTA': cta_list[cta_idx] + (f' - Opcion {variation + 1}' if variation > 0 else ''),
            'Tipo_Hook': hook_type,
            'Palabras_Clave': f'hook_{hook_type.lower()}_{i}',
            'Urgencia': 'Alta' if hook_type == 'Urgencia' else 'Media' if hook_type in ['Problema', 'Pregunta'] else 'Baja',
            'Nivel_Emocional': 'Alta' if hook_type in ['Emocion', 'Storytelling', 'Urgencia'] else 'Media' if hook_type in ['Problema', 'Pregunta', 'Contraste'] else 'Baja'
        })

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('webinar_copywriting_variants_complete.xlsx', index=False)
print('Excel file created with 1000 variants')


