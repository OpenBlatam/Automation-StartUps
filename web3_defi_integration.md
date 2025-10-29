# Web3 and DeFi Integration for VC
## Decentralized Finance & Web3 Investment Platform

### DeFi Investment Protocols

#### Automated Market Making for VC Tokens
**Decentralized VC Token Exchange**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract VCTokenAMM is ReentrancyGuard, Ownable {
    struct Pool {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalSupply;
        bool isActive;
    }
    
    mapping(address => mapping(address => Pool)) public pools;
    mapping(address => bool) public whitelistedTokens;
    
    uint256 public constant FEE_RATE = 30; // 0.3% fee
    uint256 public constant MINIMUM_LIQUIDITY = 1000;
    
    event PoolCreated(address indexed tokenA, address indexed tokenB, uint256 amountA, uint256 amountB);
    event LiquidityAdded(address indexed tokenA, address indexed tokenB, uint256 amountA, uint256 amountB);
    event SwapExecuted(address indexed tokenIn, address indexed tokenOut, uint256 amountIn, uint256 amountOut);
    
    modifier onlyWhitelisted(address token) {
        require(whitelistedTokens[token], "Token not whitelisted");
        _;
    }
    
    function createPool(address tokenA, address tokenB, uint256 amountA, uint256 amountB) 
        external 
        onlyWhitelisted(tokenA) 
        onlyWhitelisted(tokenB) 
    {
        require(tokenA != tokenB, "Identical tokens");
        require(amountA > 0 && amountB > 0, "Invalid amounts");
        
        // Transfer tokens from user
        IERC20(tokenA).transferFrom(msg.sender, address(this), amountA);
        IERC20(tokenB).transferFrom(msg.sender, address(this), amountB);
        
        // Create pool
        pools[tokenA][tokenB] = Pool({
            tokenA: tokenA,
            tokenB: tokenB,
            reserveA: amountA,
            reserveB: amountB,
            totalSupply: sqrt(amountA * amountB),
            isActive: true
        });
        
        emit PoolCreated(tokenA, tokenB, amountA, amountB);
    }
    
    function addLiquidity(address tokenA, address tokenB, uint256 amountA, uint256 amountB) 
        external 
        nonReentrant 
    {
        Pool storage pool = pools[tokenA][tokenB];
        require(pool.isActive, "Pool not active");
        
        // Calculate optimal amounts
        uint256 optimalAmountB = (amountA * pool.reserveB) / pool.reserveA;
        require(amountB >= optimalAmountB, "Insufficient amount B");
        
        // Transfer tokens
        IERC20(tokenA).transferFrom(msg.sender, address(this), amountA);
        IERC20(tokenB).transferFrom(msg.sender, address(this), optimalAmountB);
        
        // Update reserves
        pool.reserveA += amountA;
        pool.reserveB += optimalAmountB;
        
        // Mint liquidity tokens
        uint256 liquidity = (amountA * pool.totalSupply) / pool.reserveA;
        pool.totalSupply += liquidity;
        
        emit LiquidityAdded(tokenA, tokenB, amountA, optimalAmountB);
    }
    
    function swap(address tokenIn, address tokenOut, uint256 amountIn) 
        external 
        nonReentrant 
        returns (uint256 amountOut) 
    {
        Pool storage pool = pools[tokenIn][tokenOut];
        require(pool.isActive, "Pool not active");
        
        // Calculate amount out with fee
        uint256 amountInWithFee = amountIn * (10000 - FEE_RATE) / 10000;
        amountOut = (amountInWithFee * pool.reserveB) / (pool.reserveA + amountInWithFee);
        
        require(amountOut > 0, "Insufficient output amount");
        
        // Transfer tokens
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(tokenOut).transfer(msg.sender, amountOut);
        
        // Update reserves
        pool.reserveA += amountIn;
        pool.reserveB -= amountOut;
        
        emit SwapExecuted(tokenIn, tokenOut, amountIn, amountOut);
    }
    
    function getAmountOut(uint256 amountIn, address tokenIn, address tokenOut) 
        external 
        view 
        returns (uint256) 
    {
        Pool memory pool = pools[tokenIn][tokenOut];
        if (!pool.isActive) return 0;
        
        uint256 amountInWithFee = amountIn * (10000 - FEE_RATE) / 10000;
        return (amountInWithFee * pool.reserveB) / (pool.reserveA + amountInWithFee);
    }
    
    function whitelistToken(address token) external onlyOwner {
        whitelistedTokens[token] = true;
    }
    
    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }
}
```

### Yield Farming for VC Portfolios

#### Automated Yield Optimization
**DeFi Yield Farming Strategy**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract VCYieldFarming is ReentrancyGuard {
    struct Farm {
        address token;
        address pool;
        uint256 apy;
        uint256 totalStaked;
        uint256 rewardsPerBlock;
        bool isActive;
    }
    
    struct UserStake {
        uint256 amount;
        uint256 timestamp;
        uint256 lastClaimed;
    }
    
    mapping(address => Farm) public farms;
    mapping(address => mapping(address => UserStake)) public userStakes;
    mapping(address => bool) public supportedTokens;
    
    address public rewardToken;
    uint256 public totalRewardsDistributed;
    
    event FarmCreated(address indexed token, address indexed pool, uint256 apy);
    event Staked(address indexed user, address indexed token, uint256 amount);
    event Unstaked(address indexed user, address indexed token, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    
    modifier onlySupportedToken(address token) {
        require(supportedTokens[token], "Token not supported");
        _;
    }
    
    function createFarm(address token, address pool, uint256 apy, uint256 rewardsPerBlock) 
        external 
        onlySupportedToken(token) 
    {
        farms[token] = Farm({
            token: token,
            pool: pool,
            apy: apy,
            totalStaked: 0,
            rewardsPerBlock: rewardsPerBlock,
            isActive: true
        });
        
        emit FarmCreated(token, pool, apy);
    }
    
    function stake(address token, uint256 amount) external nonReentrant {
        Farm storage farm = farms[token];
        require(farm.isActive, "Farm not active");
        require(amount > 0, "Invalid amount");
        
        // Transfer tokens from user
        IERC20(token).transferFrom(msg.sender, address(this), amount);
        
        // Update user stake
        UserStake storage userStake = userStakes[msg.sender][token];
        if (userStake.amount > 0) {
            // Claim pending rewards first
            claimRewards(token);
        }
        
        userStake.amount += amount;
        userStake.timestamp = block.timestamp;
        userStake.lastClaimed = block.timestamp;
        
        // Update farm total
        farm.totalStaked += amount;
        
        emit Staked(msg.sender, token, amount);
    }
    
    function unstake(address token, uint256 amount) external nonReentrant {
        UserStake storage userStake = userStakes[msg.sender][token];
        require(userStake.amount >= amount, "Insufficient stake");
        
        // Claim pending rewards first
        claimRewards(token);
        
        // Update user stake
        userStake.amount -= amount;
        
        // Update farm total
        farms[token].totalStaked -= amount;
        
        // Transfer tokens back to user
        IERC20(token).transfer(msg.sender, amount);
        
        emit Unstaked(msg.sender, token, amount);
    }
    
    function claimRewards(address token) public {
        UserStake storage userStake = userStakes[msg.sender][token];
        require(userStake.amount > 0, "No stake");
        
        uint256 pendingRewards = calculatePendingRewards(msg.sender, token);
        require(pendingRewards > 0, "No rewards to claim");
        
        // Update last claimed timestamp
        userStake.lastClaimed = block.timestamp;
        
        // Transfer rewards to user
        IERC20(rewardToken).transfer(msg.sender, pendingRewards);
        
        totalRewardsDistributed += pendingRewards;
        
        emit RewardsClaimed(msg.sender, pendingRewards);
    }
    
    function calculatePendingRewards(address user, address token) public view returns (uint256) {
        UserStake memory userStake = userStakes[user][token];
        Farm memory farm = farms[token];
        
        if (userStake.amount == 0 || !farm.isActive) return 0;
        
        uint256 blocksPassed = block.number - (userStake.lastClaimed / 15); // Assuming 15 seconds per block
        uint256 rewardsPerBlock = (userStake.amount * farm.rewardsPerBlock) / farm.totalStaked;
        
        return blocksPassed * rewardsPerBlock;
    }
    
    function getFarmAPY(address token) external view returns (uint256) {
        return farms[token].apy;
    }
    
    function getUserStake(address user, address token) external view returns (uint256) {
        return userStakes[user][token].amount;
    }
    
    function addSupportedToken(address token) external {
        supportedTokens[token] = true;
    }
}
```

### NFT-Based Portfolio Representation

#### Portfolio NFTs
**Non-Fungible Portfolio Tokens**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract PortfolioNFT is ERC721, ERC721URIStorage, Ownable {
    struct PortfolioData {
        uint256 totalValue;
        uint256 totalInvestments;
        uint256 irr;
        uint256 tvpi;
        address[] companies;
        uint256[] ownerships;
        string metadata;
    }
    
    mapping(uint256 => PortfolioData) public portfolios;
    mapping(address => uint256[]) public userPortfolios;
    
    uint256 private _tokenIdCounter;
    
    event PortfolioMinted(uint256 indexed tokenId, address indexed owner, uint256 totalValue);
    event PortfolioUpdated(uint256 indexed tokenId, uint256 newValue);
    
    constructor() ERC721("PortfolioNFT", "PFNFT") {}
    
    function mintPortfolio(
        address to,
        uint256 totalValue,
        uint256 totalInvestments,
        uint256 irr,
        uint256 tvpi,
        address[] memory companies,
        uint256[] memory ownerships,
        string memory metadata
    ) external onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter++;
        
        portfolios[tokenId] = PortfolioData({
            totalValue: totalValue,
            totalInvestments: totalInvestments,
            irr: irr,
            tvpi: tvpi,
            companies: companies,
            ownerships: ownerships,
            metadata: metadata
        });
        
        userPortfolios[to].push(tokenId);
        
        _safeMint(to, tokenId);
        
        emit PortfolioMinted(tokenId, to, totalValue);
        
        return tokenId;
    }
    
    function updatePortfolio(
        uint256 tokenId,
        uint256 newValue,
        uint256 newIrr,
        uint256 newTvpi
    ) external onlyOwner {
        require(_exists(tokenId), "Token does not exist");
        
        portfolios[tokenId].totalValue = newValue;
        portfolios[tokenId].irr = newIrr;
        portfolios[tokenId].tvpi = newTvpi;
        
        emit PortfolioUpdated(tokenId, newValue);
    }
    
    function getPortfolioData(uint256 tokenId) external view returns (PortfolioData memory) {
        return portfolios[tokenId];
    }
    
    function getUserPortfolios(address user) external view returns (uint256[] memory) {
        return userPortfolios[user];
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
}
```

### Decentralized Autonomous Organization (DAO)

#### VC DAO Governance
**Decentralized VC Decision Making**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";

contract VCDAO is Governor, GovernorVotes, GovernorVotesQuorumFraction, GovernorTimelockControl {
    struct InvestmentProposal {
        address company;
        uint256 amount;
        uint256 valuation;
        uint256 ownership;
        string description;
        bool executed;
    }
    
    mapping(uint256 => InvestmentProposal) public investmentProposals;
    mapping(address => bool) public isMember;
    mapping(address => uint256) public memberStakes;
    
    uint256 public constant MINIMUM_STAKE = 1000 * 10**18; // 1000 tokens
    uint256 public constant VOTING_DELAY = 1; // 1 block
    uint256 public constant VOTING_PERIOD = 100; // 100 blocks
    uint256 public constant PROPOSAL_THRESHOLD = 1000; // 1000 tokens
    
    event InvestmentProposalCreated(uint256 indexed proposalId, address indexed company, uint256 amount);
    event InvestmentExecuted(uint256 indexed proposalId, address indexed company, uint256 amount);
    event MemberAdded(address indexed member, uint256 stake);
    
    constructor(IVotes _token, TimelockController _timelock)
        Governor("VC DAO")
        GovernorVotes(_token)
        GovernorVotesQuorumFraction(4) // 4% quorum
        GovernorTimelockControl(_timelock)
    {}
    
    function proposeInvestment(
        address company,
        uint256 amount,
        uint256 valuation,
        uint256 ownership,
        string memory description
    ) public returns (uint256) {
        require(isMember[msg.sender], "Not a DAO member");
        require(memberStakes[msg.sender] >= MINIMUM_STAKE, "Insufficient stake");
        
        // Create investment proposal
        uint256 proposalId = super.propose(
            [address(this)],
            [0],
            [abi.encodeWithSignature("executeInvestment(address,uint256,uint256,uint256)", company, amount, valuation, ownership)],
            description
        );
        
        investmentProposals[proposalId] = InvestmentProposal({
            company: company,
            amount: amount,
            valuation: valuation,
            ownership: ownership,
            description: description,
            executed: false
        });
        
        emit InvestmentProposalCreated(proposalId, company, amount);
        
        return proposalId;
    }
    
    function executeInvestment(
        address company,
        uint256 amount,
        uint256 valuation,
        uint256 ownership
    ) external {
        // This function would be called by the DAO after proposal execution
        // Implementation would include actual investment logic
        
        emit InvestmentExecuted(0, company, amount); // proposalId would be passed
    }
    
    function addMember(address member, uint256 stake) external onlyOwner {
        require(stake >= MINIMUM_STAKE, "Insufficient stake");
        
        isMember[member] = true;
        memberStakes[member] = stake;
        
        emit MemberAdded(member, stake);
    }
    
    function removeMember(address member) external onlyOwner {
        isMember[member] = false;
        memberStakes[member] = 0;
    }
    
    function getInvestmentProposal(uint256 proposalId) external view returns (InvestmentProposal memory) {
        return investmentProposals[proposalId];
    }
    
    function isMember(address account) external view returns (bool) {
        return isMember[account];
    }
    
    function getMemberStake(address account) external view returns (uint256) {
        return memberStakes[account];
    }
}
```

### Cross-Chain Integration

#### Multi-Chain VC Platform
**Cross-Chain Asset Management**
```javascript
import { ethers } from 'ethers';
import { Web3Provider } from '@ethersproject/providers';
import { Bridge } from 'cross-chain-bridge';

class CrossChainVCPlatform {
  constructor() {
    this.supportedChains = {
      ethereum: {
        chainId: 1,
        rpcUrl: 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
        contracts: {
          vcToken: '0x...',
          portfolioManager: '0x...',
          yieldFarming: '0x...'
        }
      },
      polygon: {
        chainId: 137,
        rpcUrl: 'https://polygon-rpc.com',
        contracts: {
          vcToken: '0x...',
          portfolioManager: '0x...',
          yieldFarming: '0x...'
        }
      },
      arbitrum: {
        chainId: 42161,
        rpcUrl: 'https://arb1.arbitrum.io/rpc',
        contracts: {
          vcToken: '0x...',
          portfolioManager: '0x...',
          yieldFarming: '0x...'
        }
      },
      avalanche: {
        chainId: 43114,
        rpcUrl: 'https://api.avax.network/ext/bc/C/rpc',
        contracts: {
          vcToken: '0x...',
          portfolioManager: '0x...',
          yieldFarming: '0x...'
        }
      }
    };
    
    this.bridge = new Bridge();
    this.providers = {};
    this.contracts = {};
    
    this.initializeProviders();
  }
  
  initializeProviders() {
    Object.keys(this.supportedChains).forEach(chain => {
      const chainConfig = this.supportedChains[chain];
      this.providers[chain] = new ethers.providers.JsonRpcProvider(chainConfig.rpcUrl);
    });
  }
  
  async bridgeAssets(fromChain, toChain, amount, tokenAddress) {
    try {
      // Initiate cross-chain bridge
      const bridgeTx = await this.bridge.bridgeTokens({
        fromChain: fromChain,
        toChain: toChain,
        amount: amount,
        tokenAddress: tokenAddress,
        recipient: await this.getCurrentAccount()
      });
      
      // Wait for bridge completion
      const bridgeResult = await this.bridge.waitForBridgeCompletion(bridgeTx.hash);
      
      return bridgeResult;
    } catch (error) {
      console.error('Bridge failed:', error);
      throw error;
    }
  }
  
  async getPortfolioAcrossChains(userAddress) {
    const portfolioData = {};
    
    for (const chain of Object.keys(this.supportedChains)) {
      try {
        const chainPortfolio = await this.getPortfolioOnChain(chain, userAddress);
        portfolioData[chain] = chainPortfolio;
      } catch (error) {
        console.error(`Failed to get portfolio on ${chain}:`, error);
        portfolioData[chain] = { error: error.message };
      }
    }
    
    return portfolioData;
  }
  
  async getPortfolioOnChain(chain, userAddress) {
    const provider = this.providers[chain];
    const portfolioManagerAddress = this.supportedChains[chain].contracts.portfolioManager;
    
    // Create contract instance
    const portfolioManager = new ethers.Contract(
      portfolioManagerAddress,
      portfolioManagerABI,
      provider
    );
    
    // Get portfolio data
    const portfolioData = await portfolioManager.getUserPortfolio(userAddress);
    
    return {
      totalValue: portfolioData.totalValue.toString(),
      totalInvestments: portfolioData.totalInvestments.toString(),
      irr: portfolioData.irr.toString(),
      tvpi: portfolioData.tvpi.toString(),
      companies: portfolioData.companies,
      ownerships: portfolioData.ownerships
    };
  }
  
  async optimizeYieldAcrossChains(userAddress) {
    const chainYields = {};
    
    // Get yield opportunities on each chain
    for (const chain of Object.keys(this.supportedChains)) {
      try {
        const yieldOpportunities = await this.getYieldOpportunities(chain);
        chainYields[chain] = yieldOpportunities;
      } catch (error) {
        console.error(`Failed to get yield opportunities on ${chain}:`, error);
      }
    }
    
    // Find optimal yield strategy
    const optimalStrategy = this.calculateOptimalYieldStrategy(chainYields);
    
    // Execute cross-chain yield optimization
    const executionResults = await this.executeYieldStrategy(optimalStrategy, userAddress);
    
    return executionResults;
  }
  
  async getYieldOpportunities(chain) {
    const provider = this.providers[chain];
    const yieldFarmingAddress = this.supportedChains[chain].contracts.yieldFarming;
    
    const yieldFarming = new ethers.Contract(
      yieldFarmingAddress,
      yieldFarmingABI,
      provider
    );
    
    const farms = await yieldFarming.getAllFarms();
    
    return farms.map(farm => ({
      token: farm.token,
      apy: farm.apy.toString(),
      totalStaked: farm.totalStaked.toString(),
      isActive: farm.isActive
    }));
  }
  
  calculateOptimalYieldStrategy(chainYields) {
    // Calculate optimal yield strategy across chains
    const strategy = {
      allocations: {},
      expectedYield: 0,
      riskScore: 0
    };
    
    // Simple optimization: allocate to highest yield farms
    Object.keys(chainYields).forEach(chain => {
      const farms = chainYields[chain];
      const bestFarm = farms.reduce((best, current) => 
        current.apy > best.apy ? current : best
      );
      
      strategy.allocations[chain] = {
        farm: bestFarm,
        allocation: 1 / Object.keys(chainYields).length // Equal allocation
      };
      
      strategy.expectedYield += bestFarm.apy * strategy.allocations[chain].allocation;
    });
    
    return strategy;
  }
  
  async executeYieldStrategy(strategy, userAddress) {
    const results = {};
    
    for (const chain of Object.keys(strategy.allocations)) {
      try {
        const allocation = strategy.allocations[chain];
        const result = await this.stakeOnChain(chain, userAddress, allocation);
        results[chain] = result;
      } catch (error) {
        console.error(`Failed to execute strategy on ${chain}:`, error);
        results[chain] = { error: error.message };
      }
    }
    
    return results;
  }
  
  async stakeOnChain(chain, userAddress, allocation) {
    const provider = this.providers[chain];
    const yieldFarmingAddress = this.supportedChains[chain].contracts.yieldFarming;
    
    const yieldFarming = new ethers.Contract(
      yieldFarmingAddress,
      yieldFarmingABI,
      provider
    );
    
    // Get user's token balance
    const tokenBalance = await this.getTokenBalance(chain, userAddress);
    const stakeAmount = tokenBalance.mul(allocation.allocation);
    
    // Execute stake
    const stakeTx = await yieldFarming.stake(allocation.farm.token, stakeAmount);
    await stakeTx.wait();
    
    return {
      txHash: stakeTx.hash,
      amount: stakeAmount.toString(),
      farm: allocation.farm
    };
  }
  
  async getTokenBalance(chain, userAddress) {
    const provider = this.providers[chain];
    const tokenAddress = this.supportedChains[chain].contracts.vcToken;
    
    const token = new ethers.Contract(tokenAddress, erc20ABI, provider);
    return await token.balanceOf(userAddress);
  }
  
  async getCurrentAccount() {
    // Implementation to get current user account
    // This would typically come from a wallet connection
    return '0x...'; // Placeholder
  }
}

export default CrossChainVCPlatform;
```

### DeFi Analytics Dashboard

#### Real-Time DeFi Metrics
**Comprehensive DeFi Analytics**
```javascript
import { Web3Provider } from '@ethersproject/providers';
import { UniswapV2Factory } from '@uniswap/v2-core';
import { SushiSwapFactory } from '@sushiswap/core';

class DeFiAnalyticsDashboard {
  constructor() {
    this.providers = {
      ethereum: new Web3Provider(window.ethereum),
      polygon: new ethers.providers.JsonRpcProvider('https://polygon-rpc.com'),
      arbitrum: new ethers.providers.JsonRpcProvider('https://arb1.arbitrum.io/rpc')
    };
    
    this.dexFactories = {
      uniswap: '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
      sushiswap: '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac',
      pancakeswap: '0xcA143Ce0Fe65960E6Aa4D42C8d3cE161c2B6604f'
    };
    
    this.analytics = {
      totalValueLocked: 0,
      yieldOpportunities: [],
      liquidityPools: [],
      arbitrageOpportunities: []
    };
  }
  
  async getTotalValueLocked() {
    const tvlData = {};
    
    for (const chain of Object.keys(this.providers)) {
      try {
        const chainTVL = await this.getChainTVL(chain);
        tvlData[chain] = chainTVL;
      } catch (error) {
        console.error(`Failed to get TVL on ${chain}:`, error);
      }
    }
    
    return tvlData;
  }
  
  async getChainTVL(chain) {
    const provider = this.providers[chain];
    const factories = this.dexFactories;
    
    let totalTVL = 0;
    const poolData = [];
    
    for (const [dex, factoryAddress] of Object.entries(factories)) {
      try {
        const factory = new ethers.Contract(factoryAddress, factoryABI, provider);
        const allPairs = await factory.getAllPairs();
        
        for (const pairAddress of allPairs) {
          const pair = new ethers.Contract(pairAddress, pairABI, provider);
          const reserves = await pair.getReserves();
          const totalSupply = await pair.totalSupply();
          
          const poolTVL = reserves[0].add(reserves[1]);
          totalTVL += parseFloat(ethers.utils.formatEther(poolTVL));
          
          poolData.push({
            dex: dex,
            pair: pairAddress,
            tvl: poolTVL.toString(),
            reserves: reserves.map(r => r.toString())
          });
        }
      } catch (error) {
        console.error(`Failed to get ${dex} data on ${chain}:`, error);
      }
    }
    
    return {
      totalTVL: totalTVL,
      pools: poolData
    };
  }
  
  async getYieldOpportunities() {
    const yieldData = {};
    
    for (const chain of Object.keys(this.providers)) {
      try {
        const chainYields = await this.getChainYieldOpportunities(chain);
        yieldData[chain] = chainYields;
      } catch (error) {
        console.error(`Failed to get yield opportunities on ${chain}:`, error);
      }
    }
    
    return yieldData;
  }
  
  async getChainYieldOpportunities(chain) {
    const provider = this.providers[chain];
    const yieldFarmingAddress = this.supportedChains[chain].contracts.yieldFarming;
    
    const yieldFarming = new ethers.Contract(
      yieldFarmingAddress,
      yieldFarmingABI,
      provider
    );
    
    const farms = await yieldFarming.getAllFarms();
    
    return farms.map(farm => ({
      token: farm.token,
      apy: farm.apy.toString(),
      totalStaked: farm.totalStaked.toString(),
      isActive: farm.isActive,
      riskScore: this.calculateRiskScore(farm)
    }));
  }
  
  calculateRiskScore(farm) {
    // Simple risk scoring based on APY and total staked
    const apyRisk = Math.min(farm.apy / 100, 1); // Higher APY = higher risk
    const liquidityRisk = Math.max(0, 1 - (farm.totalStaked / 1000000)); // Lower liquidity = higher risk
    
    return (apyRisk + liquidityRisk) / 2;
  }
  
  async getArbitrageOpportunities() {
    const arbitrageData = {};
    
    for (const chain of Object.keys(this.providers)) {
      try {
        const chainArbitrage = await this.getChainArbitrageOpportunities(chain);
        arbitrageData[chain] = chainArbitrage;
      } catch (error) {
        console.error(`Failed to get arbitrage opportunities on ${chain}:`, error);
      }
    }
    
    return arbitrageData;
  }
  
  async getChainArbitrageOpportunities(chain) {
    const provider = this.providers[chain];
    const opportunities = [];
    
    // Compare prices across different DEXs
    const dexPrices = await this.getDexPrices(chain);
    
    for (const token of Object.keys(dexPrices)) {
      const prices = dexPrices[token];
      const maxPrice = Math.max(...prices.map(p => p.price));
      const minPrice = Math.min(...prices.map(p => p.price));
      
      if (maxPrice > minPrice * 1.01) { // 1% arbitrage opportunity
        opportunities.push({
          token: token,
          buyDex: prices.find(p => p.price === minPrice).dex,
          sellDex: prices.find(p => p.price === maxPrice).dex,
          profit: maxPrice - minPrice,
          profitPercentage: ((maxPrice - minPrice) / minPrice) * 100
        });
      }
    }
    
    return opportunities;
  }
  
  async getDexPrices(chain) {
    const provider = this.providers[chain];
    const tokenPrices = {};
    
    // Get prices from different DEXs
    for (const [dex, factoryAddress] of Object.entries(this.dexFactories)) {
      try {
        const factory = new ethers.Contract(factoryAddress, factoryABI, provider);
        const allPairs = await factory.getAllPairs();
        
        for (const pairAddress of allPairs) {
          const pair = new ethers.Contract(pairAddress, pairABI, provider);
          const reserves = await pair.getReserves();
          const token0 = await pair.token0();
          const token1 = await pair.token1();
          
          // Calculate price
          const price = reserves[1].div(reserves[0]);
          
          if (!tokenPrices[token0]) tokenPrices[token0] = [];
          if (!tokenPrices[token1]) tokenPrices[token1] = [];
          
          tokenPrices[token0].push({
            dex: dex,
            price: parseFloat(ethers.utils.formatEther(price))
          });
          
          tokenPrices[token1].push({
            dex: dex,
            price: parseFloat(ethers.utils.formatEther(price))
          });
        }
      } catch (error) {
        console.error(`Failed to get ${dex} prices on ${chain}:`, error);
      }
    }
    
    return tokenPrices;
  }
  
  async getPortfolioPerformance() {
    const performanceData = {};
    
    for (const chain of Object.keys(this.providers)) {
      try {
        const chainPerformance = await this.getChainPortfolioPerformance(chain);
        performanceData[chain] = chainPerformance;
      } catch (error) {
        console.error(`Failed to get portfolio performance on ${chain}:`, error);
      }
    }
    
    return performanceData;
  }
  
  async getChainPortfolioPerformance(chain) {
    const provider = this.providers[chain];
    const portfolioManagerAddress = this.supportedChains[chain].contracts.portfolioManager;
    
    const portfolioManager = new ethers.Contract(
      portfolioManagerAddress,
      portfolioManagerABI,
      provider
    );
    
    const portfolioData = await portfolioManager.getPortfolioMetrics();
    
    return {
      totalValue: portfolioData.totalValue.toString(),
      totalInvestments: portfolioData.totalInvestments.toString(),
      irr: portfolioData.irr.toString(),
      tvpi: portfolioData.tvpi.toString(),
      dpi: portfolioData.dpi.toString()
    };
  }
}

export default DeFiAnalyticsDashboard;
```

This comprehensive Web3 and DeFi integration provides a complete decentralized finance ecosystem for VC operations, including automated market making, yield farming, NFT-based portfolio representation, DAO governance, cross-chain integration, and real-time DeFi analytics.



