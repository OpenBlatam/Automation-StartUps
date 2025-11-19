"""
API REST para Time Tracking
Endpoints para clock in/out, consultas y reportes
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal
from flask import Flask, request, jsonify
from flask_cors import CORS

from .storage import TimeTrackingStorage
from .clock_manager import ClockManager
from .session_manager import SessionManager
from .hour_calculator import TimeTrackingHourCalculator
from .geofencing import GeofencingValidator
from .timezone_manager import TimezoneManager
from .validators import TimeTrackingValidator

logger = logging.getLogger(__name__)


class TimeTrackingAPI:
    """API REST para gestión de tiempo"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
        self.clock_manager = ClockManager(storage)
        self.hour_calculator = TimeTrackingHourCalculator(storage)
        self.session_manager = SessionManager(
            storage, self.clock_manager, self.hour_calculator
        )
        self.geofencing = GeofencingValidator(storage)
        self.tz_manager = TimezoneManager(storage)
        self.validator = TimeTrackingValidator(storage)
        
        self.app = Flask(__name__)
        CORS(self.app)
        self._register_routes()
    
    def _register_routes(self):
        """Registra todas las rutas de la API"""
        
        @self.app.route('/api/time-tracking/clock-in', methods=['POST'])
        def clock_in():
            """Endpoint para clock in"""
            try:
                data = request.get_json()
                employee_id = data.get('employee_id')
                latitude = data.get('latitude')
                longitude = data.get('longitude')
                location_name = data.get('location')
                device_type = data.get('device_type', 'api')
                notes = data.get('notes')
                
                if not employee_id:
                    return jsonify({'error': 'employee_id is required'}), 400
                
                # Validar ubicación si se proporciona
                if latitude and longitude:
                    is_valid, error, location = self.geofencing.validate_location(
                        employee_id, latitude, longitude, location_name
                    )
                    if not is_valid:
                        return jsonify({
                            'error': 'Location not authorized',
                            'message': error,
                            'nearest_location': location
                        }), 403
                
                # Validar clock in
                event_time = datetime.now()
                is_valid, error = self.validator.validate_clock_in(employee_id, event_time)
                if not is_valid:
                    return jsonify({'error': error}), 400
                
                # Registrar clock in
                session_id = self.session_manager.start_session(
                    employee_id=employee_id,
                    clock_in_time=event_time,
                    location=location_name,
                    notes=notes
                )
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'clock_in_time': event_time.isoformat(),
                    'message': 'Clock in successful'
                }), 200
                
            except Exception as e:
                logger.error(f"Error in clock_in: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/time-tracking/clock-out', methods=['POST'])
        def clock_out():
            """Endpoint para clock out"""
            try:
                data = request.get_json()
                employee_id = data.get('employee_id')
                latitude = data.get('latitude')
                longitude = data.get('longitude')
                location_name = data.get('location')
                notes = data.get('notes')
                
                if not employee_id:
                    return jsonify({'error': 'employee_id is required'}), 400
                
                # Validar clock out
                event_time = datetime.now()
                is_valid, error = self.validator.validate_clock_out(employee_id, event_time)
                if not is_valid:
                    return jsonify({'error': error}), 400
                
                # Registrar clock out
                session_id = self.session_manager.end_session(
                    employee_id=employee_id,
                    clock_out_time=event_time,
                    notes=notes
                )
                
                if not session_id:
                    return jsonify({'error': 'No open session found'}), 404
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'clock_out_time': event_time.isoformat(),
                    'message': 'Clock out successful'
                }), 200
                
            except Exception as e:
                logger.error(f"Error in clock_out: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/time-tracking/status/<employee_id>', methods=['GET'])
        def get_status(employee_id):
            """Obtiene el estado actual del empleado"""
            try:
                today = date.today()
                open_session = self.storage.get_open_session(employee_id, today)
                
                if open_session:
                    clock_in_time = open_session['clock_in_time']
                    hours_open = (datetime.now() - clock_in_time).total_seconds() / 3600.0
                    
                    return jsonify({
                        'is_clocked_in': True,
                        'session_id': open_session['id'],
                        'clock_in_time': clock_in_time.isoformat(),
                        'hours_open': round(hours_open, 2),
                        'work_date': str(today)
                    }), 200
                else:
                    return jsonify({
                        'is_clocked_in': False,
                        'work_date': str(today)
                    }), 200
                    
            except Exception as e:
                logger.error(f"Error in get_status: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/time-tracking/summary/<employee_id>', methods=['GET'])
        def get_summary(employee_id):
            """Obtiene resumen de tiempo trabajado"""
            try:
                from datetime import timedelta
                
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                
                if not start_date:
                    start_date = (date.today() - timedelta(days=30)).isoformat()
                if not end_date:
                    end_date = date.today().isoformat()
                
                summary = self.session_manager.get_session_summary(
                    employee_id=employee_id,
                    start_date=date.fromisoformat(start_date),
                    end_date=date.fromisoformat(end_date)
                )
                
                return jsonify({
                    'employee_id': employee_id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'summary': {
                        'total_sessions': summary['total_sessions'],
                        'total_hours': float(summary['total_hours']),
                        'regular_hours': float(summary['regular_hours']),
                        'overtime_hours': float(summary['overtime_hours']),
                        'disputed_count': summary['disputed_count'],
                        'unapproved_count': summary['unapproved_count']
                    }
                }), 200
                
            except Exception as e:
                logger.error(f"Error in get_summary: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/time-tracking/vacation-balance/<employee_id>', methods=['GET'])
        def get_vacation_balance(employee_id):
            """Obtiene saldo de vacaciones"""
            try:
                balance = self.storage.get_vacation_balance(employee_id)
                
                return jsonify({
                    'employee_id': employee_id,
                    'balance': {
                        'vacation_days': float(balance['vacation_days']),
                        'sick_days': float(balance['sick_days']),
                        'personal_days': float(balance['personal_days'])
                    }
                }), 200
                
            except Exception as e:
                logger.error(f"Error in get_vacation_balance: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/time-tracking/alerts/<employee_id>', methods=['GET'])
        def get_alerts(employee_id):
            """Obtiene alertas activas del empleado"""
            try:
                from .notifications import TimeTrackingNotifier
                notifier = TimeTrackingNotifier(self.storage)
                alerts = notifier.get_active_alerts(employee_id)
                
                return jsonify({
                    'employee_id': employee_id,
                    'alerts': alerts
                }), 200
                
            except Exception as e:
                logger.error(f"Error in get_alerts: {e}")
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecuta el servidor Flask"""
        self.app.run(host=host, port=port, debug=debug)

