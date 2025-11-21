-- ============================================================================
-- Templates de Comunicación Pre-configurados para ATS
-- ============================================================================

-- Template: Invitación a entrevista
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'interview_invite_standard',
    'Invitación a Entrevista - Estándar',
    'interview_invite',
    'Entrevista programada - {{job_title}}',
    'Hola {{candidate_name}},

Nos complace informarte que has sido seleccionado para una entrevista para el puesto de {{job_title}}.

Detalles de la entrevista:
- Fecha: {{interview_date}}
- Hora: {{interview_time}}
- Duración: {{duration}} minutos
- Tipo: {{interview_type}}
- Entrevistador: {{interviewer_name}}
- Link de reunión: {{meeting_link}}

Por favor confirma tu asistencia respondiendo a este email.

Saludos,
Equipo de Reclutamiento',
    '{"candidate_name": "string", "job_title": "string", "interview_date": "date", "interview_time": "time", "duration": "number", "interview_type": "string", "interviewer_name": "string", "meeting_link": "url"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

-- Template: Rechazo estándar
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'rejection_standard',
    'Rechazo Estándar',
    'rejection',
    'Actualización sobre tu aplicación - {{job_title}}',
    'Hola {{candidate_name}},

Gracias por tu interés en el puesto de {{job_title}} en nuestra empresa.

Después de revisar cuidadosamente tu perfil, hemos decidido seguir adelante con otros candidatos en esta ocasión.

Sin embargo, te animamos a estar atento a futuras oportunidades que puedan ser adecuadas para tu perfil.

Te deseamos mucho éxito en tu búsqueda profesional.

Saludos,
Equipo de Reclutamiento',
    '{"candidate_name": "string", "job_title": "string"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

-- Template: Oferta de trabajo
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'offer_standard',
    'Oferta de Trabajo - Estándar',
    'offer',
    '¡Felicitaciones! Oferta de trabajo - {{job_title}}',
    'Hola {{candidate_name}},

¡Felicitaciones! Estamos encantados de ofrecerte el puesto de {{job_title}}.

Detalles de la oferta:
- Puesto: {{job_title}}
- Departamento: {{department}}
- Ubicación: {{location}}
- Tipo: {{employment_type}}
- Fecha de inicio: {{start_date}}
- Salario: {{salary_range}}

Por favor, revisa los detalles adjuntos y confirma tu aceptación antes del {{offer_expiry_date}}.

Estamos emocionados de tenerte en nuestro equipo.

Saludos,
Equipo de Reclutamiento',
    '{"candidate_name": "string", "job_title": "string", "department": "string", "location": "string", "employment_type": "string", "start_date": "date", "salary_range": "string", "offer_expiry_date": "date"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

-- Template: Test de evaluación
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'assessment_test_standard',
    'Test de Evaluación - Estándar',
    'assessment_test',
    'Test de Evaluación - {{job_title}}',
    'Hola {{candidate_name}},

Como parte del proceso de selección para {{job_title}}, te invitamos a completar una evaluación.

Detalles del test:
- Tipo: {{test_type}}
- Duración estimada: {{duration}} minutos
- Fecha límite: {{due_date}}
- Link: {{test_url}}

Instrucciones:
{{test_instructions}}

Por favor completa el test antes de la fecha límite.

Saludos,
Equipo de Reclutamiento',
    '{"candidate_name": "string", "job_title": "string", "test_type": "string", "duration": "number", "due_date": "date", "test_url": "url", "test_instructions": "text"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

-- Template: Recordatorio de entrevista
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'interview_reminder',
    'Recordatorio de Entrevista',
    'interview_reminder',
    'Recordatorio: Entrevista mañana - {{job_title}}',
    'Hola {{candidate_name}},

Este es un recordatorio de que tienes una entrevista programada para mañana.

Detalles:
- Fecha: {{interview_date}}
- Hora: {{interview_time}}
- Link: {{meeting_link}}

Por favor confirma tu asistencia.

Saludos,
Equipo de Reclutamiento',
    '{"candidate_name": "string", "job_title": "string", "interview_date": "date", "interview_time": "time", "meeting_link": "url"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

-- Template: Bienvenida post-hire
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'welcome_post_hire',
    'Bienvenida Post-Contratación',
    'welcome',
    '¡Bienvenido a {{company_name}}!',
    'Hola {{candidate_name}},

¡Bienvenido a {{company_name}}!

Estamos emocionados de tenerte en nuestro equipo como {{job_title}}.

Tu fecha de inicio es {{start_date}}.

En los próximos días recibirás:
- Documentos de contratación
- Información sobre onboarding
- Accesos a sistemas
- Calendario de tu primera semana

Si tienes alguna pregunta, no dudes en contactarnos.

¡Nos vemos pronto!

Saludos,
Equipo de RRHH',
    '{"candidate_name": "string", "company_name": "string", "job_title": "string", "start_date": "date"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

-- Template: Feedback de entrevista
INSERT INTO ats_communication_templates (template_id, template_name, template_type, subject, body, variables, is_active)
VALUES (
    'feedback_request',
    'Solicitud de Feedback',
    'feedback_request',
    'Solicitud de feedback - Entrevista {{interview_type}}',
    'Hola {{interviewer_name}},

Solicitamos tu feedback sobre la entrevista con {{candidate_name}} para el puesto de {{job_title}}.

Por favor completa el formulario antes del {{deadline}}:
{{feedback_url}}

Gracias por tu tiempo.

Saludos,
Equipo de Reclutamiento',
    '{"interviewer_name": "string", "candidate_name": "string", "job_title": "string", "interview_type": "string", "deadline": "date", "feedback_url": "url"}',
    true
) ON CONFLICT (template_id) DO NOTHING;

