#!/usr/bin/env python3
"""
Competitive Pricing Analysis System Startup Script
==================================================

This script provides an easy way to start the competitive pricing analysis system.
It handles initialization, configuration validation, and system startup.

Usage:
    python start_pricing_system.py [options]

Options:
    --mode [api|analyzer|both]  : Choose what to run (default: both)
    --port PORT                 : API server port (default: 8080)
    --config CONFIG_FILE        : Configuration file path (default: pricing_config.yaml)
    --sample-data               : Load sample data for testing
    --help                      : Show this help message
"""

import argparse
import sys
import os
import yaml
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pricing_system_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'requests', 'beautifulsoup4',
        'aiohttp', 'yaml', 'openpyxl', 'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install them using: pip install -r requirements_pricing.txt")
        return False
    
    logger.info("All required dependencies are installed")
    return True

def validate_config(config_file):
    """Validate configuration file"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['data_sources', 'products', 'competitors']
        for section in required_sections:
            if section not in config:
                logger.warning(f"Missing configuration section: {section}")
        
        # Check database path
        if 'database_path' not in config:
            config['database_path'] = 'pricing_analysis.db'
            logger.info("Using default database path: pricing_analysis.db")
        
        logger.info("Configuration file is valid")
        return True
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_file}")
        return False
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file: {e}")
        return False
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        return False

def load_sample_data():
    """Load sample data for testing"""
    try:
        from competitive_pricing_analyzer import CompetitivePricingAnalyzer, PricingData, DataSource
        import pandas as pd
        
        logger.info("Loading sample data...")
        
        # Initialize analyzer
        analyzer = CompetitivePricingAnalyzer()
        
        # Read sample data
        df = pd.read_csv('sample_pricing_data.csv')
        
        # Convert to PricingData objects
        pricing_data_list = []
        for _, row in df.iterrows():
            pricing_data = PricingData(
                product_id=row['product_id'],
                product_name=row['product_name'],
                competitor=row['competitor'],
                price=float(row['price']),
                currency=row['currency'],
                date_collected=datetime.now(),
                source=DataSource.CSV_IMPORT,
                additional_data={'sample_data': True}
            )
            pricing_data_list.append(pricing_data)
        
        # Store data
        analyzer._store_pricing_data(pricing_data_list)
        
        logger.info(f"Loaded {len(pricing_data_list)} sample data points")
        return True
        
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        return False

def run_analyzer():
    """Run the competitive pricing analyzer"""
    try:
        from competitive_pricing_analyzer import CompetitivePricingAnalyzer
        
        logger.info("Starting Competitive Pricing Analyzer...")
        
        # Initialize analyzer
        analyzer = CompetitivePricingAnalyzer()
        
        # Run analysis
        logger.info("Collecting pricing data...")
        asyncio.run(analyzer.collect_pricing_data())
        
        logger.info("Analyzing pricing differences...")
        insights = analyzer.analyze_pricing_differences()
        
        logger.info("Generating report...")
        report = analyzer.generate_pricing_report()
        
        # Export report
        filename = analyzer.export_to_excel()
        
        logger.info(f"Analysis complete! Report exported to {filename}")
        logger.info(f"Generated {len(insights)} insights")
        
        # Print summary
        print("\n" + "="*50)
        print("COMPETITIVE PRICING ANALYSIS SUMMARY")
        print("="*50)
        print(f"Products analyzed: {report['summary_statistics'].get('total_products', 0)}")
        print(f"Competitors tracked: {report['summary_statistics'].get('total_competitors', 0)}")
        print(f"Data points collected: {report['summary_statistics'].get('total_data_points', 0)}")
        print(f"Average price: ${report['summary_statistics'].get('average_price', 0):.2f}")
        
        print("\nTOP INSIGHTS:")
        for i, insight in enumerate(insights[:5], 1):
            print(f"{i}. {insight.description}")
            print(f"   Recommendation: {insight.recommendation}")
            print(f"   Impact Score: {insight.impact_score:.2f}")
            print()
        
        return True
        
    except Exception as e:
        logger.error(f"Error running analyzer: {e}")
        return False

def run_api_server(port=8080):
    """Run the API server"""
    try:
        from pricing_api_server import app
        
        logger.info(f"Starting API server on port {port}...")
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error running API server: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Start the Competitive Pricing Analysis System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_pricing_system.py                    # Run both analyzer and API server
  python start_pricing_system.py --mode api         # Run only API server
  python start_pricing_system.py --mode analyzer    # Run only analyzer
  python start_pricing_system.py --sample-data      # Load sample data and run
  python start_pricing_system.py --port 9000        # Run API server on port 9000
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['api', 'analyzer', 'both'],
        default='both',
        help='Choose what to run (default: both)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='API server port (default: 8080)'
    )
    
    parser.add_argument(
        '--config',
        default='pricing_config.yaml',
        help='Configuration file path (default: pricing_config.yaml)'
    )
    
    parser.add_argument(
        '--sample-data',
        action='store_true',
        help='Load sample data for testing'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("="*60)
    print("🏆 COMPETITIVE PRICING ANALYSIS SYSTEM")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {args.mode}")
    print(f"Config: {args.config}")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Validate configuration
    if not validate_config(args.config):
        logger.warning("Configuration validation failed, but continuing...")
    
    # Load sample data if requested
    if args.sample_data:
        if not load_sample_data():
            logger.error("Failed to load sample data")
            sys.exit(1)
    
    # Run based on mode
    success = True
    
    if args.mode in ['analyzer', 'both']:
        if not run_analyzer():
            success = False
            if args.mode == 'analyzer':
                sys.exit(1)
    
    if args.mode in ['api', 'both']:
        if not run_api_server(args.port):
            success = False
            if args.mode == 'api':
                sys.exit(1)
    
    if success:
        logger.info("System started successfully!")
        if args.mode in ['api', 'both']:
            print(f"\n🌐 Dashboard available at: http://localhost:{args.port}")
            print("📊 API documentation available at: http://localhost:{}/api/docs".format(args.port))
    else:
        logger.error("System startup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()






