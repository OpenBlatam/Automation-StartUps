#!/usr/bin/env python3
"""
Script helper para gestionar carritos abandonados.
Útil para integrar con aplicaciones web y registrar carritos.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql


class AbandonedCartHelper:
    """Helper para gestionar carritos abandonados."""
    
    def __init__(self, db_conn_string: Optional[str] = None):
        """
        Inicializa el helper.
        
        Args:
            db_conn_string: Connection string de PostgreSQL. 
                           Si no se proporciona, usa variables de entorno.
        """
        if db_conn_string:
            self.conn_string = db_conn_string
        else:
            self.conn_string = os.getenv(
                "POSTGRES_CONN_STRING",
                "postgresql://user:password@localhost:5432/dbname"
            )
    
    def register_cart(
        self,
        cart_id: str,
        customer_email: str,
        items: list,
        total_amount: float,
        customer_name: Optional[str] = None,
        currency: str = "USD",
        metadata: Optional[Dict[str, Any]] = None,
        cart_link: Optional[str] = None
    ) -> int:
        """
        Registra un carrito abandonado.
        
        Args:
            cart_id: ID único del carrito
            customer_email: Email del cliente
            items: Lista de items en el carrito
            total_amount: Monto total del carrito
            customer_name: Nombre del cliente (opcional)
            currency: Moneda (default: USD)
            metadata: Metadata adicional (opcional)
            cart_link: Link para completar la compra (opcional)
            
        Returns:
            ID del carrito registrado
        """
        conn = psycopg2.connect(self.conn_string)
        try:
            with conn.cursor() as cur:
                # Preparar metadata
                cart_metadata = metadata or {}
                if cart_link:
                    cart_metadata["cart_link"] = cart_link
                
                # Preparar items en formato JSONB
                items_json = json.dumps({
                    "items": items,
                    "count": len(items)
                })
                
                cur.execute("""
                    SELECT register_abandoned_cart(
                        %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb
                    )
                """, (
                    cart_id,
                    customer_email,
                    customer_name,
                    items_json,
                    total_amount,
                    currency,
                    json.dumps(cart_metadata) if cart_metadata else None
                ))
                
                result = cur.fetchone()[0]
                conn.commit()
                return result
                
        finally:
            conn.close()
    
    def mark_recovered(self, cart_id: str) -> bool:
        """
        Marca un carrito como recuperado (compró).
        
        Args:
            cart_id: ID del carrito
            
        Returns:
            True si se actualizó, False si no se encontró
        """
        conn = psycopg2.connect(self.conn_string)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT mark_cart_recovered(%s)", (cart_id,))
                result = cur.fetchone()[0]
                conn.commit()
                return result
        finally:
            conn.close()
    
    def validate_discount_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Valida un código de descuento.
        
        Args:
            code: Código de descuento
            
        Returns:
            Dict con información del código o None si no es válido
        """
        conn = psycopg2.connect(self.conn_string)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM validate_discount_code(%s)", (code,))
                result = cur.fetchone()
                
                if result and result['is_valid']:
                    return dict(result)
                return None
        finally:
            conn.close()
    
    def use_discount_code(self, code: str) -> bool:
        """
        Marca un código de descuento como usado.
        
        Args:
            code: Código de descuento
            
        Returns:
            True si se marcó como usado, False si no es válido
        """
        conn = psycopg2.connect(self.conn_string)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT mark_discount_code_used(%s)", (code,))
                result = cur.fetchone()[0]
                conn.commit()
                return result
        finally:
            conn.close()
    
    def get_cart_status(self, cart_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado de un carrito.
        
        Args:
            cart_id: ID del carrito
            
        Returns:
            Dict con información del carrito o None
        """
        conn = psycopg2.connect(self.conn_string)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id, cart_id, customer_email, customer_name,
                        items, total_amount, currency, 
                        created_at, reminder_sent_at, discount_sent_at,
                        discount_code, status, conversion_status
                    FROM abandoned_carts
                    WHERE cart_id = %s
                """, (cart_id,))
                
                result = cur.fetchone()
                if result:
                    return dict(result)
                return None
        finally:
            conn.close()


def main():
    """CLI para el helper."""
    parser = argparse.ArgumentParser(
        description="Helper para gestionar carritos abandonados"
    )
    parser.add_argument(
        "--db-conn",
        default=os.getenv("POSTGRES_CONN_STRING"),
        help="Connection string de PostgreSQL"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Comando register
    register_parser = subparsers.add_parser("register", help="Registrar un carrito abandonado")
    register_parser.add_argument("--cart-id", required=True, help="ID del carrito")
    register_parser.add_argument("--email", required=True, help="Email del cliente")
    register_parser.add_argument("--items", required=True, help="Items en formato JSON")
    register_parser.add_argument("--total", type=float, required=True, help="Total del carrito")
    register_parser.add_argument("--name", help="Nombre del cliente")
    register_parser.add_argument("--currency", default="USD", help="Moneda")
    register_parser.add_argument("--cart-link", help="Link para completar compra")
    
    # Comando recover
    recover_parser = subparsers.add_parser("recover", help="Marcar carrito como recuperado")
    recover_parser.add_argument("--cart-id", required=True, help="ID del carrito")
    
    # Comando validate
    validate_parser = subparsers.add_parser("validate", help="Validar código de descuento")
    validate_parser.add_argument("--code", required=True, help="Código de descuento")
    
    # Comando use-code
    use_parser = subparsers.add_parser("use-code", help="Marcar código como usado")
    use_parser.add_argument("--code", required=True, help="Código de descuento")
    
    # Comando status
    status_parser = subparsers.add_parser("status", help="Obtener estado de un carrito")
    status_parser.add_argument("--cart-id", required=True, help="ID del carrito")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    helper = AbandonedCartHelper(args.db_conn)
    
    if args.command == "register":
        try:
            items = json.loads(args.items)
        except json.JSONDecodeError:
            print("Error: items debe ser un JSON válido", file=sys.stderr)
            sys.exit(1)
        
        cart_id = helper.register_cart(
            cart_id=args.cart_id,
            customer_email=args.email,
            items=items,
            total_amount=args.total,
            customer_name=args.name,
            currency=args.currency,
            cart_link=args.cart_link
        )
        print(f"Carrito registrado con ID: {cart_id}")
    
    elif args.command == "recover":
        result = helper.mark_recovered(args.cart_id)
        if result:
            print(f"Carrito {args.cart_id} marcado como recuperado")
        else:
            print(f"Carrito {args.cart_id} no encontrado o ya recuperado")
            sys.exit(1)
    
    elif args.command == "validate":
        result = helper.validate_discount_code(args.code)
        if result:
            print(f"Código válido: {args.code}")
            print(f"Descuento: {result['discount_percentage']}%")
            print(f"Cart ID: {result['cart_id']}")
            if result['expires_at']:
                print(f"Expira: {result['expires_at']}")
        else:
            print(f"Código inválido o expirado: {args.code}")
            sys.exit(1)
    
    elif args.command == "use-code":
        result = helper.use_discount_code(args.code)
        if result:
            print(f"Código {args.code} marcado como usado")
        else:
            print(f"Código {args.code} no válido o ya usado")
            sys.exit(1)
    
    elif args.command == "status":
        result = helper.get_cart_status(args.cart_id)
        if result:
            print(json.dumps(dict(result), indent=2, default=str))
        else:
            print(f"Carrito {args.cart_id} no encontrado")
            sys.exit(1)


if __name__ == "__main__":
    main()



















