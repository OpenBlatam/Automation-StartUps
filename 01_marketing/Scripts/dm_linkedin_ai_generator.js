#!/usr/bin/env node
/**
 * Generador de DMs con IA (Claude/OpenAI)
 * Genera variantes personalizadas basadas en contexto del prospecto
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  apiKey: process.env.OPENAI_API_KEY || process.env.CLAUDE_API_KEY,
  model: process.env.AI_MODEL || 'gpt-4',
  templateFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_template_base.json'),
  outputFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_generated_variants.json'),
};

const TEMPLATE_PROMPT = `
Genera 3 variantes de DM de LinkedIn para:
- Producto: {PRODUCT}
- Prospecto: {NAME}, {ROLE} en {COMPANY}
- Industria: {INDUSTRY}
- Problema clave: {PAIN_POINT}

Requisitos:
- Máximo 200 caracteres
- Tono profesional pero cercano
- 1 CTA claro
- Incluye opt-out: "Si prefieres no recibir más mensajes, responde 'stop'"
- Variante A: Enfoque en problema
- Variante B: Enfoque en resultado/beneficio
- Variante C: Enfoque en social proof/urgencia

Formato JSON:
{
  "variants": [
    {
      "variant_id": "{PRODUCT}_A",
      "message": "...",
      "hook_type": "problem",
      "utm_content": "{PRODUCT}_Problem_A"
    },
    ...
  ]
}
`;

async function generateVariant(prospect, productInfo) {
  // Placeholder: Integra con OpenAI/Claude API
  // Por ahora retorna estructura base
  const prompt = TEMPLATE_PROMPT
    .replace('{PRODUCT}', productInfo.name)
    .replace('{NAME}', prospect.name)
    .replace('{ROLE}', prospect.role || 'profesional')
    .replace('{COMPANY}', prospect.company || 'tu empresa')
    .replace('{INDUSTRY}', prospect.industry || 'marketing')
    .replace('{PAIN_POINT}', productInfo.painPoint || 'falta de eficiencia');

  // TODO: Integrar con API real
  // const response = await fetch('https://api.openai.com/v1/chat/completions', {...});
  
  return {
    variants: [
      {
        variant_id: `${productInfo.id}_AI_A`,
        message: `Hola ${prospect.name}, veo que eres ${prospect.role} en ${prospect.company}. ${productInfo.painPoint} con IA puedes resolverlo en minutos. ¿Te muestro cómo? Si prefieres no recibir más mensajes, responde 'stop'.`,
        hook_type: 'problem',
        utm_content: `${productInfo.id}_Problem_AI_A`,
      },
      {
        variant_id: `${productInfo.id}_AI_B`,
        message: `Hola ${prospect.name}, ${prospect.role}s en tu industria ven +40% conversión con ${productInfo.name}. Tengo un recurso rápido (<10 min). ¿Te lo mando? Si prefieres no recibir más mensajes, responde 'stop'.`,
        hook_type: 'benefit',
        utm_content: `${productInfo.id}_Benefit_AI_B`,
      },
      {
        variant_id: `${productInfo.id}_AI_C`,
        message: `Hola ${prospect.name}, quedan pocos cupos para el demo de ${productInfo.name} esta semana. ¿Te anoto? Si prefieres no recibir más mensajes, responde 'stop'.`,
        hook_type: 'urgency',
        utm_content: `${productInfo.id}_Urgency_AI_C`,
      },
    ],
  };
}

async function generateBatch(prospects, productInfo) {
  const allVariants = [];
  for (const prospect of prospects) {
    const variants = await generateVariant(prospect, productInfo);
    allVariants.push(...variants.variants.map(v => ({
      ...v,
      prospect_name: prospect.name,
      prospect_company: prospect.company,
      prospect_role: prospect.role,
    })));
  }
  return allVariants;
}

async function main() {
  const prospects = [
    { name: 'Ana García', role: 'CMO', company: 'TechCorp', industry: 'SaaS' },
    { name: 'Luis Pérez', role: 'Marketing Manager', company: 'EcomStore', industry: 'E-commerce' },
  ];
  const productInfo = {
    id: 'curso_ia',
    name: 'Curso de IA Aplicada',
    painPoint: 'Pierdes 15h/semana en tareas manuales que IA puede automatizar',
  };
  
  const variants = await generateBatch(prospects, productInfo);
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(variants, null, 2), 'utf8');
  console.log(`✅ Generated ${variants.length} variants → ${CONFIG.outputFile}`);
}

if (require.main === module) {
  main().catch(console.error);
}




