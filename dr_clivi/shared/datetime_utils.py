"""
Date and Time Utilities
Common utilities for handling dates, times, and time zones
"""

import logging
from typing import Optional, List, Union
from datetime import datetime, timedelta, timezone
import pytz
from dateutil import parser


logger = logging.getLogger(__name__)


class DateTimeUtils:
    """Utility class for date and time operations"""
    
    # Common timezone for Mexico
    MEXICO_TZ = pytz.timezone('America/Mexico_City')
    UTC_TZ = pytz.UTC
    
    @classmethod
    def now_mexico(cls) -> datetime:
        """Get current time in Mexico timezone"""
        return datetime.now(cls.MEXICO_TZ)
    
    @classmethod
    def now_utc(cls) -> datetime:
        """Get current time in UTC"""
        return datetime.now(cls.UTC_TZ)
    
    @classmethod
    def to_mexico_time(cls, dt: datetime) -> datetime:
        """Convert datetime to Mexico timezone"""
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = cls.UTC_TZ.localize(dt)
        return dt.astimezone(cls.MEXICO_TZ)
    
    @classmethod
    def to_utc(cls, dt: datetime) -> datetime:
        """Convert datetime to UTC"""
        if dt.tzinfo is None:
            # Assume Mexico timezone if no timezone info
            dt = cls.MEXICO_TZ.localize(dt)
        return dt.astimezone(cls.UTC_TZ)
    
    @classmethod
    def parse_date_string(cls, date_str: str) -> Optional[datetime]:
        """Parse date string with flexible formats"""
        try:
            # Try to parse with dateutil (handles many formats)
            return parser.parse(date_str)
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse date string '{date_str}': {e}")
            return None
    
    @classmethod
    def format_date_mexico(cls, dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
        """Format datetime for Mexico display"""
        mexico_dt = cls.to_mexico_time(dt)
        return mexico_dt.strftime(format_str)
    
    @classmethod
    def format_date_friendly(cls, dt: datetime) -> str:
        """Format datetime in a user-friendly way"""
        mexico_dt = cls.to_mexico_time(dt)
        now = cls.now_mexico()
        
        # If today
        if mexico_dt.date() == now.date():
            return f"Hoy a las {mexico_dt.strftime('%H:%M')}"
        
        # If tomorrow
        tomorrow = now.date() + timedelta(days=1)
        if mexico_dt.date() == tomorrow:
            return f"Mañana a las {mexico_dt.strftime('%H:%M')}"
        
        # If within a week
        days_diff = (mexico_dt.date() - now.date()).days
        if 0 < days_diff <= 7:
            weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            weekday = weekdays[mexico_dt.weekday()]
            return f"{weekday} a las {mexico_dt.strftime('%H:%M')}"
        
        # If within this year
        if mexico_dt.year == now.year:
            return mexico_dt.strftime("%d de %B a las %H:%M")
        
        # Full date
        return mexico_dt.strftime("%d de %B %Y a las %H:%M")
    
    @classmethod
    def get_business_hours_today(cls) -> tuple[datetime, datetime]:
        """Get business hours for today (9 AM - 6 PM Mexico time)"""
        today = cls.now_mexico().date()
        start_time = cls.MEXICO_TZ.localize(
            datetime.combine(today, datetime.min.time().replace(hour=9))
        )
        end_time = cls.MEXICO_TZ.localize(
            datetime.combine(today, datetime.min.time().replace(hour=18))
        )
        return start_time, end_time
    
    @classmethod
    def is_business_hours(cls, dt: Optional[datetime] = None) -> bool:
        """Check if given time (or now) is within business hours"""
        if dt is None:
            dt = cls.now_mexico()
        else:
            dt = cls.to_mexico_time(dt)
        
        # Check if weekday (Monday = 0, Sunday = 6)
        if dt.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if within business hours
        start_time, end_time = cls.get_business_hours_today()
        return start_time <= dt <= end_time
    
    @classmethod
    def next_business_day(cls, dt: Optional[datetime] = None) -> datetime:
        """Get next business day"""
        if dt is None:
            dt = cls.now_mexico()
        else:
            dt = cls.to_mexico_time(dt)
        
        # Start from next day
        next_day = dt + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:  # Saturday or Sunday
            next_day += timedelta(days=1)
        
        # Set to start of business hours
        return cls.MEXICO_TZ.localize(
            datetime.combine(next_day.date(), datetime.min.time().replace(hour=9))
        )
    
    @classmethod
    def get_available_appointment_slots(cls, 
                                      start_date: Optional[datetime] = None,
                                      days_ahead: int = 14) -> List[datetime]:
        """Get available appointment slots for the next N days"""
        if start_date is None:
            start_date = cls.now_mexico()
        else:
            start_date = cls.to_mexico_time(start_date)
        
        slots = []
        current_date = start_date.date()
        end_date = current_date + timedelta(days=days_ahead)
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday to Friday
                # Add slots from 9 AM to 5 PM, every hour
                for hour in range(9, 17):
                    slot_datetime = cls.MEXICO_TZ.localize(
                        datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                    )
                    
                    # Only add future slots
                    if slot_datetime > start_date:
                        slots.append(slot_datetime)
            
            current_date += timedelta(days=1)
        
        return slots
    
    @classmethod
    def time_until_next_business_hours(cls) -> Optional[timedelta]:
        """Get time until next business hours"""
        now = cls.now_mexico()
        
        if cls.is_business_hours(now):
            return timedelta(0)  # Already in business hours
        
        # If it's the same day but before business hours
        start_time, _ = cls.get_business_hours_today()
        if now.time() < start_time.time() and now.weekday() < 5:
            return start_time - now
        
        # Otherwise, next business day
        next_business = cls.next_business_day(now)
        return next_business - now
