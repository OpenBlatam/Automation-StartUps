"""
Conectores para diferentes sistemas (CRM, ERP, Spreadsheets)
=============================================================

Proporciona interfaces unificadas para conectarse a diferentes sistemas
y sincronizar datos de manera consistente.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class SyncRecord:
    """Registro de sincronización individual"""
    source_id: str
    source_type: str
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    data: Dict[str, Any] = None
    checksum: Optional[str] = None
    status: str = "pending"  # pending, synced, failed, conflicted
    error_message: Optional[str] = None
    synced_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}
        if self.checksum is None and self.data:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calcula checksum SHA256 de los datos"""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


class BaseConnector(ABC):
    """Clase base para todos los conectores"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    @abstractmethod
    def connect(self) -> bool:
        """Establece conexión con el sistema"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Cierra conexión con el sistema"""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Verifica salud de la conexión"""
        pass
    
    @abstractmethod
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee registros del sistema"""
        pass
    
    @abstractmethod
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Escribe registros en el sistema"""
        pass
    
    @abstractmethod
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros existentes"""
        pass
    
    def validate_record(self, record: SyncRecord) -> Tuple[bool, Optional[str]]:
        """Valida un registro antes de sincronizar"""
        if not record.source_id:
            return False, "source_id es requerido"
        if not record.data:
            return False, "data no puede estar vacío"
        return True, None


class HubSpotConnector(BaseConnector):
    """Conector para HubSpot CRM"""
    
    def connect(self) -> bool:
        """Conecta a HubSpot API"""
        try:
            import requests
            token = self.config.get("api_token")
            if not token:
                raise ValueError("HubSpot API token requerido")
            
            # Test connection
            response = requests.get(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": 1},
                timeout=10
            )
            response.raise_for_status()
            self.logger.info("Conexión a HubSpot establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a HubSpot: {e}")
            return False
    
    def disconnect(self) -> None:
        """No requiere desconexión para API REST"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de HubSpot"""
        try:
            import requests
            token = self.config.get("api_token")
            start_time = datetime.now()
            
            response = requests.get(
                "https://api.hubapi.com/integrations/v1/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            response.raise_for_status()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee contactos/deals de HubSpot"""
        import requests
        token = self.config.get("api_token")
        object_type = filters.get("object_type", "contacts") if filters else "contacts"
        
        url = f"https://api.hubapi.com/crm/v3/objects/{object_type}"
        params = {"limit": limit or 100}
        
        if filters:
            if "properties" in filters:
                params["properties"] = ",".join(filters["properties"])
            if "createdAfter" in filters:
                params["createdAfter"] = filters["createdAfter"]
        
        records = []
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            for result in data.get("results", []):
                record = SyncRecord(
                    source_id=result.get("id"),
                    source_type=f"hubspot_{object_type}",
                    data=result.get("properties", {}),
                    metadata={"hubspot_data": result}
                )
                records.append(record)
            
            self.logger.info(f"Leídos {len(records)} registros de HubSpot")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de HubSpot: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Crea registros en HubSpot"""
        import requests
        token = self.config.get("api_token")
        results = []
        
        for record in records:
            object_type = record.data.get("object_type", "contacts")
            url = f"https://api.hubapi.com/crm/v3/objects/{object_type}"
            
            try:
                response = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={"properties": record.data},
                    timeout=30
                )
                response.raise_for_status()
                
                result_data = response.json()
                record.target_id = result_data.get("id")
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error escribiendo registro {record.source_id}: {e}")
                results.append(record)
        
        return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros en HubSpot"""
        import requests
        token = self.config.get("api_token")
        results = []
        
        for record in records:
            if not record.target_id:
                record.status = "failed"
                record.error_message = "target_id requerido para actualización"
                results.append(record)
                continue
            
            object_type = record.data.get("object_type", "contacts")
            url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/{record.target_id}"
            
            try:
                response = requests.patch(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={"properties": record.data},
                    timeout=30
                )
                response.raise_for_status()
                
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error actualizando registro {record.target_id}: {e}")
                results.append(record)
        
        return results


class QuickBooksConnector(BaseConnector):
    """Conector para QuickBooks Online"""
    
    def connect(self) -> bool:
        """Conecta a QuickBooks API"""
        try:
            access_token = self.config.get("access_token")
            realm_id = self.config.get("realm_id")
            base_url = self.config.get("base_url", "https://sandbox-quickbooks.api.intuit.com")
            
            if not access_token or not realm_id:
                raise ValueError("QuickBooks access_token y realm_id requeridos")
            
            # Test connection
            import requests
            url = f"{base_url}/v3/company/{realm_id}/query"
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                },
                params={"query": "SELECT * FROM CompanyInfo MAXRESULTS 1"},
                timeout=10
            )
            response.raise_for_status()
            self.logger.info("Conexión a QuickBooks establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a QuickBooks: {e}")
            return False
    
    def disconnect(self) -> None:
        """No requiere desconexión para API REST"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de QuickBooks"""
        try:
            import requests
            access_token = self.config.get("access_token")
            realm_id = self.config.get("realm_id")
            base_url = self.config.get("base_url", "https://sandbox-quickbooks.api.intuit.com")
            
            start_time = datetime.now()
            url = f"{base_url}/v3/company/{realm_id}/companyinfo/{realm_id}"
            
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                },
                timeout=5
            )
            response.raise_for_status()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee items/customers de QuickBooks"""
        import requests
        access_token = self.config.get("access_token")
        realm_id = self.config.get("realm_id")
        base_url = self.config.get("base_url", "https://sandbox-quickbooks.api.intuit.com")
        
        entity_type = filters.get("entity_type", "Item") if filters else "Item"
        max_results = limit or 20
        
        query = f"SELECT * FROM {entity_type} MAXRESULTS {max_results}"
        
        if filters and "updatedSince" in filters:
            query += f" WHERE MetaData.LastUpdatedTime > '{filters['updatedSince']}'"
        
        url = f"{base_url}/v3/company/{realm_id}/query"
        
        records = []
        try:
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                },
                params={"query": query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            for result in data.get("QueryResponse", {}).get(entity_type + "s", []):
                record = SyncRecord(
                    source_id=str(result.get("Id")),
                    source_type=f"quickbooks_{entity_type.lower()}",
                    data=result,
                    metadata={"quickbooks_data": result}
                )
                records.append(record)
            
            self.logger.info(f"Leídos {len(records)} registros de QuickBooks")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de QuickBooks: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Crea registros en QuickBooks"""
        import requests
        access_token = self.config.get("access_token")
        realm_id = self.config.get("realm_id")
        base_url = self.config.get("base_url", "https://sandbox-quickbooks.api.intuit.com")
        
        results = []
        
        for record in records:
            entity_type = record.data.get("entity_type", "Item")
            url = f"{base_url}/v3/company/{realm_id}/{entity_type.lower()}"
            
            try:
                response = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json=record.data,
                    timeout=30
                )
                response.raise_for_status()
                
                result_data = response.json()
                entity_result = result_data.get(f"{entity_type}Response", {}).get(entity_type, {})
                record.target_id = str(entity_result.get("Id"))
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error escribiendo registro {record.source_id}: {e}")
                results.append(record)
        
        return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros en QuickBooks"""
        import requests
        access_token = self.config.get("access_token")
        realm_id = self.config.get("realm_id")
        base_url = self.config.get("base_url", "https://sandbox-quickbooks.api.intuit.com")
        
        results = []
        
        for record in records:
            if not record.target_id:
                record.status = "failed"
                record.error_message = "target_id requerido para actualización"
                results.append(record)
                continue
            
            entity_type = record.data.get("entity_type", "Item")
            url = f"{base_url}/v3/company/{realm_id}/{entity_type.lower()}"
            
            # QuickBooks requiere SyncToken para updates
            if "SyncToken" not in record.data:
                record.data["SyncToken"] = record.metadata.get("sync_token", "0")
            
            try:
                response = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json=record.data,
                    timeout=30
                )
                response.raise_for_status()
                
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error actualizando registro {record.target_id}: {e}")
                results.append(record)
        
        return results


class GoogleSheetsConnector(BaseConnector):
    """Conector para Google Sheets"""
    
    def connect(self) -> bool:
        """Conecta a Google Sheets API"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            credentials_path = self.config.get("credentials_path")
            credentials_json = self.config.get("credentials_json")
            
            if credentials_json:
                import json
                creds = service_account.Credentials.from_service_account_info(
                    json.loads(credentials_json)
                )
            elif credentials_path:
                creds = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
            else:
                raise ValueError("Google Sheets credentials requeridas")
            
            self.service = build('sheets', 'v4', credentials=creds)
            self.logger.info("Conexión a Google Sheets establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a Google Sheets: {e}")
            return False
    
    def disconnect(self) -> None:
        """Cierra conexión"""
        self.service = None
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de Google Sheets"""
        try:
            spreadsheet_id = self.config.get("spreadsheet_id")
            if not spreadsheet_id:
                return {"status": "unhealthy", "error": "spreadsheet_id no configurado"}
            
            start_time = datetime.now()
            result = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "spreadsheet_title": result.get("properties", {}).get("title")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee filas de Google Sheets"""
        spreadsheet_id = self.config.get("spreadsheet_id")
        range_name = filters.get("range") if filters else "Sheet1!A:Z"
        
        records = []
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Primera fila como headers
            if not values:
                return records
            
            headers = values[0]
            rows = values[1:limit] if limit else values[1:]
            
            for idx, row in enumerate(rows):
                # Convertir fila a diccionario
                row_data = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_data[header] = row[i]
                
                record = SyncRecord(
                    source_id=f"row_{idx + 2}",  # +2 porque empieza en fila 2 (1 es header)
                    source_type="google_sheets",
                    data=row_data,
                    metadata={"row_number": idx + 2, "sheet": range_name}
                )
                records.append(record)
            
            self.logger.info(f"Leídos {len(records)} registros de Google Sheets")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de Google Sheets: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Escribe filas en Google Sheets (append)"""
        spreadsheet_id = self.config.get("spreadsheet_id")
        sheet_name = self.config.get("sheet_name", "Sheet1")
        
        results = []
        
        if not records:
            return results
        
        # Obtener headers del sheet o usar los de los datos
        try:
            # Leer primera fila para obtener headers
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!1:1"
            ).execute()
            
            headers = result.get('values', [[]])[0] if result.get('values') else []
            
            # Si no hay headers, usar los keys del primer registro
            if not headers and records:
                headers = list(records[0].data.keys())
                # Escribir headers primero
                self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!1:1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
        except Exception:
            # Si falla, usar headers del primer registro
            if records:
                headers = list(records[0].data.keys())
        
        # Preparar valores para escribir
        values = []
        for record in records:
            row = [record.data.get(header, "") for header in headers]
            values.append(row)
        
        try:
            # Append valores
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:Z",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': values}
            ).execute()
            
            # Actualizar registros con éxito
            for record in records:
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            
            self.logger.info(f"Escritos {len(results)} registros en Google Sheets")
        except Exception as e:
            self.logger.error(f"Error escribiendo en Google Sheets: {e}")
            for record in records:
                record.status = "failed"
                record.error_message = str(e)
                results.append(record)
        
        return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza filas en Google Sheets"""
        spreadsheet_id = self.config.get("spreadsheet_id")
        sheet_name = self.config.get("sheet_name", "Sheet1")
        
        results = []
        
        for record in records:
            # Extraer número de fila del source_id o metadata
            row_number = record.metadata.get("row_number")
            if not row_number:
                # Intentar extraer de source_id (formato: "row_2")
                try:
                    row_number = int(record.source_id.split("_")[1])
                except (IndexError, ValueError):
                    record.status = "failed"
                    record.error_message = "row_number no encontrado para actualización"
                    results.append(record)
                    continue
            
            # Obtener headers
            try:
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!1:1"
                ).execute()
                headers = result.get('values', [[]])[0] if result.get('values') else []
            except Exception:
                headers = list(record.data.keys())
            
            # Preparar valores
            values = [record.data.get(header, "") for header in headers]
            
            try:
                # Actualizar fila
                self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!{row_number}:{row_number}",
                    valueInputOption='RAW',
                    body={'values': [values]}
                ).execute()
                
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error actualizando fila {row_number}: {e}")
                results.append(record)
        
        return results


class DatabaseConnector(BaseConnector):
    """Conector para bases de datos (PostgreSQL/MySQL)"""
    
    def connect(self) -> bool:
        """Conecta a base de datos"""
        try:
            connection_string = self.config.get("connection_string")
            if not connection_string:
                raise ValueError("connection_string requerido")
            
            import psycopg2
            # Intentar conectar
            self.conn = psycopg2.connect(connection_string)
            self.logger.info("Conexión a base de datos establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a base de datos: {e}")
            return False
    
    def disconnect(self) -> None:
        """Cierra conexión"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.conn = None
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de base de datos"""
        try:
            if not hasattr(self, 'conn') or not self.conn:
                return {"status": "unhealthy", "error": "No hay conexión"}
            
            start_time = datetime.now()
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee registros de tabla"""
        table_name = filters.get("table_name") if filters else "sync_data"
        where_clause = filters.get("where") if filters else None
        order_by = filters.get("order_by", "id") if filters else "id"
        
        records = []
        try:
            cursor = self.conn.cursor()
            
            query = f"SELECT * FROM {table_name}"
            params = []
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            query += f" ORDER BY {order_by}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                # Usar id como source_id si existe
                source_id = str(row_dict.get("id", row_dict.get("uuid", "")))
                
                record = SyncRecord(
                    source_id=source_id,
                    source_type=f"database_{table_name}",
                    data=row_dict,
                    metadata={"table_name": table_name, "columns": columns}
                )
                records.append(record)
            
            cursor.close()
            self.logger.info(f"Leídos {len(records)} registros de base de datos")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de base de datos: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Inserta registros en tabla"""
        table_name = self.config.get("table_name", "sync_data")
        results = []
        
        if not records:
            return results
        
        try:
            cursor = self.conn.cursor()
            
            # Obtener columnas del primer registro
            columns = list(records[0].data.keys())
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            for record in records:
                values = [record.data.get(col) for col in columns]
                
                query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({placeholders})
                    RETURNING id
                """
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    record.target_id = str(result[0])
                    record.status = "synced"
                    record.synced_at = datetime.now()
                else:
                    record.status = "failed"
                    record.error_message = "No se obtuvo ID después de inserción"
                
                results.append(record)
            
            self.conn.commit()
            cursor.close()
            self.logger.info(f"Insertados {len([r for r in results if r.status == 'synced'])} registros")
            return results
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error insertando en base de datos: {e}")
            for record in records:
                record.status = "failed"
                record.error_message = str(e)
                results.append(record)
            return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros en tabla"""
        table_name = self.config.get("table_name", "sync_data")
        id_column = self.config.get("id_column", "id")
        results = []
        
        try:
            cursor = self.conn.cursor()
            
            for record in records:
                if not record.target_id:
                    record.status = "failed"
                    record.error_message = "target_id requerido para actualización"
                    results.append(record)
                    continue
                
                # Construir SET clause
                set_clauses = []
                values = []
                for key, value in record.data.items():
                    if key != id_column:
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                
                values.append(record.target_id)
                
                query = f"""
                    UPDATE {table_name}
                    SET {', '.join(set_clauses)}, updated_at = NOW()
                    WHERE {id_column} = %s
                """
                
                cursor.execute(query, values)
                
                if cursor.rowcount > 0:
                    record.status = "synced"
                    record.synced_at = datetime.now()
                else:
                    record.status = "failed"
                    record.error_message = "No se actualizó ningún registro"
                
                results.append(record)
            
            self.conn.commit()
            cursor.close()
            return results
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error actualizando en base de datos: {e}")
            for record in records:
                record.status = "failed"
                record.error_message = str(e)
                results.append(record)
            return results


class SalesforceConnector(BaseConnector):
    """Conector para Salesforce CRM"""
    
    def connect(self) -> bool:
        """Conecta a Salesforce API"""
        try:
            import requests
            username = self.config.get("username")
            password = self.config.get("password")
            security_token = self.config.get("security_token")
            client_id = self.config.get("client_id")
            client_secret = self.config.get("client_secret")
            sandbox = self.config.get("sandbox", False)
            
            if not all([username, password, client_id, client_secret]):
                raise ValueError("Credenciales de Salesforce requeridas")
            
            # OAuth2 login
            login_url = "https://test.salesforce.com" if sandbox else "https://login.salesforce.com"
            auth_url = f"{login_url}/services/oauth2/token"
            
            data = {
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password + security_token if security_token else password
            }
            
            response = requests.post(auth_url, data=data, timeout=10)
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data.get("access_token")
            self.instance_url = auth_data.get("instance_url")
            
            self.logger.info("Conexión a Salesforce establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a Salesforce: {e}")
            return False
    
    def disconnect(self) -> None:
        """No requiere desconexión para API REST"""
        self.access_token = None
        self.instance_url = None
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de Salesforce"""
        try:
            import requests
            if not hasattr(self, 'access_token') or not self.access_token:
                return {"status": "unhealthy", "error": "No autenticado"}
            
            start_time = datetime.now()
            response = requests.get(
                f"{self.instance_url}/services/data/v54.0/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=5
            )
            response.raise_for_status()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee objetos de Salesforce"""
        import requests
        sobject_type = filters.get("sobject_type", "Contact") if filters else "Contact"
        where_clause = filters.get("where") if filters else None
        
        records = []
        try:
            query = f"SELECT FIELDS(ALL) FROM {sobject_type}"
            if where_clause:
                query += f" WHERE {where_clause}"
            if limit:
                query += f" LIMIT {limit}"
            
            url = f"{self.instance_url}/services/data/v54.0/query"
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"q": query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            for result in data.get("records", []):
                # Remover atributos de Salesforce
                record_data = {k: v for k, v in result.items() if not k.startswith("attributes")}
                
                record = SyncRecord(
                    source_id=result.get("Id"),
                    source_type=f"salesforce_{sobject_type.lower()}",
                    data=record_data,
                    metadata={"salesforce_data": result}
                )
                records.append(record)
            
            self.logger.info(f"Leídos {len(records)} registros de Salesforce")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de Salesforce: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Crea registros en Salesforce"""
        import requests
        sobject_type = self.config.get("sobject_type", "Contact")
        results = []
        
        for record in records:
            url = f"{self.instance_url}/services/data/v54.0/sobjects/{sobject_type}/"
            
            try:
                response = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=record.data,
                    timeout=30
                )
                response.raise_for_status()
                
                result_data = response.json()
                record.target_id = result_data.get("id")
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error escribiendo registro {record.source_id}: {e}")
                results.append(record)
        
        return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros en Salesforce"""
        import requests
        sobject_type = self.config.get("sobject_type", "Contact")
        results = []
        
        for record in records:
            if not record.target_id:
                record.status = "failed"
                record.error_message = "target_id requerido para actualización"
                results.append(record)
                continue
            
            url = f"{self.instance_url}/services/data/v54.0/sobjects/{sobject_type}/{record.target_id}"
            
            try:
                response = requests.patch(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=record.data,
                    timeout=30
                )
                response.raise_for_status()
                
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error actualizando registro {record.target_id}: {e}")
                results.append(record)
        
        return results


class NetSuiteConnector(BaseConnector):
    """Conector para NetSuite ERP"""
    
    def connect(self) -> bool:
        """Conecta a NetSuite REST API usando Token-Based Authentication"""
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            
            account_id = self.config.get("account_id")
            consumer_key = self.config.get("consumer_key")
            consumer_secret = self.config.get("consumer_secret")
            token_id = self.config.get("token_id")
            token_secret = self.config.get("token_secret")
            sandbox = self.config.get("sandbox", False)
            
            if not all([account_id, consumer_key, consumer_secret, token_id, token_secret]):
                raise ValueError("NetSuite requiere account_id, consumer_key, consumer_secret, token_id, token_secret")
            
            self.account_id = account_id
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
            self.token_id = token_id
            self.token_secret = token_secret
            
            # Determinar base URL
            if sandbox:
                self.base_url = f"https://{account_id}.suitetalk.api.netsuite.com"
            else:
                self.base_url = f"https://{account_id}.suitetalk.api.netsuite.com"
            
            # Test connection
            url = f"{self.base_url}/services/rest/record/v1/metadata-catalog"
            response = requests.get(
                url,
                auth=HTTPBasicAuth(token_id, token_secret),
                headers={
                    "Content-Type": "application/json",
                    "Prefer": "transient"
                },
                timeout=10
            )
            response.raise_for_status()
            self.logger.info("Conexión a NetSuite establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a NetSuite: {e}")
            return False
    
    def disconnect(self) -> None:
        """No requiere desconexión para API REST"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de NetSuite"""
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            from datetime import datetime
            
            start_time = datetime.now()
            
            url = f"{self.base_url}/services/rest/record/v1/metadata-catalog"
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.token_id, self.token_secret),
                headers={
                    "Content-Type": "application/json",
                    "Prefer": "transient"
                },
                timeout=5
            )
            response.raise_for_status()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _get_auth(self):
        """Obtiene autenticación para requests"""
        from requests.auth import HTTPBasicAuth
        return HTTPBasicAuth(self.token_id, self.token_secret)
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers estándar para requests"""
        return {
            "Content-Type": "application/json",
            "Prefer": "transient"
        }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee registros de NetSuite usando SuiteQL o REST API"""
        import requests
        
        record_type = filters.get("record_type", "transaction") if filters else "transaction"
        query = filters.get("query") if filters else None
        
        records = []
        
        try:
            if query:
                # Usar SuiteQL para queries personalizadas
                url = f"{self.base_url}/services/rest/query/v1/suiteql"
                payload = {
                    "q": query
                }
                if limit:
                    payload["limit"] = limit
                
                response = requests.post(
                    url,
                    auth=self._get_auth(),
                    headers=self._get_headers(),
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("items", []):
                    record = SyncRecord(
                        source_id=str(item.get("id", "")),
                        source_type=f"netsuite_{record_type}",
                        data=item,
                        metadata={"netsuite_query": query}
                    )
                    records.append(record)
            else:
                # Usar REST API para buscar registros por tipo
                url = f"{self.base_url}/services/rest/record/v1/{record_type}"
                params = {}
                if limit:
                    params["limit"] = limit
                
                response = requests.get(
                    url,
                    auth=self._get_auth(),
                    headers=self._get_headers(),
                    params=params,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("items", []):
                    record = SyncRecord(
                        source_id=str(item.get("id", "")),
                        source_type=f"netsuite_{record_type}",
                        data=item,
                        metadata={"netsuite_type": record_type}
                    )
                    records.append(record)
            
            self.logger.info(f"Leídos {len(records)} registros de NetSuite")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de NetSuite: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Crea registros en NetSuite"""
        import requests
        
        results = []
        
        for record in records:
            record_type = record.data.get("record_type", "transaction")
            url = f"{self.base_url}/services/rest/record/v1/{record_type}"
            
            try:
                # Preparar payload para NetSuite
                payload = record.data.get("fields", record.data)
                
                response = requests.post(
                    url,
                    auth=self._get_auth(),
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                result_data = response.json()
                record.target_id = str(result_data.get("id", ""))
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error escribiendo registro {record.source_id}: {e}")
                results.append(record)
        
        return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros en NetSuite"""
        import requests
        
        results = []
        
        for record in records:
            if not record.target_id:
                record.status = "failed"
                record.error_message = "target_id requerido para actualización"
                results.append(record)
                continue
            
            record_type = record.data.get("record_type", "transaction")
            url = f"{self.base_url}/services/rest/record/v1/{record_type}/{record.target_id}"
            
            try:
                payload = record.data.get("fields", record.data)
                
                response = requests.patch(
                    url,
                    auth=self._get_auth(),
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                record.status = "synced"
                record.synced_at = datetime.now()
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error actualizando registro {record.target_id}: {e}")
                results.append(record)
        
        return results
    
    def get_financial_metrics(
        self,
        start_date: str,
        end_date: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extrae métricas financieras de NetSuite usando SuiteQL.
        
        Args:
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            metrics: Lista de métricas a extraer (revenue, expenses, etc.)
        
        Returns:
            Diccionario con métricas financieras
        """
        import requests
        
        if metrics is None:
            metrics = ["revenue", "expenses", "gross_profit", "net_income", "orders_count", "customers_count"]
        
        results = {}
        
        try:
            # Query para métricas financieras
            query = f"""
            SELECT 
                SUM(amount) as revenue,
                COUNT(DISTINCT transaction) as orders_count,
                COUNT(DISTINCT customer) as customers_count
            FROM transaction
            WHERE type IN ('SalesOrd', 'CustInvc', 'CustCred')
            AND trandate >= '{start_date}'
            AND trandate <= '{end_date}'
            AND status != 'Void'
            """
            
            url = f"{self.base_url}/services/rest/query/v1/suiteql"
            payload = {"q": query}
            
            response = requests.post(
                url,
                auth=self._get_auth(),
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("items"):
                item = data["items"][0]
                results = {
                    "revenue": float(item.get("revenue", 0) or 0),
                    "orders_count": int(item.get("orders_count", 0) or 0),
                    "customers_count": int(item.get("customers_count", 0) or 0),
                    "start_date": start_date,
                    "end_date": end_date
                }
            
            self.logger.info(f"Métricas financieras extraídas: {results}")
            return results
        except Exception as e:
            self.logger.error(f"Error extrayendo métricas financieras: {e}")
            return {}


class PipedriveConnector(BaseConnector):
    """Conector para Pipedrive CRM"""
    
    def connect(self) -> bool:
        """Conecta a Pipedrive API"""
        try:
            import requests
            api_token = self.config.get("api_token")
            company_domain = self.config.get("company_domain")
            
            if not api_token or not company_domain:
                raise ValueError("Pipedrive requiere api_token y company_domain")
            
            # Test connection
            url = f"https://{company_domain}.pipedrive.com/api/v1/users/me"
            response = requests.get(
                url,
                params={"api_token": api_token},
                timeout=10
            )
            response.raise_for_status()
            
            self.api_token = api_token
            self.company_domain = company_domain
            self.base_url = f"https://{company_domain}.pipedrive.com/api/v1"
            
            self.logger.info("Conexión a Pipedrive establecida")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a Pipedrive: {e}")
            return False
    
    def disconnect(self) -> None:
        """No requiere desconexión para API REST"""
        self.api_token = None
        self.company_domain = None
        self.base_url = None
    
    def health_check(self) -> Dict[str, Any]:
        """Health check de Pipedrive"""
        try:
            import requests
            if not hasattr(self, 'base_url') or not self.base_url:
                return {"status": "unhealthy", "error": "No conectado"}
            
            start_time = datetime.now()
            response = requests.get(
                f"{self.base_url}/users/me",
                params={"api_token": self.api_token},
                timeout=5
            )
            response.raise_for_status()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency_ms,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def read_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[SyncRecord]:
        """Lee personas/deals de Pipedrive"""
        import requests
        resource_type = filters.get("resource_type", "persons") if filters else "persons"
        
        records = []
        try:
            url = f"{self.base_url}/{resource_type}"
            params = {"api_token": self.api_token}
            
            if limit:
                params["limit"] = limit
            if filters and "since" in filters:
                params["since"] = filters["since"]
            
            response = requests.get(
                url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            items = data.get("data", [])
            for item in items:
                record = SyncRecord(
                    source_id=str(item.get("id", "")),
                    source_type=f"pipedrive_{resource_type}",
                    data=item,
                    metadata={"pipedrive_data": item}
                )
                records.append(record)
            
            self.logger.info(f"Leídos {len(records)} registros de Pipedrive")
            return records
        except Exception as e:
            self.logger.error(f"Error leyendo de Pipedrive: {e}")
            return []
    
    def write_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Crea registros en Pipedrive (Personas o Deals)"""
        import requests
        resource_type = self.config.get("resource_type", "persons")
        results = []
        
        for record in records:
            url = f"{self.base_url}/{resource_type}"
            
            try:
                response = requests.post(
                    url,
                    params={"api_token": self.api_token},
                    json=record.data,
                    timeout=30
                )
                response.raise_for_status()
                
                result_data = response.json()
                if result_data.get("success"):
                    data = result_data.get("data", {})
                    record.target_id = str(data.get("id", ""))
                    record.status = "synced"
                    record.synced_at = datetime.now()
                else:
                    record.status = "failed"
                    record.error_message = result_data.get("error", "Unknown error")
                
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error escribiendo registro {record.source_id}: {e}")
                results.append(record)
        
        return results
    
    def update_records(self, records: List[SyncRecord]) -> List[SyncRecord]:
        """Actualiza registros en Pipedrive"""
        import requests
        resource_type = self.config.get("resource_type", "persons")
        results = []
        
        for record in records:
            if not record.target_id:
                record.status = "failed"
                record.error_message = "target_id requerido para actualización"
                results.append(record)
                continue
            
            url = f"{self.base_url}/{resource_type}/{record.target_id}"
            
            try:
                response = requests.put(
                    url,
                    params={"api_token": self.api_token},
                    json=record.data,
                    timeout=30
                )
                response.raise_for_status()
                
                result_data = response.json()
                if result_data.get("success"):
                    record.status = "synced"
                    record.synced_at = datetime.now()
                else:
                    record.status = "failed"
                    record.error_message = result_data.get("error", "Unknown error")
                
                results.append(record)
            except Exception as e:
                record.status = "failed"
                record.error_message = str(e)
                self.logger.error(f"Error actualizando registro {record.target_id}: {e}")
                results.append(record)
        
        return results
    
    def create_deal(
        self,
        title: str,
        person_id: Optional[int] = None,
        org_id: Optional[int] = None,
        stage_id: Optional[int] = None,
        value: Optional[float] = None,
        currency: str = "USD",
        **kwargs
    ) -> Optional[str]:
        """Crea un deal en Pipedrive"""
        import requests
        
        deal_data = {
            "title": title,
            **kwargs
        }
        
        if person_id:
            deal_data["person_id"] = person_id
        if org_id:
            deal_data["org_id"] = org_id
        if stage_id:
            deal_data["stage_id"] = stage_id
        if value:
            deal_data["value"] = value
            deal_data["currency"] = currency
        
        try:
            url = f"{self.base_url}/deals"
            response = requests.post(
                url,
                params={"api_token": self.api_token},
                json=deal_data,
                timeout=30
            )
            response.raise_for_status()
            
            result_data = response.json()
            if result_data.get("success"):
                return str(result_data.get("data", {}).get("id", ""))
            return None
        except Exception as e:
            self.logger.error(f"Error creando deal en Pipedrive: {e}")
            return None
    
    def add_activity(
        self,
        subject: str,
        type: str,
        due_date: Optional[str] = None,
        person_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        **kwargs
    ) -> Optional[str]:
        """Agrega una actividad (tarea, llamada, email) en Pipedrive"""
        import requests
        
        activity_data = {
            "subject": subject,
            "type": type,
            **kwargs
        }
        
        if due_date:
            activity_data["due_date"] = due_date
        if person_id:
            activity_data["person_id"] = person_id
        if deal_id:
            activity_data["deal_id"] = deal_id
        
        try:
            url = f"{self.base_url}/activities"
            response = requests.post(
                url,
                params={"api_token": self.api_token},
                json=activity_data,
                timeout=30
            )
            response.raise_for_status()
            
            result_data = response.json()
            if result_data.get("success"):
                return str(result_data.get("data", {}).get("id", ""))
            return None
        except Exception as e:
            self.logger.error(f"Error agregando actividad en Pipedrive: {e}")
            return None


def create_connector(connector_type: str, config: Dict[str, Any]) -> BaseConnector:
    """
    Factory function para crear conectores según el tipo.
    
    Args:
        connector_type: Tipo de conector (hubspot, salesforce, pipedrive, etc.)
        config: Configuración específica del conector
    
    Returns:
        Instancia del conector apropiado
    
    Raises:
        ValueError: Si el tipo de conector no es soportado
    """
    connectors = {
        "hubspot": HubSpotConnector,
        "salesforce": SalesforceConnector,
        "pipedrive": PipedriveConnector,
        "quickbooks": QuickBooksConnector,
        "google_sheets": GoogleSheetsConnector,
        "database": DatabaseConnector,
        "postgres": DatabaseConnector,
        "mysql": DatabaseConnector,
        "netsuite": NetSuiteConnector,
    }
    
    connector_class = connectors.get(connector_type.lower())
    if not connector_class:
        raise ValueError(
            f"Tipo de conector no soportado: {connector_type}. "
            f"Tipos disponibles: {', '.join(connectors.keys())}"
        )
    
    return connector_class(config)

