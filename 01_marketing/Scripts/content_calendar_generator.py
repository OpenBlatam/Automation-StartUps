#!/usr/bin/env python3
"""
Content Calendar Generator
Automated content calendar creation tool
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ContentCalendarGenerator:
    """Generate content calendars with automated planning"""
    
    def __init__(self):
        self.content_pillars = []
        self.platforms = []
        self.posting_frequency = {}
        self.content_types = []
        
    def set_content_pillars(self, pillars: List[str]):
        """Set content pillars for the calendar"""
        self.content_pillars = pillars
        
    def set_platforms(self, platforms: List[str]):
        """Set platforms for content distribution"""
        self.platforms = platforms
        
    def set_posting_frequency(self, platform: str, frequency: Dict):
        """Set posting frequency for a platform"""
        self.posting_frequency[platform] = frequency
        
    def generate_monthly_calendar(self, year: int, month: int, 
                                  theme: str = None) -> Dict:
        """Generate a monthly content calendar"""
        calendar = {
            'year': year,
            'month': month,
            'theme': theme or f"Content Theme for {month}/{year}",
            'weeks': []
        }
        
        # Get first day of month
        first_day = datetime(year, month, 1)
        
        # Generate 4-5 weeks
        current_date = first_day
        week_num = 1
        
        while current_date.month == month and week_num <= 5:
            week = self._generate_week(current_date, week_num, month)
            calendar['weeks'].append(week)
            current_date += timedelta(days=7)
            week_num += 1
            
        return calendar
    
    def _generate_week(self, start_date: datetime, week_num: int, 
                      month: int) -> Dict:
        """Generate content for a week"""
        week = {
            'week_number': week_num,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'focus': f"Week {week_num} Focus",
            'days': []
        }
        
        current_date = start_date
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                    'Friday', 'Saturday', 'Sunday']
        
        for i in range(7):
            if current_date.month != month:
                break
                
            day_content = {
                'date': current_date.strftime('%Y-%m-%d'),
                'day_name': day_names[current_date.weekday()],
                'content_items': []
            }
            
            # Generate content for each platform
            for platform in self.platforms:
                if self._should_post(platform, current_date):
                    content_item = self._generate_content_item(
                        platform, current_date, week_num
                    )
                    day_content['content_items'].append(content_item)
            
            week['days'].append(day_content)
            current_date += timedelta(days=1)
            
        return week
    
    def _should_post(self, platform: str, date: datetime) -> bool:
        """Check if should post on this platform for this date"""
        if platform not in self.posting_frequency:
            return False
            
        freq = self.posting_frequency[platform]
        day_name = date.strftime('%A')
        
        # Check if platform posts on this day
        if 'days' in freq:
            return day_name in freq['days']
        
        # Check frequency (e.g., daily, weekly)
        if 'frequency' in freq:
            if freq['frequency'] == 'daily':
                return True
            elif freq['frequency'] == 'weekly':
                return date.weekday() == 0  # Monday
        
        return False
    
    def _generate_content_item(self, platform: str, date: datetime, 
                              week_num: int) -> Dict:
        """Generate a content item for a platform"""
        pillar = self._get_pillar_for_week(week_num)
        content_type = self._get_content_type(platform, date)
        
        return {
            'platform': platform,
            'type': content_type,
            'pillar': pillar,
            'topic': f"{pillar} - {content_type} for {platform}",
            'format': self._get_format(platform, content_type),
            'status': 'planned',
            'assigned_to': None,
            'notes': ''
        }
    
    def _get_pillar_for_week(self, week_num: int) -> str:
        """Get content pillar for the week"""
        if not self.content_pillars:
            return "General Content"
        return self.content_pillars[(week_num - 1) % len(self.content_pillars)]
    
    def _get_content_type(self, platform: str, date: datetime) -> str:
        """Get content type based on platform and day"""
        day_types = {
            0: 'Educational',  # Monday
            1: 'Case Study',   # Tuesday
            2: 'Tips',         # Wednesday
            3: 'Storytelling', # Thursday
            4: 'Roundup',      # Friday
            5: 'Inspirational', # Saturday
            6: 'Engagement'    # Sunday
        }
        return day_types.get(date.weekday(), 'General')
    
    def _get_format(self, platform: str, content_type: str) -> str:
        """Get content format for platform"""
        formats = {
            'Blog': 'Article',
            'LinkedIn': 'Post',
            'Twitter': 'Thread',
            'Instagram': 'Carousel',
            'Facebook': 'Post',
            'YouTube': 'Video'
        }
        return formats.get(platform, 'Post')
    
    def export_to_json(self, calendar: Dict, filename: str):
        """Export calendar to JSON file"""
        with open(filename, 'w') as f:
            json.dump(calendar, f, indent=2)
        print(f"Calendar exported to {filename}")
    
    def export_to_markdown(self, calendar: Dict, filename: str):
        """Export calendar to Markdown file"""
        md_content = f"# Content Calendar - {calendar['month']}/{calendar['year']}\n\n"
        md_content += f"**Theme:** {calendar['theme']}\n\n"
        
        for week in calendar['weeks']:
            md_content += f"## Week {week['week_number']}\n\n"
            md_content += f"**Focus:** {week['focus']}\n\n"
            
            for day in week['days']:
                md_content += f"### {day['day_name']}, {day['date']}\n\n"
                
                for item in day['content_items']:
                    md_content += f"- **{item['platform']}**: {item['topic']}\n"
                    md_content += f"  - Type: {item['type']}\n"
                    md_content += f"  - Format: {item['format']}\n"
                    md_content += f"  - Pillar: {item['pillar']}\n\n"
        
        with open(filename, 'w') as f:
            f.write(md_content)
        print(f"Calendar exported to {filename}")


def main():
    """Example usage"""
    generator = ContentCalendarGenerator()
    
    # Set content pillars
    generator.set_content_pillars([
        'Education',
        'Engagement',
        'Authority',
        'Conversion'
    ])
    
    # Set platforms
    generator.set_platforms([
        'Blog',
        'LinkedIn',
        'Twitter',
        'Instagram'
    ])
    
    # Set posting frequency
    generator.set_posting_frequency('Blog', {
        'frequency': 'weekly',
        'days': ['Monday']
    })
    generator.set_posting_frequency('LinkedIn', {
        'days': ['Monday', 'Wednesday', 'Friday']
    })
    generator.set_posting_frequency('Twitter', {
        'frequency': 'daily'
    })
    generator.set_posting_frequency('Instagram', {
        'days': ['Monday', 'Wednesday', 'Friday', 'Sunday']
    })
    
    # Generate calendar for current month
    now = datetime.now()
    calendar = generator.generate_monthly_calendar(
        now.year, now.month, "AI Marketing Mastery"
    )
    
    # Export
    generator.export_to_json(calendar, 'content_calendar.json')
    generator.export_to_markdown(calendar, 'content_calendar.md')
    
    print("Content calendar generated successfully!")


if __name__ == '__main__':
    main()

