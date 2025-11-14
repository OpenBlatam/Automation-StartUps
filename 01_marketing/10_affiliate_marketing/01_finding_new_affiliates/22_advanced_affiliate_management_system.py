#!/usr/bin/env python3
"""
Advanced Affiliate Management System
===================================

This module provides comprehensive affiliate management capabilities including
onboarding, performance tracking, payment processing, and relationship management.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import hashlib
import uuid
import qrcode
from io import BytesIO
import base64
import requests
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AffiliateStatus(Enum):
    """Affiliate status types"""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    INACTIVE = "inactive"

class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CommissionType(Enum):
    """Commission types"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"
    BONUS = "bonus"

@dataclass
class Affiliate:
    """Affiliate data structure"""
    affiliate_id: str
    name: str
    email: str
    phone: str
    company: Optional[str]
    website: Optional[str]
    social_media: Dict[str, str]
    payment_info: Dict[str, Any]
    status: AffiliateStatus
    tier: str
    commission_rate: float
    commission_type: CommissionType
    total_earnings: float
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    created_at: datetime
    last_activity: datetime
    notes: List[str]

@dataclass
class Commission:
    """Commission data structure"""
    commission_id: str
    affiliate_id: str
    amount: float
    commission_type: CommissionType
    description: str
    status: PaymentStatus
    created_at: datetime
    paid_at: Optional[datetime]
    payment_method: str
    transaction_id: Optional[str]

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    affiliate_id: str
    period: str
    clicks: int
    conversions: int
    revenue: float
    commission_earned: float
    conversion_rate: float
    click_through_rate: float
    revenue_per_click: float
    commission_per_conversion: float

class AdvancedAffiliateManagementSystem:
    """
    Advanced Affiliate Management System
    """
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 smtp_username: str = None, smtp_password: str = None):
        self.affiliates = {}
        self.commissions = []
        self.performance_metrics = []
        self.payment_methods = {}
        self.tiers = {}
        self.notifications = []
        
        # Email configuration
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        
        # Initialize default tiers
        self._initialize_default_tiers()
        
        # Initialize payment methods
        self._initialize_payment_methods()
    
    def _initialize_default_tiers(self):
        """
        Initialize default affiliate tiers
        """
        self.tiers = {
            'bronze': {
                'name': 'Bronze',
                'commission_rate': 0.05,  # 5%
                'min_earnings': 0,
                'max_earnings': 1000,
                'benefits': ['Basic support', 'Standard reporting']
            },
            'silver': {
                'name': 'Silver',
                'commission_rate': 0.07,  # 7%
                'min_earnings': 1000,
                'max_earnings': 5000,
                'benefits': ['Priority support', 'Advanced reporting', 'Dedicated manager']
            },
            'gold': {
                'name': 'Gold',
                'commission_rate': 0.10,  # 10%
                'min_earnings': 5000,
                'max_earnings': 20000,
                'benefits': ['VIP support', 'Custom reporting', 'Dedicated manager', 'Co-marketing opportunities']
            },
            'platinum': {
                'name': 'Platinum',
                'commission_rate': 0.15,  # 15%
                'min_earnings': 20000,
                'max_earnings': float('inf'),
                'benefits': ['Executive support', 'Custom reporting', 'Dedicated manager', 'Co-marketing opportunities', 'Exclusive events']
            }
        }
    
    def _initialize_payment_methods(self):
        """
        Initialize payment methods
        """
        self.payment_methods = {
            'paypal': {
                'name': 'PayPal',
                'enabled': True,
                'min_amount': 10.0,
                'processing_fee': 0.029
            },
            'bank_transfer': {
                'name': 'Bank Transfer',
                'enabled': True,
                'min_amount': 50.0,
                'processing_fee': 0.0
            },
            'crypto': {
                'name': 'Cryptocurrency',
                'enabled': True,
                'min_amount': 25.0,
                'processing_fee': 0.01
            }
        }
    
    def register_affiliate(self, name: str, email: str, phone: str, 
                          company: str = None, website: str = None, 
                          social_media: Dict = None) -> Affiliate:
        """
        Register new affiliate
        """
        # Generate affiliate ID
        affiliate_id = f"aff_{uuid.uuid4().hex[:8]}"
        
        # Create affiliate
        affiliate = Affiliate(
            affiliate_id=affiliate_id,
            name=name,
            email=email,
            phone=phone,
            company=company,
            website=website,
            social_media=social_media or {},
            payment_info={},
            status=AffiliateStatus.PENDING,
            tier='bronze',
            commission_rate=self.tiers['bronze']['commission_rate'],
            commission_type=CommissionType.PERCENTAGE,
            total_earnings=0.0,
            total_clicks=0,
            total_conversions=0,
            conversion_rate=0.0,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            notes=[]
        )
        
        self.affiliates[affiliate_id] = affiliate
        
        # Send welcome email
        self._send_welcome_email(affiliate)
        
        # Add notification
        self._add_notification(
            f"New affiliate registered: {name} ({email})",
            "affiliate_registration",
            affiliate_id
        )
        
        logger.info(f"Registered new affiliate: {name} ({affiliate_id})")
        return affiliate
    
    def _send_welcome_email(self, affiliate: Affiliate):
        """
        Send welcome email to new affiliate
        """
        if not self.smtp_server:
            logger.warning("SMTP not configured, skipping welcome email")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = affiliate.email
            msg['Subject'] = "Welcome to Our Affiliate Program!"
            
            # Create email body
            body = f"""
            Dear {affiliate.name},
            
            Welcome to our affiliate program! We're excited to have you on board.
            
            Your affiliate ID: {affiliate.affiliate_id}
            Your tier: {affiliate.tier.title()}
            Commission rate: {affiliate.commission_rate:.1%}
            
            Next steps:
            1. Complete your profile setup
            2. Add your payment information
            3. Access your affiliate dashboard
            4. Start promoting our products!
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            The Affiliate Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Welcome email sent to {affiliate.email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
    
    def _add_notification(self, message: str, notification_type: str, 
                         affiliate_id: str = None):
        """
        Add notification
        """
        notification = {
            'id': f"notif_{uuid.uuid4().hex[:8]}",
            'message': message,
            'type': notification_type,
            'affiliate_id': affiliate_id,
            'timestamp': datetime.now(),
            'read': False
        }
        
        self.notifications.append(notification)
    
    def approve_affiliate(self, affiliate_id: str, approver: str = "admin") -> bool:
        """
        Approve affiliate
        """
        if affiliate_id not in self.affiliates:
            logger.error(f"Affiliate {affiliate_id} not found")
            return False
        
        affiliate = self.affiliates[affiliate_id]
        
        if affiliate.status != AffiliateStatus.PENDING:
            logger.error(f"Affiliate {affiliate_id} is not pending approval")
            return False
        
        # Update status
        affiliate.status = AffiliateStatus.APPROVED
        affiliate.last_activity = datetime.now()
        affiliate.notes.append(f"Approved by {approver} on {datetime.now()}")
        
        # Send approval email
        self._send_approval_email(affiliate)
        
        # Add notification
        self._add_notification(
            f"Affiliate {affiliate.name} approved by {approver}",
            "affiliate_approval",
            affiliate_id
        )
        
        logger.info(f"Approved affiliate: {affiliate.name} ({affiliate_id})")
        return True
    
    def _send_approval_email(self, affiliate: Affiliate):
        """
        Send approval email to affiliate
        """
        if not self.smtp_server:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = affiliate.email
            msg['Subject'] = "Your Affiliate Application Has Been Approved!"
            
            body = f"""
            Dear {affiliate.name},
            
            Great news! Your affiliate application has been approved.
            
            You can now:
            1. Access your affiliate dashboard
            2. Generate your affiliate links
            3. Start earning commissions
            4. Track your performance
            
            Login to your dashboard to get started.
            
            Best regards,
            The Affiliate Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send approval email: {str(e)}")
    
    def update_affiliate_tier(self, affiliate_id: str) -> bool:
        """
        Update affiliate tier based on performance
        """
        if affiliate_id not in self.affiliates:
            logger.error(f"Affiliate {affiliate_id} not found")
            return False
        
        affiliate = self.affiliates[affiliate_id]
        
        # Determine new tier based on total earnings
        new_tier = 'bronze'
        for tier_name, tier_info in self.tiers.items():
            if affiliate.total_earnings >= tier_info['min_earnings']:
                new_tier = tier_name
        
        if new_tier != affiliate.tier:
            old_tier = affiliate.tier
            affiliate.tier = new_tier
            affiliate.commission_rate = self.tiers[new_tier]['commission_rate']
            affiliate.notes.append(f"Tier updated from {old_tier} to {new_tier} on {datetime.now()}")
            
            # Send tier update email
            self._send_tier_update_email(affiliate, old_tier, new_tier)
            
            logger.info(f"Updated {affiliate.name} from {old_tier} to {new_tier} tier")
            return True
        
        return False
    
    def _send_tier_update_email(self, affiliate: Affiliate, old_tier: str, new_tier: str):
        """
        Send tier update email
        """
        if not self.smtp_server:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = affiliate.email
            msg['Subject'] = f"Congratulations! You've Been Promoted to {new_tier.title()} Tier!"
            
            new_tier_info = self.tiers[new_tier]
            
            body = f"""
            Dear {affiliate.name},
            
            Congratulations! You've been promoted to {new_tier.title()} tier!
            
            New benefits:
            - Commission rate: {new_tier_info['commission_rate']:.1%}
            - Benefits: {', '.join(new_tier_info['benefits'])}
            
            Keep up the great work!
            
            Best regards,
            The Affiliate Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send tier update email: {str(e)}")
    
    def add_performance_metrics(self, affiliate_id: str, period: str, 
                               clicks: int, conversions: int, revenue: float):
        """
        Add performance metrics for affiliate
        """
        if affiliate_id not in self.affiliates:
            logger.error(f"Affiliate {affiliate_id} not found")
            return
        
        affiliate = self.affiliates[affiliate_id]
        
        # Calculate metrics
        conversion_rate = conversions / clicks if clicks > 0 else 0
        click_through_rate = clicks / 1000  # Assuming 1000 impressions
        revenue_per_click = revenue / clicks if clicks > 0 else 0
        commission_earned = revenue * affiliate.commission_rate
        commission_per_conversion = commission_earned / conversions if conversions > 0 else 0
        
        # Create performance metrics
        metrics = PerformanceMetrics(
            affiliate_id=affiliate_id,
            period=period,
            clicks=clicks,
            conversions=conversions,
            revenue=revenue,
            commission_earned=commission_earned,
            conversion_rate=conversion_rate,
            click_through_rate=click_through_rate,
            revenue_per_click=revenue_per_click,
            commission_per_conversion=commission_per_conversion
        )
        
        self.performance_metrics.append(metrics)
        
        # Update affiliate totals
        affiliate.total_clicks += clicks
        affiliate.total_conversions += conversions
        affiliate.total_earnings += commission_earned
        affiliate.conversion_rate = affiliate.total_conversions / affiliate.total_clicks if affiliate.total_clicks > 0 else 0
        affiliate.last_activity = datetime.now()
        
        # Update tier if necessary
        self.update_affiliate_tier(affiliate_id)
        
        # Create commission record
        self._create_commission_record(affiliate_id, commission_earned, f"Commission for {period}")
        
        logger.info(f"Added performance metrics for {affiliate_id}: {clicks} clicks, {conversions} conversions, ${revenue:.2f} revenue")
    
    def _create_commission_record(self, affiliate_id: str, amount: float, description: str):
        """
        Create commission record
        """
        commission = Commission(
            commission_id=f"comm_{uuid.uuid4().hex[:8]}",
            affiliate_id=affiliate_id,
            amount=amount,
            commission_type=CommissionType.PERCENTAGE,
            description=description,
            status=PaymentStatus.PENDING,
            created_at=datetime.now(),
            paid_at=None,
            payment_method="",
            transaction_id=None
        )
        
        self.commissions.append(commission)
    
    def process_payment(self, commission_id: str, payment_method: str) -> bool:
        """
        Process commission payment
        """
        commission = next((c for c in self.commissions if c.commission_id == commission_id), None)
        if not commission:
            logger.error(f"Commission {commission_id} not found")
            return False
        
        if commission.status != PaymentStatus.PENDING:
            logger.error(f"Commission {commission_id} is not pending")
            return False
        
        # Check minimum amount
        payment_method_info = self.payment_methods.get(payment_method)
        if not payment_method_info:
            logger.error(f"Payment method {payment_method} not found")
            return False
        
        if commission.amount < payment_method_info['min_amount']:
            logger.error(f"Commission amount ${commission.amount:.2f} is below minimum ${payment_method_info['min_amount']:.2f}")
            return False
        
        # Process payment (simplified)
        try:
            # Update commission status
            commission.status = PaymentStatus.PROCESSING
            commission.payment_method = payment_method
            
            # Simulate payment processing
            await asyncio.sleep(1)  # Simulate processing time
            
            # Update status to completed
            commission.status = PaymentStatus.COMPLETED
            commission.paid_at = datetime.now()
            commission.transaction_id = f"txn_{uuid.uuid4().hex[:8]}"
            
            # Send payment notification
            self._send_payment_notification(commission)
            
            logger.info(f"Processed payment for commission {commission_id}: ${commission.amount:.2f}")
            return True
            
        except Exception as e:
            commission.status = PaymentStatus.FAILED
            logger.error(f"Failed to process payment: {str(e)}")
            return False
    
    def _send_payment_notification(self, commission: Commission):
        """
        Send payment notification
        """
        if not self.smtp_server:
            return
        
        affiliate = self.affiliates.get(commission.affiliate_id)
        if not affiliate:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = affiliate.email
            msg['Subject'] = f"Payment Processed - ${commission.amount:.2f}"
            
            body = f"""
            Dear {affiliate.name},
            
            Your commission payment has been processed.
            
            Amount: ${commission.amount:.2f}
            Payment method: {commission.payment_method}
            Transaction ID: {commission.transaction_id}
            Date: {commission.paid_at}
            
            Thank you for your continued partnership!
            
            Best regards,
            The Affiliate Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send payment notification: {str(e)}")
    
    def generate_affiliate_report(self, affiliate_id: str, period: str = "monthly") -> Dict:
        """
        Generate affiliate performance report
        """
        if affiliate_id not in self.affiliates:
            return {}
        
        affiliate = self.affiliates[affiliate_id]
        
        # Get performance metrics for period
        period_metrics = [m for m in self.performance_metrics 
                         if m.affiliate_id == affiliate_id and m.period == period]
        
        # Calculate totals
        total_clicks = sum(m.clicks for m in period_metrics)
        total_conversions = sum(m.conversions for m in period_metrics)
        total_revenue = sum(m.revenue for m in period_metrics)
        total_commission = sum(m.commission_earned for m in period_metrics)
        
        # Calculate averages
        avg_conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0
        avg_revenue_per_click = total_revenue / total_clicks if total_clicks > 0 else 0
        
        # Get commission history
        commission_history = [c for c in self.commissions if c.affiliate_id == affiliate_id]
        
        return {
            'affiliate_id': affiliate_id,
            'affiliate_name': affiliate.name,
            'period': period,
            'tier': affiliate.tier,
            'commission_rate': affiliate.commission_rate,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'total_commission': total_commission,
            'conversion_rate': avg_conversion_rate,
            'revenue_per_click': avg_revenue_per_click,
            'commission_history': [asdict(c) for c in commission_history],
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_affiliate_qr_code(self, affiliate_id: str) -> str:
        """
        Generate QR code for affiliate
        """
        if affiliate_id not in self.affiliates:
            return ""
        
        affiliate = self.affiliates[affiliate_id]
        
        # Create affiliate link
        affiliate_link = f"https://example.com/affiliate/{affiliate_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(affiliate_link)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def get_affiliate_dashboard_data(self, affiliate_id: str) -> Dict:
        """
        Get affiliate dashboard data
        """
        if affiliate_id not in self.affiliates:
            return {}
        
        affiliate = self.affiliates[affiliate_id]
        
        # Get recent performance
        recent_metrics = [m for m in self.performance_metrics 
                         if m.affiliate_id == affiliate_id][-10:]  # Last 10 records
        
        # Get pending commissions
        pending_commissions = [c for c in self.commissions 
                             if c.affiliate_id == affiliate_id and c.status == PaymentStatus.PENDING]
        
        # Get recent notifications
        recent_notifications = [n for n in self.notifications 
                              if n['affiliate_id'] == affiliate_id][-5:]  # Last 5 notifications
        
        return {
            'affiliate': asdict(affiliate),
            'recent_metrics': [asdict(m) for m in recent_metrics],
            'pending_commissions': [asdict(c) for c in pending_commissions],
            'recent_notifications': recent_notifications,
            'qr_code': self.generate_affiliate_qr_code(affiliate_id),
            'tier_info': self.tiers[affiliate.tier]
        }
    
    def get_admin_dashboard_data(self) -> Dict:
        """
        Get admin dashboard data
        """
        # Calculate overall statistics
        total_affiliates = len(self.affiliates)
        active_affiliates = len([a for a in self.affiliates.values() if a.status == AffiliateStatus.ACTIVE])
        pending_approvals = len([a for a in self.affiliates.values() if a.status == AffiliateStatus.PENDING])
        
        total_commissions = sum(c.amount for c in self.commissions if c.status == PaymentStatus.COMPLETED)
        pending_payments = sum(c.amount for c in self.commissions if c.status == PaymentStatus.PENDING)
        
        # Get tier distribution
        tier_distribution = {}
        for affiliate in self.affiliates.values():
            tier = affiliate.tier
            if tier not in tier_distribution:
                tier_distribution[tier] = 0
            tier_distribution[tier] += 1
        
        # Get top performers
        top_performers = sorted(
            self.affiliates.values(),
            key=lambda a: a.total_earnings,
            reverse=True
        )[:10]
        
        return {
            'total_affiliates': total_affiliates,
            'active_affiliates': active_affiliates,
            'pending_approvals': pending_approvals,
            'total_commissions': total_commissions,
            'pending_payments': pending_payments,
            'tier_distribution': tier_distribution,
            'top_performers': [asdict(a) for a in top_performers],
            'recent_notifications': self.notifications[-10:],
            'generated_at': datetime.now().isoformat()
        }
    
    def export_affiliate_data(self, format: str = 'json') -> str:
        """
        Export affiliate data
        """
        data = {
            'affiliates': [asdict(affiliate) for affiliate in self.affiliates.values()],
            'commissions': [asdict(commission) for commission in self.commissions],
            'performance_metrics': [asdict(metric) for metric in self.performance_metrics],
            'tiers': self.tiers,
            'payment_methods': self.payment_methods
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Export affiliates as CSV
            df = pd.DataFrame([asdict(affiliate) for affiliate in self.affiliates.values()])
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
async def main():
    """
    Example usage of Advanced Affiliate Management System
    """
    # Initialize system
    system = AdvancedAffiliateManagementSystem(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="your-email@gmail.com",
        smtp_password="your-password"
    )
    
    # Register affiliates
    affiliate1 = system.register_affiliate(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        company="Marketing Agency",
        website="https://example.com",
        social_media={"twitter": "@johndoe", "linkedin": "john-doe"}
    )
    
    affiliate2 = system.register_affiliate(
        name="Jane Smith",
        email="jane@example.com",
        phone="+1234567891",
        company="Content Creator",
        website="https://janesmith.com",
        social_media={"instagram": "@janesmith", "youtube": "Jane Smith"}
    )
    
    # Approve affiliates
    system.approve_affiliate(affiliate1.affiliate_id)
    system.approve_affiliate(affiliate2.affiliate_id)
    
    # Add performance metrics
    system.add_performance_metrics(affiliate1.affiliate_id, "2024-01", 1000, 50, 5000)
    system.add_performance_metrics(affiliate2.affiliate_id, "2024-01", 800, 40, 4000)
    
    # Process payments
    pending_commissions = [c for c in system.commissions if c.status == PaymentStatus.PENDING]
    for commission in pending_commissions:
        await system.process_payment(commission.commission_id, "paypal")
    
    # Generate reports
    report1 = system.generate_affiliate_report(affiliate1.affiliate_id)
    report2 = system.generate_affiliate_report(affiliate2.affiliate_id)
    
    print(f"Affiliate 1 report: {report1}")
    print(f"Affiliate 2 report: {report2}")
    
    # Get dashboard data
    dashboard_data = system.get_admin_dashboard_data()
    print(f"Admin dashboard: {dashboard_data}")

if __name__ == "__main__":
    asyncio.run(main())


