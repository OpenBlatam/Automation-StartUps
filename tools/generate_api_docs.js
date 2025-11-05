#!/usr/bin/env node
/**
 * Genera documentación de API/interfaz para los scripts del sistema
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const OUTPUT_FILE = path.join(ROOT_DIR, 'docs/API_DOCUMENTATION.md');

console.log('📚 Generando documentación de API...');
console.log('');

// Analizar scripts y extraer información
const toolsDir = path.join(ROOT_DIR, 'tools');
const scripts = [];

function analyzeScript(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const name = path.basename(filePath);
  const ext = path.extname(filePath);
  
  let description = '';
  let usage = '';
  let examples = [];
  
  // Extraer descripción (comentarios al inicio)
  const descMatch = content.match(/^#.*?\n([^\n]+)/m) || 
                   content.match(/\/\*\*?\s*([^\n]+)/);
  if (descMatch) {
    description = descMatch[1].trim();
  }
  
  // Buscar show_help o ayuda
  const helpMatch = content.match(/show_help\(\)[\s\S]*?EOF([\s\S]*?)EOF/);
  if (helpMatch) {
    usage = helpMatch[1].trim();
  }
  
  // Buscar ejemplos en comentarios
  const exampleMatches = content.matchAll(/Ejemplo[s]?:?\s*```?\s*bash\s*\n([^`]+)/gi);
  for (const match of exampleMatches) {
    examples.push(match[1].trim());
  }
  
  return {
    name,
    path: `tools/${name}`,
    type: ext === '.sh' ? 'Bash' : 'Node.js',
    description: description || 'Sin descripción',
    usage,
    examples: examples.slice(0, 3) // Máximo 3 ejemplos
  };
}

// Analizar todos los scripts
if (fs.existsSync(toolsDir)) {
  const files = fs.readdirSync(toolsDir);
  files.forEach(file => {
    if (file.endsWith('.sh') || file.endsWith('.js')) {
      const filePath = path.join(toolsDir, file);
      try {
        scripts.push(analyzeScript(filePath));
      } catch (e) {
        // Ignorar errores
      }
    }
  });
}

// Generar documentación
const doc = `# Documentación de API/Herramientas

Generada automáticamente: ${new Date().toLocaleString()}

**Total de herramientas**: ${scripts.length}

## Índice

${scripts.map((s, i) => `${i + 1}. [${s.name}](#${s.name.replace(/[^a-z0-9]/gi, '-').toLowerCase()})`).join('\n')}

---

${scripts.map(script => {
  return `## ${script.name}

**Tipo**: ${script.type}  
**Ruta**: \`${script.path}\`

### Descripción
${script.description}

${script.usage ? `### Uso
\`\`\`
${script.usage}
\`\`\`
` : ''}

${script.examples.length > 0 ? `### Ejemplos
${script.examples.map(ex => `\`\`\`bash
${ex}
\`\`\``).join('\n\n')}
` : ''}

`;
}).join('\n---\n\n')}

## Categorías

### Setup y Configuración
${scripts.filter(s => s.name.includes('install') || s.name.includes('setup') || s.name.includes('init')).map(s => `- [${s.name}](${s.path})`).join('\n')}

### Validación
${scripts.filter(s => s.name.includes('validate') || s.name.includes('check') || s.name.includes('health')).map(s => `- [${s.name}](${s.path})`).join('\n')}

### Generación y Exportación
${scripts.filter(s => s.name.includes('generate') || s.name.includes('export') || s.name.includes('build')).map(s => `- [${s.name}](${s.path})`).join('\n')}

### Análisis y Reportes
${scripts.filter(s => s.name.includes('analyze') || s.name.includes('report') || s.name.includes('summary')).map(s => `- [${s.name}](${s.path})`).join('\n')}

### Automatización
${scripts.filter(s => s.name.includes('auto') || s.name.includes('batch') || s.name.includes('sync')).map(s => `- [${s.name}](${s.path})`).join('\n')}

---

*Documentación generada automáticamente. Para actualizar, ejecuta: \`node tools/generate_api_docs.js\`*
`;

fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
fs.writeFileSync(OUTPUT_FILE, doc);

console.log('✅ Documentación generada:');
console.log(`   ${OUTPUT_FILE}`);
console.log('');
console.log(`📊 Resumen:`);
console.log(`   Scripts documentados: ${scripts.length}`);
console.log(`   Bash: ${scripts.filter(s => s.type === 'Bash').length}`);
console.log(`   Node.js: ${scripts.filter(s => s.type === 'Node.js').length}`);

