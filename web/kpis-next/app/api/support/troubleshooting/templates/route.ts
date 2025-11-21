/**
 * API para gestionar plantillas de troubleshooting
 */

import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';

const TEMPLATES_PATH = join(process.cwd(), 'data/integrations/troubleshooting_templates.json');

// Obtener plantillas
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get('category');
    const template_id = searchParams.get('template_id');

    const templatesData = JSON.parse(
      await readFile(TEMPLATES_PATH, 'utf-8')
    );

    if (template_id) {
      // Obtener plantilla específica
      if (templatesData[template_id]) {
        return NextResponse.json({
          template: templatesData[template_id]
        });
      } else {
        return NextResponse.json(
          { error: 'Template not found' },
          { status: 404 }
        );
      }
    }

    // Listar plantillas
    let templates = Object.entries(templatesData).map(([id, template]: [string, any]) => ({
      template_id: id,
      name: template.name,
      description: template.description,
      category: template.category,
      variables_count: template.variables?.length || 0,
      steps_count: template.steps_template?.length || 0
    }));

    // Filtrar por categoría si se especifica
    if (category) {
      templates = templates.filter(t => t.category === category);
    }

    return NextResponse.json({
      templates
    });

  } catch (error: any) {
    console.error('Error getting templates:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// Crear o actualizar plantilla
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { template_id, name, description, category, variables, steps_template, metadata } = body;

    if (!template_id || !name || !description || !category || !steps_template) {
      return NextResponse.json(
        { error: 'template_id, name, description, category, and steps_template are required' },
        { status: 400 }
      );
    }

    const templatesData = JSON.parse(
      await readFile(TEMPLATES_PATH, 'utf-8')
    );

    templatesData[template_id] = {
      name,
      description,
      category,
      variables: variables || [],
      steps_template,
      metadata: metadata || {}
    };

    await writeFile(
      TEMPLATES_PATH,
      JSON.stringify(templatesData, null, 2),
      'utf-8'
    );

    return NextResponse.json({
      success: true,
      template_id,
      message: 'Template saved successfully'
    });

  } catch (error: any) {
    console.error('Error saving template:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// Renderizar plantilla con variables
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { template_id, variables } = body;

    if (!template_id || !variables) {
      return NextResponse.json(
        { error: 'template_id and variables are required' },
        { status: 400 }
      );
    }

    const templatesData = JSON.parse(
      await readFile(TEMPLATES_PATH, 'utf-8')
    );

    if (!templatesData[template_id]) {
      return NextResponse.json(
        { error: 'Template not found' },
        { status: 404 }
      );
    }

    const template = templatesData[template_id];

    // Validar variables requeridas
    const requiredVars = template.variables?.filter((v: any) => v.required) || [];
    const missingVars = requiredVars.filter((v: any) => !(v.name in variables));

    if (missingVars.length > 0) {
      return NextResponse.json(
        { 
          error: 'Missing required variables',
          missing_variables: missingVars.map((v: any) => v.name)
        },
        { status: 400 }
      );
    }

    // Renderizar plantilla (simplificado - en producción usaría el manager de Python)
    const renderText = (text: string) => {
      return text.replace(/\{\{(\w+)\}\}/g, (match, varName) => {
        return variables[varName] || match;
      });
    };

    const rendered = {
      problem_title: renderText(template.name),
      problem_description: renderText(template.description),
      category: template.category,
      steps: template.steps_template.map((step: any) => ({
        ...step,
        title: renderText(step.title),
        description: renderText(step.description),
        instructions: step.instructions?.map((inst: string) => renderText(inst)),
        expected_result: renderText(step.expected_result),
        warnings: step.warnings?.map((w: string) => renderText(w)),
        resources: step.resources?.map((r: any) => ({
          ...r,
          title: renderText(r.title),
          url: renderText(r.url)
        }))
      })),
      metadata: template.metadata
    };

    return NextResponse.json({
      rendered_template: rendered
    });

  } catch (error: any) {
    console.error('Error rendering template:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



