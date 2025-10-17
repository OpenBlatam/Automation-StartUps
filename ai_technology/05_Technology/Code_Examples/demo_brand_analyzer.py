#!/usr/bin/env python3
"""
Demo script for TruthGPT Brand Analyzer
Shows how to use the enhanced brand analysis system.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path

# Add the brandkit module to the path
sys.path.append(str(Path(__file__).parent / "TruthGPT" / "brandkit"))

from brand_analyzer import BrandAnalyzerAPI, BrandAnalyzerArgs, BrandTrainer, BrandDataset
from torch.utils.data import DataLoader
import torch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_website_data():
    """Create sample website data for demonstration."""
    return {
        'colors': [
            [255, 0, 0],      # Red primary
            [0, 255, 0],      # Green secondary
            [0, 0, 255],      # Blue accent
            [255, 255, 255],  # White background
            [0, 0, 0]         # Black text
        ],
        'typography': [0.8, 0.2, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7],  # Typography features
        'layout': [0.5, 0.3, 0.2, 0.1, 0.4, 0.6, 0.7, 0.8],      # Layout features
        'text_features': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]  # Text embeddings
    }

def demo_basic_analysis():
    """Demonstrate basic brand analysis."""
    print("🔍 Demo: Basic Brand Analysis")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = BrandAnalyzerAPI()
    
    # Create sample data
    website_data = create_sample_website_data()
    
    print("📊 Analyzing website...")
    start_time = time.time()
    
    # Analyze the website
    result = analyzer.analyze_website(website_data)
    
    analysis_time = time.time() - start_time
    
    if result['success']:
        print(f"✅ Analysis completed in {analysis_time:.2f} seconds")
        print(f"🎯 Brand Consistency Score: {result['model_outputs']['consistency_score']:.3f}")
        
        brand_kit = result['brand_kit']
        print(f"🎨 Dominant Colors: {brand_kit['color_palette'][:5]}")
        print(f"📝 Dominant Tone: {brand_kit['tone_profile']['dominant_tone']}")
        print(f"💭 Sentiment Profile: {brand_kit['sentiment_profile'][:3]}...")
        
        # Save results
        with open('brand_analysis_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("💾 Results saved to 'brand_analysis_result.json'")
        
    else:
        print(f"❌ Analysis failed: {result['error']}")
    
    print()

def demo_batch_analysis():
    """Demonstrate batch analysis of multiple websites."""
    print("🔍 Demo: Batch Brand Analysis")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = BrandAnalyzerAPI()
    
    # Create multiple sample websites
    websites = [
        {
            'colors': [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
            'typography': [0.8, 0.2, 0.1, 0.3],
            'layout': [0.5, 0.3, 0.2, 0.1],
            'text_features': [0.1, 0.2, 0.3, 0.4]
        },
        {
            'colors': [[128, 0, 128], [255, 255, 0], [0, 255, 255]],
            'typography': [0.6, 0.4, 0.2, 0.5],
            'layout': [0.3, 0.5, 0.4, 0.2],
            'text_features': [0.2, 0.3, 0.4, 0.5]
        },
        {
            'colors': [[255, 165, 0], [0, 128, 0], [255, 192, 203]],
            'typography': [0.7, 0.3, 0.1, 0.4],
            'layout': [0.4, 0.4, 0.3, 0.3],
            'text_features': [0.3, 0.4, 0.5, 0.6]
        }
    ]
    
    print(f"📊 Analyzing {len(websites)} websites...")
    start_time = time.time()
    
    # Analyze all websites
    results = analyzer.batch_analyze(websites)
    
    analysis_time = time.time() - start_time
    
    print(f"✅ Batch analysis completed in {analysis_time:.2f} seconds")
    print()
    
    # Display results
    for i, result in enumerate(results):
        if result['success']:
            consistency = result['model_outputs']['consistency_score']
            print(f"🌐 Website {i+1}: Consistency = {consistency:.3f}")
        else:
            print(f"❌ Website {i+1}: Failed - {result['error']}")
    
    print()

def demo_training():
    """Demonstrate model training with sample data."""
    print("🔍 Demo: Model Training")
    print("=" * 50)
    
    # Create sample training data
    train_data = []
    for i in range(100):  # 100 sample websites
        train_data.append({
            'colors': [[i % 255, (i * 2) % 255, (i * 3) % 255] for _ in range(5)],
            'typography': [0.1 + i * 0.01, 0.2 + i * 0.01, 0.3 + i * 0.01, 0.4 + i * 0.01],
            'layout': [0.1 + i * 0.01, 0.2 + i * 0.01, 0.3 + i * 0.01, 0.4 + i * 0.01],
            'text_features': [0.1 + i * 0.01, 0.2 + i * 0.01, 0.3 + i * 0.01, 0.4 + i * 0.01],
            'consistency_score': 0.5 + (i % 50) * 0.01  # Varying consistency scores
        })
    
    # Create dataset and dataloader
    args = BrandAnalyzerArgs(
        batch_size=16,
        learning_rate=1e-3,
        max_epochs=5,  # Short training for demo
        device="cpu"   # Use CPU for demo
    )
    
    dataset = BrandDataset(train_data, args)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Create model and trainer
    from brand_analyzer import BrandAnalyzer
    model = BrandAnalyzer(args)
    trainer = BrandTrainer(model, args)
    
    print("🚀 Starting training...")
    print(f"📊 Training on {len(train_data)} samples")
    print(f"🔧 Batch size: {args.batch_size}")
    print(f"📈 Learning rate: {args.learning_rate}")
    print()
    
    # Train the model
    start_time = time.time()
    trainer.train(dataloader)
    training_time = time.time() - start_time
    
    print(f"✅ Training completed in {training_time:.2f} seconds")
    print()

def demo_custom_configuration():
    """Demonstrate custom configuration."""
    print("🔍 Demo: Custom Configuration")
    print("=" * 50)
    
    # Create custom configuration
    custom_args = BrandAnalyzerArgs(
        hidden_size=512,           # Smaller model for demo
        num_layers=4,              # Fewer layers
        num_attention_heads=8,     # Fewer attention heads
        dropout=0.2,               # Higher dropout
        use_flash_attention=True,  # Enable flash attention
        use_mixed_precision=True,  # Enable mixed precision
        batch_size=8,              # Smaller batch size
        learning_rate=2e-4,        # Custom learning rate
        device="cpu"               # Use CPU for demo
    )
    
    print("⚙️ Custom Configuration:")
    print(f"   Hidden Size: {custom_args.hidden_size}")
    print(f"   Layers: {custom_args.num_layers}")
    print(f"   Attention Heads: {custom_args.num_attention_heads}")
    print(f"   Dropout: {custom_args.dropout}")
    print(f"   Flash Attention: {custom_args.use_flash_attention}")
    print(f"   Mixed Precision: {custom_args.use_mixed_precision}")
    print()
    
    # Create analyzer with custom config
    analyzer = BrandAnalyzerAPI()
    analyzer.args = custom_args
    analyzer.model = analyzer.model.__class__(custom_args)
    
    # Test with sample data
    website_data = create_sample_website_data()
    result = analyzer.analyze_website(website_data)
    
    if result['success']:
        print("✅ Custom configuration works!")
        print(f"🎯 Consistency Score: {result['model_outputs']['consistency_score']:.3f}")
    else:
        print(f"❌ Custom configuration failed: {result['error']}")
    
    print()

def main():
    """Main demo function."""
    print("🚀 TruthGPT Brand Analyzer Demo")
    print("=" * 60)
    print()
    
    try:
        # Run all demos
        demo_basic_analysis()
        demo_batch_analysis()
        demo_custom_configuration()
        demo_training()
        
        print("🎉 All demos completed successfully!")
        print()
        print("📚 Next Steps:")
        print("   1. Check 'brand_analysis_result.json' for detailed results")
        print("   2. Modify the sample data to test different scenarios")
        print("   3. Try training with your own data")
        print("   4. Explore the configuration options")
        print()
        print("📖 For more information, see the README.md files")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"❌ Demo failed: {str(e)}")
        print("Please check the error logs and try again.")

if __name__ == "__main__":
    main()

