# Salesforce Objects (outline) ↔ Airtable mapping

Lead
- Fields: Email (Leads.email), Company (Leads.empresa), Title (Leads.rol), Country (Leads.pais), LeadScore__c (Leads.score), UTM_Source__c (Leads.utm_source), UTM_Campaign__c (Leads.utm_campaign), Lifecycle__c (Leads.etapa)

Task
- Fields: Subject (Tareas.tipo), DueDate (Tareas.due_date), Status (Tareas.estado), OwnerId (Tareas.owner)

Custom Object: Evento__c
- Fields: Lead__c (lookup Lead), Tipo__c (Eventos.tipo), Producto__c (Eventos.producto), Metadata__c (Eventos.metadata_json), Timestamp__c (Eventos.timestamp)

Custom Object: Compra__c
- Fields: Lead__c, Oferta__c, Monto__c (Compras.monto), Fecha__c (Compras.fecha), Cupon__c (Compras.cupon), Metodo__c (Compras.metodo)

Custom Object: Webinar__c
- Fields: Titulo__c, Fecha__c, Registrados__c, Asistentes__c, Ventas__c (Webinars.*)

Custom Object: Demo__c
- Fields: Lead__c, Fecha__c, Resultado__c, Notas__c, SiguientePaso__c (Demos.*)

