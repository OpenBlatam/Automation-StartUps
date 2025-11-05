const express = require('express');
const router = express.Router();

/**
 * Blockchain Marketing API Routes
 * Handles all blockchain and Web3 operations
 */

// Get blockchain state
router.get('/state', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const state = blockchainMarketing.getBlockchainState();
    
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('Error getting blockchain state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get blockchain state'
    });
  }
});

// Get latest blocks
router.get('/blocks', async (req, res) => {
  try {
    const { limit = 10 } = req.query;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const blocks = blockchainMarketing.getLatestBlocks(parseInt(limit));
    
    res.json({
      success: true,
      data: blocks
    });
  } catch (error) {
    console.error('Error getting blocks:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get blocks'
    });
  }
});

// Get pending transactions
router.get('/transactions/pending', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const transactions = blockchainMarketing.getPendingTransactions();
    
    res.json({
      success: true,
      data: transactions
    });
  } catch (error) {
    console.error('Error getting pending transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get pending transactions'
    });
  }
});

// Get confirmed transactions
router.get('/transactions/confirmed', async (req, res) => {
  try {
    const { limit = 50 } = req.query;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const transactions = blockchainMarketing.getConfirmedTransactions(parseInt(limit));
    
    res.json({
      success: true,
      data: transactions
    });
  } catch (error) {
    console.error('Error getting confirmed transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get confirmed transactions'
    });
  }
});

// Create transaction
router.post('/transactions', async (req, res) => {
  try {
    const { from, to, amount, type } = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const transaction = blockchainMarketing.createTransaction(from, to, amount, type);
    
    res.json({
      success: true,
      data: transaction
    });
  } catch (error) {
    console.error('Error creating transaction:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create transaction'
    });
  }
});

// Get smart contracts
router.get('/contracts', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const state = blockchainMarketing.getBlockchainState();
    
    res.json({
      success: true,
      data: state.smartContracts
    });
  } catch (error) {
    console.error('Error getting smart contracts:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get smart contracts'
    });
  }
});

// Get NFT collections
router.get('/nfts/collections', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const collections = blockchainMarketing.getNFTCollections();
    
    res.json({
      success: true,
      data: collections
    });
  } catch (error) {
    console.error('Error getting NFT collections:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get NFT collections'
    });
  }
});

// Create NFT collection
router.post('/nfts/collections', async (req, res) => {
  try {
    const collectionData = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const collection = blockchainMarketing.createNFTCollection(collectionData);
    
    res.json({
      success: true,
      data: collection
    });
  } catch (error) {
    console.error('Error creating NFT collection:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create NFT collection'
    });
  }
});

// Mint NFT
router.post('/nfts/mint', async (req, res) => {
  try {
    const { collectionId, to, metadata } = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const nft = blockchainMarketing.mintNFT(collectionId, to, metadata);
    
    res.json({
      success: true,
      data: nft
    });
  } catch (error) {
    console.error('Error minting NFT:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to mint NFT'
    });
  }
});

// Get DAO proposals
router.get('/dao/proposals', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const proposals = blockchainMarketing.getActiveDAOProposals();
    
    res.json({
      success: true,
      data: proposals
    });
  } catch (error) {
    console.error('Error getting DAO proposals:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get DAO proposals'
    });
  }
});

// Create DAO proposal
router.post('/dao/proposals', async (req, res) => {
  try {
    const proposalData = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const proposal = blockchainMarketing.createDAOProposal(proposalData);
    
    res.json({
      success: true,
      data: proposal
    });
  } catch (error) {
    console.error('Error creating DAO proposal:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create DAO proposal'
    });
  }
});

// Vote on DAO proposal
router.post('/dao/proposals/:id/vote', async (req, res) => {
  try {
    const { id } = req.params;
    const { voter, vote, votingPower } = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const proposal = blockchainMarketing.voteOnProposal(id, voter, vote, votingPower);
    
    res.json({
      success: true,
      data: proposal
    });
  } catch (error) {
    console.error('Error voting on proposal:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to vote on proposal'
    });
  }
});

// Execute DAO proposal
router.post('/dao/proposals/:id/execute', async (req, res) => {
  try {
    const { id } = req.params;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const proposal = blockchainMarketing.executeDAOProposal(id);
    
    res.json({
      success: true,
      data: proposal
    });
  } catch (error) {
    console.error('Error executing proposal:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to execute proposal'
    });
  }
});

// Get DeFi protocols
router.get('/defi/protocols', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const protocols = blockchainMarketing.getDeFiProtocols();
    
    res.json({
      success: true,
      data: protocols
    });
  } catch (error) {
    console.error('Error getting DeFi protocols:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get DeFi protocols'
    });
  }
});

// Add liquidity to DeFi protocol
router.post('/defi/protocols/:id/liquidity', async (req, res) => {
  try {
    const { id } = req.params;
    const { tokenA, tokenB, amountA, amountB } = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const protocol = blockchainMarketing.addLiquidity(parseInt(id), tokenA, tokenB, amountA, amountB);
    
    res.json({
      success: true,
      data: protocol
    });
  } catch (error) {
    console.error('Error adding liquidity:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to add liquidity'
    });
  }
});

// Stake tokens
router.post('/defi/stake', async (req, res) => {
  try {
    const { protocolId, amount } = req.body;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const protocol = blockchainMarketing.stakeTokens(parseInt(protocolId), amount);
    
    res.json({
      success: true,
      data: protocol
    });
  } catch (error) {
    console.error('Error staking tokens:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to stake tokens'
    });
  }
});

// Get wallet balance
router.get('/wallets/:address/balance', async (req, res) => {
  try {
    const { address } = req.params;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const balance = blockchainMarketing.getWalletBalance(address);
    
    res.json({
      success: true,
      data: {
        address,
        balance
      }
    });
  } catch (error) {
    console.error('Error getting wallet balance:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get wallet balance'
    });
  }
});

// Get wallet transaction history
router.get('/wallets/:address/transactions', async (req, res) => {
  try {
    const { address } = req.params;
    const { limit = 50 } = req.query;
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    
    const transactions = blockchainMarketing.getWalletTransactionHistory(address, parseInt(limit));
    
    res.json({
      success: true,
      data: transactions
    });
  } catch (error) {
    console.error('Error getting wallet transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get wallet transactions'
    });
  }
});

// Get blockchain analytics
router.get('/analytics', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const analytics = blockchainMarketing.getBlockchainAnalytics();
    
    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('Error getting blockchain analytics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get blockchain analytics'
    });
  }
});

// Validate blockchain
router.get('/validate', async (req, res) => {
  try {
    const blockchainMarketing = req.app.locals.blockchainMarketing;
    const isValid = blockchainMarketing.validateBlockchain();
    
    res.json({
      success: true,
      data: {
        isValid,
        message: isValid ? 'Blockchain is valid' : 'Blockchain validation failed'
      }
    });
  } catch (error) {
    console.error('Error validating blockchain:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to validate blockchain'
    });
  }
});

module.exports = router;

