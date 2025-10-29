# Automated VC Scoring Calculator
## Dynamic Startup Evaluation Tool

### Scoring Calculator Interface

#### Input Fields
**Company Information**
- Company Name: [Text Input]
- Sector: [Dropdown: AI/Climate/Fintech/Other]
- Stage: [Dropdown: Pre-Seed/Seed/Series A/Series B]
- Location: [Text Input]
- Team Size: [Number Input]

**Problem Assessment (25% weight)**
- Market Pain Intensity: [Slider 1-10]
- Market Size (TAM): [Dropdown: <$1B/$1-10B/$10-100B/>$100B]
- Market Timing: [Slider 1-10]

**Solution Analysis (20% weight)**
- Technical Moat: [Slider 1-10]
- Network Effects: [Slider 1-10]
- Data Moat: [Slider 1-10]
- Switching Costs: [Slider 1-10]

**Traction Metrics (20% weight)**
- MRR Growth: [Dropdown: <2%/2-5%/5-10%/10-20%/>20%]
- User Growth: [Dropdown: <5%/5-20%/20-50%/>50%]
- Revenue Quality: [Slider 1-10]
- Market Validation: [Slider 1-10]

**Team Evaluation (15% weight)**
- Domain Expertise: [Slider 1-10]
- Execution Track Record: [Slider 1-10]
- Team Completeness: [Slider 1-10]
- Leadership Quality: [Slider 1-10]

**Unit Economics (10% weight)**
- CAC: [Dropdown: <$100/$100-500/$500-2000/>$2000]
- LTV: [Dropdown: <$500/$500-2K/$2K-10K/>$10K]
- LTV/CAC Ratio: [Dropdown: <2x/2-3x/3-5x/5-10x/>10x]
- Burn Rate: [Dropdown: <$50K/$50-200K/$200-500K/>$500K]

**Funding Ask (5% weight)**
- Valuation Reasonableness: [Slider 1-10]
- Use of Funds: [Slider 1-10]
- Runway: [Dropdown: <6mo/6-12mo/12-18mo/>18mo]

**Red Flags Assessment (5% weight)**
- Legal/Regulatory: [Slider 1-10]
- Competition: [Slider 1-10]
- Technology Risk: [Slider 1-10]
- Market Risk: [Slider 1-10]

### Automated Scoring Logic

#### Problem Assessment Calculation
```javascript
function calculateProblemScore(painIntensity, marketSize, marketTiming) {
    const painWeight = 0.4;
    const sizeWeight = 0.4;
    const timingWeight = 0.2;
    
    const sizeScore = getMarketSizeScore(marketSize);
    const totalScore = (painIntensity * painWeight) + 
                      (sizeScore * sizeWeight) + 
                      (marketTiming * timingWeight);
    
    return Math.round(totalScore * 10) / 10;
}

function getMarketSizeScore(size) {
    const sizeMap = {
        '<$1B': 3,
        '$1-10B': 6,
        '$10-100B': 8,
        '>$100B': 10
    };
    return sizeMap[size] || 5;
}
```

#### Solution Analysis Calculation
```javascript
function calculateSolutionScore(technicalMoat, networkEffects, dataMoat, switchingCosts) {
    const weights = [0.3, 0.25, 0.25, 0.2];
    const scores = [technicalMoat, networkEffects, dataMoat, switchingCosts];
    
    const weightedScore = scores.reduce((sum, score, index) => 
        sum + (score * weights[index]), 0);
    
    return Math.round(weightedScore * 10) / 10;
}
```

#### Traction Metrics Calculation
```javascript
function calculateTractionScore(mrrGrowth, userGrowth, revenueQuality, marketValidation) {
    const mrrScore = getGrowthScore(mrrGrowth);
    const userScore = getGrowthScore(userGrowth);
    
    const weights = [0.3, 0.3, 0.2, 0.2];
    const scores = [mrrScore, userScore, revenueQuality, marketValidation];
    
    const weightedScore = scores.reduce((sum, score, index) => 
        sum + (score * weights[index]), 0);
    
    return Math.round(weightedScore * 10) / 10;
}

function getGrowthScore(growth) {
    const growthMap = {
        '<2%': 2,
        '2-5%': 4,
        '5-10%': 6,
        '10-20%': 8,
        '>20%': 10
    };
    return growthMap[growth] || 5;
}
```

#### Overall Score Calculation
```javascript
function calculateOverallScore(scores) {
    const weights = {
        problem: 0.25,
        solution: 0.20,
        traction: 0.20,
        team: 0.15,
        unitEconomics: 0.10,
        ask: 0.05,
        redFlags: 0.05
    };
    
    const weightedScore = Object.keys(weights).reduce((sum, key) => 
        sum + (scores[key] * weights[key]), 0);
    
    return Math.round(weightedScore * 10) / 10;
}
```

### Real-Time Recommendations

#### Decision Engine
```javascript
function generateRecommendation(overallScore, redFlagsScore) {
    if (overallScore >= 8.0 && redFlagsScore >= 7.0) {
        return {
            decision: 'PASS',
            confidence: 'HIGH',
            reasoning: 'Exceptional opportunity with strong fundamentals and minimal risks'
        };
    } else if (overallScore >= 6.0 && overallScore < 8.0) {
        return {
            decision: 'DEEP DIVE',
            confidence: overallScore >= 7.0 ? 'HIGH' : 'MEDIUM',
            reasoning: 'Strong opportunity requiring detailed due diligence'
        };
    } else if (overallScore >= 4.0 && overallScore < 6.0) {
        return {
            decision: 'DEEP DIVE (CAUTION)',
            confidence: 'LOW',
            reasoning: 'Moderate opportunity with significant concerns'
        };
    } else {
        return {
            decision: 'REJECT',
            confidence: 'HIGH',
            reasoning: 'Poor opportunity with major red flags'
        };
    }
}
```

#### Risk Assessment
```javascript
function assessRisks(scores) {
    const risks = [];
    
    if (scores.redFlags < 5) {
        risks.push({
            type: 'HIGH_RISK',
            description: 'Multiple red flags present',
            mitigation: 'Conduct thorough due diligence'
        });
    }
    
    if (scores.unitEconomics < 5) {
        risks.push({
            type: 'UNIT_ECONOMICS',
            description: 'Poor unit economics',
            mitigation: 'Review pricing and cost structure'
        });
    }
    
    if (scores.traction < 5) {
        risks.push({
            type: 'TRACTION',
            description: 'Weak traction metrics',
            mitigation: 'Validate product-market fit'
        });
    }
    
    return risks;
}
```

### Dynamic Scoring Adjustments

#### Sector-Specific Adjustments
```javascript
function applySectorAdjustments(baseScore, sector) {
    const adjustments = {
        'AI': {
            solution: 1.1,  // Boost solution score for AI
            team: 1.05,     // Slight boost for team
            redFlags: 0.95  // Slight penalty for red flags
        },
        'Climate': {
            problem: 1.05,  // Boost problem score
            ask: 1.1,       // Boost ask score
            redFlags: 0.9   // Penalty for red flags
        },
        'Fintech': {
            redFlags: 0.85, // Heavy penalty for red flags
            team: 1.1,      // Boost team score
            solution: 1.05  // Slight boost for solution
        }
    };
    
    const sectorAdjustment = adjustments[sector] || {};
    return Object.keys(sectorAdjustment).reduce((adjusted, key) => {
        adjusted[key] = Math.min(baseScore[key] * sectorAdjustment[key], 10);
        return adjusted;
    }, {...baseScore});
}
```

#### Stage-Specific Adjustments
```javascript
function applyStageAdjustments(baseScore, stage) {
    const adjustments = {
        'Pre-Seed': {
            traction: 0.8,      // Lower traction expectations
            team: 1.1,          // Higher team importance
            problem: 1.05       // Slight boost for problem
        },
        'Seed': {
            traction: 0.9,      // Moderate traction expectations
            unitEconomics: 0.95, // Slight penalty for unit economics
            team: 1.05          // Slight boost for team
        },
        'Series A': {
            traction: 1.1,      // Higher traction expectations
            unitEconomics: 1.05, // Boost unit economics
            team: 0.95          // Slight penalty for team
        }
    };
    
    const stageAdjustment = adjustments[stage] || {};
    return Object.keys(stageAdjustment).reduce((adjusted, key) => {
        adjusted[key] = Math.min(baseScore[key] * stageAdjustment[key], 10);
        return adjusted;
    }, {...baseScore});
}
```

### Output Dashboard

#### Score Summary
- **Overall Score**: [X]/10
- **Decision**: PASS/DEEP DIVE/REJECT
- **Confidence Level**: HIGH/MEDIUM/LOW
- **Risk Level**: LOW/MEDIUM/HIGH

#### Detailed Breakdown
- **Problem Score**: [X]/10 (25% weight)
- **Solution Score**: [X]/10 (20% weight)
- **Traction Score**: [X]/10 (20% weight)
- **Team Score**: [X]/10 (15% weight)
- **Unit Economics Score**: [X]/10 (10% weight)
- **Ask Score**: [X]/10 (5% weight)
- **Red Flags Score**: [X]/10 (5% weight)

#### Recommendations
- **Next Steps**: [List of recommended actions]
- **Due Diligence Items**: [List of DD requirements]
- **Risk Mitigation**: [List of risk mitigation strategies]
- **Follow-up Actions**: [List of follow-up actions]

#### Benchmarking
- **Sector Average**: [X]/10
- **Stage Average**: [X]/10
- **Portfolio Average**: [X]/10
- **Market Benchmark**: [X]/10



