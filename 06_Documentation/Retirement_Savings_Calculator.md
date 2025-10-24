# Retirement Savings Calculator

## Personal Information
| Field | Value | Notes |
|-------|-------|-------|
| Current Age | | |
| Desired Retirement Age | | |
| Years to Retirement | =B3-B2 | |
| Current Annual Income | | |
| Expected Retirement Income Need | | |
| Expected Social Security | | |
| Expected Pension | | |
| Other Retirement Income | | |

## Retirement Income Analysis
| Income Source | Annual Amount (MXN) | Monthly Amount | Notes |
|---------------|-------------------|----------------|-------|
| Social Security | | | |
| Pension | | | |
| Other Income | | | |
| **Total Guaranteed Income** | **=SUM(B10:B12)** | **=B13/12** | |
| **Income Gap** | **=B5-B13** | **=B15/12** | Amount needed from savings |

## Retirement Savings Calculation

### Method 1: 4% Rule
| Required Annual Income from Savings | Required Total Savings | Monthly Savings Needed |
|-----------------------------------|----------------------|----------------------|
| =B15 | =B16/0.04 | =B17/(B4*12) |

### Method 2: 25x Annual Expenses
| Annual Retirement Expenses | Required Total Savings | Monthly Savings Needed |
|---------------------------|----------------------|----------------------|
| =B5 | =B20*25 | =B21/(B4*12) |

### Method 3: Detailed Calculation
| Item | Amount (MXN) | Notes |
|------|--------------|-------|
| Annual Retirement Expenses | =B5 | |
| Minus Social Security | =-B10 | |
| Minus Pension | =-B11 | |
| Minus Other Income | =-B12 | |
| **Net Annual Need** | **=SUM(B24:B27)** | |
| **Required Savings (4% rule)** | **=B28/0.04** | |
| **Required Savings (3% rule)** | **=B28/0.03** | Conservative approach |

## Current Retirement Savings Status
| Account Type | Current Balance | Annual Contribution | Employer Match | Total Annual Contribution |
|--------------|-----------------|-------------------|----------------|-------------------------|
| 401(k) | | | | |
| IRA (Traditional) | | | | |
| IRA (Roth) | | | | |
| Other Retirement | | | | |
| **Total Current Savings** | **=SUM(B32:B35)** | **=SUM(C32:C35)** | **=SUM(D32:D35)** | **=SUM(E32:E35)** |

## Retirement Savings Projection
| Age | Years to Retirement | Current Savings | Annual Contribution | Expected Return | Projected Balance |
|-----|-------------------|-----------------|-------------------|-----------------|------------------|
| =B2 | =B4 | =B36 | =B37 | 7% | =B40*(1+B42)^B41 + B41*B39 |
| =B2+5 | =B4-5 | | =B39 | 7% | |
| =B2+10 | =B4-10 | | =B39 | 7% | |
| =B2+15 | =B4-15 | | =B39 | 7% | |
| =B2+20 | =B4-20 | | =B39 | 7% | |
| =B3 | 0 | | =B39 | 7% | |

## Retirement Savings Gap Analysis
| Scenario | Required Savings | Projected Savings | Gap/Surplus | Action Needed |
|----------|------------------|------------------|-------------|---------------|
| Conservative (3% rule) | =B30 | =B47 | =B48-B47 | |
| Moderate (4% rule) | =B17 | =B47 | =B48-B47 | |
| Aggressive (5% rule) | =B28/0.05 | =B47 | =B48-B47 | |

## Catch-Up Strategies
| Strategy | Additional Monthly Savings | Timeline | Impact |
|----------|---------------------------|----------|--------|
| Increase 401(k) contribution | | 1 year | |
| Max out IRA contributions | | 1 year | |
| Take advantage of catch-up contributions (50+) | | | |
| Reduce current expenses | | | |
| Increase income | | | |
| Delay retirement by 1 year | | | |
| Delay retirement by 2 years | | | |
| **Total Additional Savings** | **=SUM(B55:B61)** | | |

## Retirement Account Optimization
| Account Type | 2024 Contribution Limit | Current Contribution | Room for Increase | Priority |
|--------------|------------------------|---------------------|------------------|----------|
| 401(k) | $23,000 | | | 1 |
| 401(k) Catch-up (50+) | $7,500 | | | 2 |
| IRA (Traditional) | $7,000 | | | 3 |
| IRA (Roth) | $7,000 | | | 4 |
| IRA Catch-up (50+) | $1,000 | | | 5 |

## Tax Considerations
| Account Type | Tax Treatment | Withdrawal Age | Required Minimum Distributions |
|--------------|---------------|----------------|-------------------------------|
| 401(k) Traditional | Tax-deferred | 59.5 | Yes (72+) |
| IRA Traditional | Tax-deferred | 59.5 | Yes (72+) |
| IRA Roth | Tax-free | 59.5 | No |
| 401(k) Roth | Tax-free | 59.5 | No |

## Retirement Lifestyle Planning
| Expense Category | Current Monthly | Retirement Monthly | Change | Notes |
|------------------|-----------------|-------------------|--------|-------|
| Housing | | | | |
| Healthcare | | | | |
| Transportation | | | | |
| Food | | | | |
| Entertainment | | | | |
| Travel | | | | |
| Insurance | | | | |
| **Total Monthly** | | | | |

## Retirement Income Sources Timeline
| Age | Social Security | Pension | 401(k) | IRA | Other | Total |
|-----|-----------------|---------|--------|-----|-------|-------|
| 62 | | | | | | |
| 65 | | | | | | |
| 67 | | | | | | |
| 70 | | | | | | |
| 72 | | | | | | |

## Monthly Retirement Planning Checklist
- [ ] Review current contribution rates
- [ ] Check employer match utilization
- [ ] Rebalance retirement portfolio
- [ ] Update income projections
- [ ] Review retirement goals
- [ ] Consider catch-up contributions
- [ ] Plan for healthcare costs

## Retirement Milestones
- [ ] Start contributing to 401(k)
- [ ] Get full employer match
- [ ] Max out 401(k) contributions
- [ ] Open IRA account
- [ ] Max out IRA contributions
- [ ] Start catch-up contributions (50+)
- [ ] Reach 1x annual salary saved
- [ ] Reach 3x annual salary saved
- [ ] Reach 5x annual salary saved
- [ ] Reach 10x annual salary saved

## Notes
- Update calculations annually
- Consider inflation in projections (use 3% inflation rate)
- Review Social Security estimates annually
- Plan for healthcare costs in retirement
- Consider long-term care insurance
- Update beneficiary information regularly
