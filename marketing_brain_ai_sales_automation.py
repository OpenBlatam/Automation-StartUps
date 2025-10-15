"""
Marketing Brain AI Sales Automation Engine
Motor avanzado de automatización de ventas con IA
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class AISalesAutomationEngine:
    def __init__(self):
        self.lead_data = {}
        self.sales_models = {}
        self.automation_workflows = {}
        self.lead_scoring = {}
        self.sales_forecasting = {}
        self.performance_metrics = {}
        self.crm_integration = {}
        
    def load_lead_data(self, lead_data):
        """Cargar datos de leads"""
        if isinstance(lead_data, str):
            if lead_data.endswith('.csv'):
                self.lead_data = pd.read_csv(lead_data)
            elif lead_data.endswith('.json'):
                with open(lead_data, 'r') as f:
                    data = json.load(f)
                self.lead_data = pd.DataFrame(data)
        else:
            self.lead_data = pd.DataFrame(lead_data)
        
        print(f"✅ Datos de leads cargados: {len(self.lead_data)} registros")
        return True
    
    def build_lead_scoring_model(self, target_variable='converted'):
        """Construir modelo de scoring de leads"""
        if target_variable not in self.lead_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.lead_data.columns if col != target_variable and col != 'lead_id']
        X = self.lead_data[feature_columns]
        y = self.lead_data[target_variable]
        
        # Codificar variables categóricas
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
            label_encoders[column] = le
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entrenar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        model_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.sales_models['lead_scoring'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def score_leads(self, leads_data=None):
        """Calificar leads"""
        if leads_data is None:
            leads_data = self.lead_data
        
        if 'lead_scoring' not in self.sales_models:
            raise ValueError("Modelo de scoring de leads no encontrado. Ejecute build_lead_scoring_model() primero.")
        
        model_info = self.sales_models['lead_scoring']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        label_encoders = model_info['label_encoders']
        scaler = model_info['scaler']
        
        # Preparar datos
        X = leads_data[feature_columns]
        
        # Codificar variables categóricas
        for column in X.select_dtypes(include=['object']).columns:
            if column in label_encoders:
                le = label_encoders[column]
                X[column] = le.transform(X[column].astype(str))
        
        # Escalar datos
        X_scaled = scaler.transform(X)
        
        # Predecir scores
        scores = model.predict_proba(X_scaled)[:, 1]
        
        # Clasificar leads
        lead_classifications = []
        for score in scores:
            if score >= 0.8:
                classification = 'Hot'
            elif score >= 0.6:
                classification = 'Warm'
            elif score >= 0.4:
                classification = 'Cold'
            else:
                classification = 'Dead'
            
            lead_classifications.append(classification)
        
        # Crear DataFrame de resultados
        results = leads_data.copy()
        results['lead_score'] = scores
        results['lead_classification'] = lead_classifications
        results['scoring_date'] = datetime.now().isoformat()
        
        self.lead_scoring = results
        return results
    
    def build_sales_forecasting_model(self, target_variable='sales_amount'):
        """Construir modelo de forecasting de ventas"""
        if target_variable not in self.lead_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.lead_data.columns if col != target_variable and col != 'lead_id']
        X = self.lead_data[feature_columns]
        y = self.lead_data[target_variable]
        
        # Codificar variables categóricas
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
            label_encoders[column] = le
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entrenar modelo
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test_scaled)
        
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        model_metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.sales_models['sales_forecasting'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def forecast_sales(self, forecast_periods=12):
        """Predecir ventas futuras"""
        if 'sales_forecasting' not in self.sales_models:
            raise ValueError("Modelo de forecasting de ventas no encontrado. Ejecute build_sales_forecasting_model() primero.")
        
        model_info = self.sales_models['sales_forecasting']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        label_encoders = model_info['label_encoders']
        scaler = model_info['scaler']
        
        # Usar datos más recientes para predicción
        recent_data = self.lead_data.tail(1)[feature_columns]
        
        # Codificar variables categóricas
        for column in recent_data.select_dtypes(include=['object']).columns:
            if column in label_encoders:
                le = label_encoders[column]
                recent_data[column] = le.transform(recent_data[column].astype(str))
        
        # Escalar datos
        recent_data_scaled = scaler.transform(recent_data)
        
        # Generar predicciones
        predictions = []
        current_data = recent_data_scaled.copy()
        
        for period in range(forecast_periods):
            # Predecir siguiente período
            pred = model.predict(current_data)[0]
            predictions.append(pred)
            
            # Actualizar datos para siguiente predicción (simplificado)
            current_data[0][0] = pred  # Asumir que la primera característica es la variable objetivo
        
        # Crear fechas futuras
        future_dates = [datetime.now() + timedelta(days=30*i) for i in range(1, forecast_periods+1)]
        
        # Crear DataFrame de predicciones
        predictions_df = pd.DataFrame({
            'date': future_dates,
            'predicted_sales': predictions,
            'confidence_interval_lower': [p * 0.8 for p in predictions],
            'confidence_interval_upper': [p * 1.2 for p in predictions]
        })
        
        self.sales_forecasting = predictions_df
        return predictions_df
    
    def create_automation_workflows(self, workflow_configs):
        """Crear workflows de automatización de ventas"""
        for workflow_name, config in workflow_configs.items():
            workflow = {
                'name': workflow_name,
                'description': config.get('description', ''),
                'trigger': config['trigger'],
                'conditions': config.get('conditions', []),
                'actions': config['actions'],
                'target_audience': config.get('target_audience', 'all'),
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'performance': {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'conversion_rate': 0
                }
            }
            
            self.automation_workflows[workflow_name] = workflow
        
        return self.automation_workflows
    
    def execute_workflow(self, workflow_name, lead_data=None):
        """Ejecutar workflow de automatización"""
        if workflow_name not in self.automation_workflows:
            raise ValueError(f"Workflow {workflow_name} no encontrado")
        
        workflow = self.automation_workflows[workflow_name]
        
        if lead_data is None:
            lead_data = self.lead_data
        
        # Verificar condiciones del trigger
        if not self._check_workflow_conditions(workflow, lead_data):
            return {'status': 'skipped', 'reason': 'Workflow conditions not met'}
        
        # Obtener audiencia objetivo
        target_leads = self._get_target_leads(workflow, lead_data)
        
        # Ejecutar acciones
        execution_results = []
        for action in workflow['actions']:
            result = self._execute_sales_action(action, target_leads)
            execution_results.append(result)
            
            # Actualizar métricas de performance
            self._update_workflow_performance(workflow_name, result)
        
        return {
            'status': 'executed',
            'workflow': workflow_name,
            'target_leads_count': len(target_leads),
            'actions_executed': len(execution_results),
            'results': execution_results
        }
    
    def _check_workflow_conditions(self, workflow, lead_data):
        """Verificar condiciones del workflow"""
        trigger = workflow['trigger']
        conditions = workflow.get('conditions', [])
        
        if trigger['type'] == 'lead_score_based':
            # Verificar si hay leads con score alto
            if 'lead_scoring' in self.lead_scoring.columns:
                high_score_leads = self.lead_scoring[self.lead_scoring['lead_score'] >= trigger['min_score']]
                return len(high_score_leads) > 0
        
        elif trigger['type'] == 'time_based':
            # Verificar si es hora de ejecutar
            schedule_config = workflow.get('schedule', {})
            return self._check_schedule_condition(schedule_config)
        
        elif trigger['type'] == 'behavior_based':
            # Verificar comportamiento de leads
            if trigger['behavior'] in lead_data.columns:
                behavior_data = lead_data[lead_data[trigger['behavior']] == trigger['value']]
                return len(behavior_data) > 0
        
        return False
    
    def _check_schedule_condition(self, schedule_config):
        """Verificar condición de programación"""
        current_time = datetime.now()
        
        if 'frequency' in schedule_config:
            frequency = schedule_config['frequency']
            if frequency == 'daily':
                return True  # Simplificado para ejemplo
            elif frequency == 'weekly':
                return current_time.weekday() == schedule_config.get('day_of_week', 0)
            elif frequency == 'monthly':
                return current_time.day == schedule_config.get('day_of_month', 1)
        
        return False
    
    def _get_target_leads(self, workflow, lead_data):
        """Obtener leads objetivo"""
        target_audience = workflow.get('target_audience', 'all')
        
        if target_audience == 'all':
            return lead_data
        
        elif isinstance(target_audience, dict):
            if 'lead_classification' in target_audience:
                classification = target_audience['lead_classification']
                if 'lead_scoring' in self.lead_scoring.columns:
                    return self.lead_scoring[self.lead_scoring['lead_classification'] == classification]
        
        return lead_data
    
    def _execute_sales_action(self, action, target_leads):
        """Ejecutar acción de ventas"""
        action_type = action['type']
        
        if action_type == 'send_email':
            return self._send_sales_email(action, target_leads)
        elif action_type == 'schedule_call':
            return self._schedule_sales_call(action, target_leads)
        elif action_type == 'create_task':
            return self._create_sales_task(action, target_leads)
        elif action_type == 'update_lead_status':
            return self._update_lead_status(action, target_leads)
        elif action_type == 'assign_to_sales_rep':
            return self._assign_to_sales_rep(action, target_leads)
        
        return {'status': 'error', 'message': f'Unknown action type: {action_type}'}
    
    def _send_sales_email(self, action, target_leads):
        """Enviar email de ventas"""
        template = action.get('template', 'default')
        subject = action.get('subject', 'Sales Follow-up')
        
        # Simular envío de email
        sent_count = 0
        for lead in target_leads.head(50):  # Limitar para ejemplo
            # Aquí iría la lógica real de envío
            sent_count += 1
        
        return {
            'action_type': 'send_email',
            'status': 'success',
            'sent_count': sent_count,
            'template': template,
            'subject': subject
        }
    
    def _schedule_sales_call(self, action, target_leads):
        """Programar llamada de ventas"""
        call_type = action.get('call_type', 'follow_up')
        priority = action.get('priority', 'medium')
        
        # Simular programación de llamadas
        scheduled_count = 0
        for lead in target_leads.head(20):  # Limitar para ejemplo
            # Aquí iría la lógica real de programación
            scheduled_count += 1
        
        return {
            'action_type': 'schedule_call',
            'status': 'success',
            'scheduled_count': scheduled_count,
            'call_type': call_type,
            'priority': priority
        }
    
    def _create_sales_task(self, action, target_leads):
        """Crear tarea de ventas"""
        task_type = action.get('task_type', 'follow_up')
        due_date = action.get('due_date', '24h')
        
        # Simular creación de tareas
        created_count = 0
        for lead in target_leads.head(30):  # Limitar para ejemplo
            # Aquí iría la lógica real de creación
            created_count += 1
        
        return {
            'action_type': 'create_task',
            'status': 'success',
            'created_count': created_count,
            'task_type': task_type,
            'due_date': due_date
        }
    
    def _update_lead_status(self, action, target_leads):
        """Actualizar estado del lead"""
        new_status = action.get('new_status', 'contacted')
        
        # Simular actualización de estado
        updated_count = 0
        for lead in target_leads:
            # Aquí iría la lógica real de actualización
            updated_count += 1
        
        return {
            'action_type': 'update_lead_status',
            'status': 'success',
            'updated_count': updated_count,
            'new_status': new_status
        }
    
    def _assign_to_sales_rep(self, action, target_leads):
        """Asignar lead a representante de ventas"""
        sales_rep = action.get('sales_rep', 'auto_assign')
        
        # Simular asignación
        assigned_count = 0
        for lead in target_leads:
            # Aquí iría la lógica real de asignación
            assigned_count += 1
        
        return {
            'action_type': 'assign_to_sales_rep',
            'status': 'success',
            'assigned_count': assigned_count,
            'sales_rep': sales_rep
        }
    
    def _update_workflow_performance(self, workflow_name, result):
        """Actualizar métricas de performance del workflow"""
        if workflow_name in self.automation_workflows:
            workflow = self.automation_workflows[workflow_name]
            performance = workflow['performance']
            
            if result['status'] == 'success':
                performance['total_executions'] += 1
                performance['successful_executions'] += 1
                
                # Calcular tasa de conversión
                if performance['total_executions'] > 0:
                    performance['conversion_rate'] = performance['successful_executions'] / performance['total_executions']
    
    def analyze_sales_performance(self):
        """Analizar performance de ventas"""
        if self.lead_data.empty:
            return None
        
        # Métricas básicas
        total_leads = len(self.lead_data)
        converted_leads = len(self.lead_data[self.lead_data['converted'] == 1]) if 'converted' in self.lead_data.columns else 0
        conversion_rate = converted_leads / total_leads if total_leads > 0 else 0
        
        # Análisis por fuente
        if 'lead_source' in self.lead_data.columns:
            source_analysis = self.lead_data.groupby('lead_source').agg({
                'converted': 'sum' if 'converted' in self.lead_data.columns else lambda x: 0,
                'lead_id': 'count'
            }).reset_index()
            source_analysis['conversion_rate'] = source_analysis['converted'] / source_analysis['lead_id']
        else:
            source_analysis = pd.DataFrame()
        
        # Análisis por segmento
        if 'lead_segment' in self.lead_data.columns:
            segment_analysis = self.lead_data.groupby('lead_segment').agg({
                'converted': 'sum' if 'converted' in self.lead_data.columns else lambda x: 0,
                'lead_id': 'count'
            }).reset_index()
            segment_analysis['conversion_rate'] = segment_analysis['converted'] / segment_analysis['lead_id']
        else:
            segment_analysis = pd.DataFrame()
        
        # Análisis temporal
        if 'created_date' in self.lead_data.columns:
            self.lead_data['created_date'] = pd.to_datetime(self.lead_data['created_date'])
            self.lead_data['month'] = self.lead_data['created_date'].dt.to_period('M')
            
            monthly_analysis = self.lead_data.groupby('month').agg({
                'converted': 'sum' if 'converted' in self.lead_data.columns else lambda x: 0,
                'lead_id': 'count'
            }).reset_index()
            monthly_analysis['conversion_rate'] = monthly_analysis['converted'] / monthly_analysis['lead_id']
        else:
            monthly_analysis = pd.DataFrame()
        
        performance_analysis = {
            'total_leads': total_leads,
            'converted_leads': converted_leads,
            'overall_conversion_rate': conversion_rate,
            'source_analysis': source_analysis.to_dict('records') if not source_analysis.empty else [],
            'segment_analysis': segment_analysis.to_dict('records') if not segment_analysis.empty else [],
            'monthly_analysis': monthly_analysis.to_dict('records') if not monthly_analysis.empty else [],
            'analysis_date': datetime.now().isoformat()
        }
        
        self.performance_metrics = performance_analysis
        return performance_analysis
    
    def create_sales_dashboard(self):
        """Crear dashboard de automatización de ventas"""
        if not self.lead_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Lead Scoring', 'Sales Forecasting',
                          'Workflow Performance', 'Sales Performance'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Gráfico de lead scoring
        if 'lead_scoring' in self.lead_scoring.columns:
            lead_classifications = self.lead_scoring['lead_classification'].value_counts()
            fig.add_trace(
                go.Bar(x=lead_classifications.index, y=lead_classifications.values, name='Lead Classifications'),
                row=1, col=1
            )
        
        # Gráfico de sales forecasting
        if 'sales_forecasting' in self.sales_forecasting.columns:
            forecast_data = self.sales_forecasting
            fig.add_trace(
                go.Scatter(
                    x=forecast_data['date'],
                    y=forecast_data['predicted_sales'],
                    mode='lines',
                    name='Sales Forecast'
                ),
                row=1, col=2
            )
        
        # Gráfico de workflow performance
        if self.automation_workflows:
            workflow_names = list(self.automation_workflows.keys())
            execution_counts = [workflow['performance']['total_executions'] for workflow in self.automation_workflows.values()]
            
            fig.add_trace(
                go.Bar(x=workflow_names, y=execution_counts, name='Workflow Executions'),
                row=2, col=1
            )
        
        # Gráfico de sales performance
        if self.performance_metrics:
            performance = self.performance_metrics
            if 'source_analysis' in performance and performance['source_analysis']:
                sources = [item['lead_source'] for item in performance['source_analysis']]
                conversion_rates = [item['conversion_rate'] for item in performance['source_analysis']]
                
                fig.add_trace(
                    go.Pie(labels=sources, values=conversion_rates, name='Conversion by Source'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Automatización de Ventas con IA",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_sales_analysis(self, filename='ai_sales_automation_analysis.json'):
        """Exportar análisis de automatización de ventas"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'lead_scoring': self.lead_scoring.to_dict('records') if 'lead_scoring' in self.lead_scoring.columns else [],
            'sales_forecasting': self.sales_forecasting.to_dict('records') if 'sales_forecasting' in self.sales_forecasting.columns else [],
            'automation_workflows': self.automation_workflows,
            'performance_metrics': self.performance_metrics,
            'summary': {
                'total_leads': len(self.lead_data),
                'total_workflows': len(self.automation_workflows),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de automatización de ventas exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del motor de automatización de ventas
    sales_automation = AISalesAutomationEngine()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'lead_id': range(1000),
        'lead_source': np.random.choice(['Website', 'Social Media', 'Email', 'Referral'], 1000),
        'lead_segment': np.random.choice(['Enterprise', 'SMB', 'Startup'], 1000),
        'company_size': np.random.choice(['1-10', '11-50', '51-200', '200+'], 1000),
        'industry': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Retail'], 1000),
        'budget': np.random.normal(50000, 15000, 1000),
        'decision_timeline': np.random.choice(['1 month', '3 months', '6 months', '1 year'], 1000),
        'pain_points': np.random.choice(['Cost', 'Efficiency', 'Scalability', 'Security'], 1000),
        'engagement_score': np.random.uniform(0, 10, 1000),
        'converted': np.random.choice([0, 1], 1000, p=[0.7, 0.3]),
        'sales_amount': np.random.normal(100000, 30000, 1000),
        'created_date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de leads
    print("📊 Cargando datos de leads...")
    sales_automation.load_lead_data(sample_data)
    
    # Construir modelo de scoring de leads
    print("🎯 Construyendo modelo de scoring de leads...")
    scoring_metrics = sales_automation.build_lead_scoring_model()
    
    # Calificar leads
    print("📈 Calificando leads...")
    lead_scores = sales_automation.score_leads()
    
    # Construir modelo de forecasting de ventas
    print("🔮 Construyendo modelo de forecasting de ventas...")
    forecasting_metrics = sales_automation.build_sales_forecasting_model()
    
    # Predecir ventas
    print("💰 Prediciendo ventas...")
    sales_forecast = sales_automation.forecast_sales(12)
    
    # Crear workflows de automatización
    print("🔄 Creando workflows de automatización...")
    workflow_configs = {
        'Hot Lead Follow-up': {
            'description': 'Seguimiento automático para leads calientes',
            'trigger': {'type': 'lead_score_based', 'min_score': 0.8},
            'actions': [
                {'type': 'send_email', 'template': 'hot_lead', 'subject': 'Urgent: Let\'s discuss your needs'},
                {'type': 'schedule_call', 'call_type': 'discovery', 'priority': 'high'},
                {'type': 'assign_to_sales_rep', 'sales_rep': 'senior_rep'}
            ],
            'target_audience': {'lead_classification': 'Hot'}
        },
        'Warm Lead Nurturing': {
            'description': 'Nutrición de leads tibios',
            'trigger': {'type': 'lead_score_based', 'min_score': 0.6},
            'actions': [
                {'type': 'send_email', 'template': 'nurture', 'subject': 'More information about our solution'},
                {'type': 'create_task', 'task_type': 'follow_up', 'due_date': '48h'}
            ],
            'target_audience': {'lead_classification': 'Warm'}
        }
    }
    
    workflows = sales_automation.create_automation_workflows(workflow_configs)
    
    # Ejecutar workflows
    print("⚡ Ejecutando workflows de automatización...")
    for workflow_name in workflows.keys():
        result = sales_automation.execute_workflow(workflow_name)
        print(f"Workflow {workflow_name}: {result['status']}")
    
    # Analizar performance de ventas
    print("📊 Analizando performance de ventas...")
    performance_analysis = sales_automation.analyze_sales_performance()
    
    # Crear dashboard
    print("📈 Creando dashboard de automatización de ventas...")
    dashboard = sales_automation.create_sales_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de automatización de ventas...")
    export_data = sales_automation.export_sales_analysis()
    
    print("✅ Sistema de automatización de ventas con IA completado!")




