//<context:REQ>
//The requirements of the contract are
//1. The contract should have a function to stake the NFT token
//2. The user should be able to stake between 7 days to 300 days
//3. The contract should have a function to withdraw the staked NFT token
//4. The contract should have a function to check the staked NFT token
//5. The reward is an erc20 token provided in the constructor, which will be transafered to this contract
//6. The staking mechanism should be calculated according to this way:
//      6.1 Starting day one, if a user stakes the NFT, they will get 100% of the 
//      daily reward which should be set in the construcoctor (example 10 tokens per day)
//      6.2 Every passing 24 hours from the contract deployment, the reward will be reduced by 0.1% 
//      to instroduce the deflationary mechanism, until it reaches 0.1 percent of the original value
//      6.3 the mechanism is implemented in a way the user can withdraw the NFT at any moment with a 30 percent penalty
//      6.4 The deflationary mechanism works only for new Stakers so the rate is locked for the particular day the staker
//      stakes the NFT. For example if I choose to stake 7 days, I will receive the daily reward according to the rate of the day, I staked on
//      6.5 this needs to be implemented in the calculation of the reward.
//<context:REQ/>

//<prompt:Constructor>
// Please write the constructor for the contract based on the requirements
// {REQ}
//<prompt:Constructor/>

//<Constructor>
// SPDX-License-Identifier-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract NFTStakingContract {

    IERC721 public nftToken;
    IERC20 public rewardToken;
    uint256 public dailyReward;
    uint256 public contractDeployTime;
    uint256 public constant MINIMUM_STAKING_PERIOD = 7 days;
    uint256 public constant MAXIMUM_STAKING_PERIOD = 300 days;
    uint256 public constant PENALTY_PERCENTAGE = 30;
    uint256 public constant MAX_REWARD_REDUCTION = 1000; // represents 1000x reduction to 0.1%
    uint256 public constant DAILY_REWARD_REDUCTION = 1; // 0.1%

    // Struct to keep track of each stake
    struct Stake {
        uint256 tokenId;
        uint256 stakingTime;
        uint256 stakingPeriod;
        uint256 lockedRewardRate;
    }

    mapping(address => Stake) public stakes;

    /**
     * @dev Constructor for the NFT staking contract
     * @param _nftToken The NFT token to be staked
     * @param _rewardToken The ERC20 reward token to be distributed
     * @param _dailyReward The daily reward for staking the NFT
     */
    constructor(IERC721 _nftToken, IERC20 _rewardToken, uint256 _dailyReward) {
        nftToken = _nftToken;
        rewardToken = _rewardToken;
        dailyReward = _dailyReward;
        contractDeployTime = block.timestamp;
    }

    // The functions to stake, withdraw, and check the staked NFT token as well as reward calculations will be added separately

    // Please note that actual reward distribution logic is not provided in this constructor but should be implemented in the relevant functions.
}
//<Constructor/>

//<prompt:StakingFuncions>
// Please implement functions for nr 1,2,3,4 form the requirements
// {REQ}
//<prompt:StakingFuncions/>

//<StakingFuncions>
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract NFTStaking {
    // SafeMath library is used for safe calculations with uint256
    using SafeMath for uint256;
    
    IERC721 public nft; // Interface for the NFT contract
    IERC20 public rewardToken; // Interface for the ERC20 reward token
    
    uint256 public constant MAX_STAKE_DAYS = 300;
    uint256 public constant MIN_STAKE_DAYS = 7;
    uint256 public constant PENALTY_PERCENT = 30;
    
    uint256 public dailyReward;
    uint256 public contractDeploymentTimestamp;
    uint256 public initialDailyReward;

    // Struct to represent staking information
    struct Stake {
        uint256 tokenId;
        uint256 stakeTimestamp;
        uint256 stakedDays;
    }
    
    // Mapping of staker's address to stake information
    mapping(address => Stake) public stakes;

    // Event emitted when a token is staked
    event Staked(address indexed user, uint256 tokenId, uint256 stakedDays);
    // Event emitted when a token is withdrawn
    event Withdrawn(address indexed user, uint256 tokenId);
    
    constructor(IERC20 _rewardToken, uint256 _dailyReward) {
        rewardToken = _rewardToken;
        dailyReward = _dailyReward;
        initialDailyReward = _dailyReward;
        contractDeploymentTimestamp = block.timestamp;
    }
    
    // Function to stake the NFT token
    function stake(uint256 tokenId, uint256 stakedDays) external {
        require(stakedDays >= MIN_STAKE_DAYS && stakedDays <= MAX_STAKE_DAYS, "Staking days out of range");
        
        nft.transferFrom(msg.sender, address(this), tokenId); // Transfers the NFT to this contract

        uint256 stakeTimestamp = block.timestamp;
        stakes[msg.sender] = Stake(tokenId, stakeTimestamp, stakedDays);
        
        emit Staked(msg.sender, tokenId, stakedDays);
    }
    
    // Function to withdraw the staked NFT token
    function withdraw() external {
        Stake storage stakeInfo = stakes[msg.sender];
        require(stakeInfo.tokenId != 0, "No token staked");
        
        uint256 currentRate = currentRewardRate();
        uint256 reward = calculateReward(stakeInfo.stakeTimestamp, stakeInfo.stakedDays, currentRate);
        
        if (block.timestamp < stakeInfo.stakeTimestamp.add(stakeInfo.stakedDays.mul(1 days))) {
            // Apply the penalty if withdrawn before staked period
            reward = reward.mul(100 - PENALTY_PERCENT).div(100);
        }
        
        nft.transferFrom(address(this), msg.sender, stakeInfo.tokenId); // Transfers the NFT back to the owner
        rewardToken.transfer(msg.sender, reward); // Transfer the calculated reward
        
        delete stakes[msg.sender]; // Remove the stake info for the user

        emit Withdrawn(msg.sender, stakeInfo.tokenId);
    }
    
    // Function to check the staked NFT token
    function checkStake(address user) external view returns (Stake memory) {
        return stakes[user];
    }
    
    // Helper function to calculate the reward based on the current rate and staked time
    function calculateReward(uint256 stakeTimestamp, uint256 stakedDays, uint256 currentRate) internal view returns (uint256) {
        uint256 stakingDays = (block.timestamp.sub(stakeTimestamp)).div(1 days);
        uint256 finalDays is stakingDays > stakedDays ? stakedDays : stakingDays;
        return finalDays.mul(currentRate);
    }
    
    // Function to calculate the current reward rate
    function currentRewardRate() public view returns (uint256) {
        uint256 daysSinceDeployment = (block.timestamp.sub(contractDeploymentTimestamp)).div(1 days);
        uint256 deflationFactor = 1000 - daysSinceDeployment; // 0.1% deflation per day
        deflationFactor = deflationFactor < 1 ? 1 : deflationFactor; // Min rate is 0.1%
        return initialDailyReward.mul(deflationFactor).div(1000);
    }
}
//<StakingFuncions/>

//<prompt:RewardCalc>
// Please implement the reward calculation view function and reward for the requirements:
// {REQ}
//<prompt:RewardCalc/>

//<RewardCalc>
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract NFTStakingContract {

    IERC721 public immutable nftToken;
    IERC20 public immutable rewardToken;
    uint256 public immutable rewardPerDay;
    uint256 public immutable startTimestamp;
    uint256 public constant MAX_STAKE_DAYS = 300;
    uint256 public constant MIN_STAKE_DAYS = 7;
    uint256 public constant PENALTY_PERCENT = 30;
    uint256 public constant DEF_MULT = 1000; // Multiplier to handle deflation with integers
    uint256 public deflationRatePerDay;

    struct StakedToken {
        uint256 tokenId;
        address owner;
        uint256 stakeTimestamp;
        uint256 stakeDays;
        uint256 rateOnStake;
    }

    mapping(uint256 => StakedToken) public stakedTokens;
    uint256 public stakedTokenCount;

    constructor(IERC721 _nftToken, IERC20 _rewardToken, uint256 _rewardPerDay) {
        nftToken = _nftToken;
        rewardToken = _rewardToken;
        rewardPerDay = _rewardPerDay;
        startTimestamp = block.timestamp;
        deflationRatePerDay = 999; // 100% - 0.1%
    }

    // Stake NFT with tokenId for a certain number of days
    function stakeNFT(uint256 tokenId, uint256 stakeDays) external {
        require(stakeDays >= MIN_STAKE_DAYS && stakeDays <= MAX_STAKE_DAYS, "Invalid staking period");
        
        nftToken.transferFrom(msg.sender, address(this), tokenId);

        uint256 currentRate = getCurrentRate();
        
        stakedTokens[stakedTokenCount] = StakedToken({
            tokenId: tokenId,
            owner: msg.sender,
            stakeTimestamp: block.timestamp,
            stakeDays: stakeDays,
            rateOnStake: currentRate
        });

        stakedTokenCount++;
    }

    // Withdraw the staked NFT
    function withdrawNFT(uint256 stakeId) external {
        StakedToken storage tokenInfo = stakedTokens[stakeId];
        
        require(msg.sender == tokenInfo.owner, "You do not own this staked token");

        // Calculate reward for the staked period
        uint256 withdrawTimestamp = block.timestamp;
        uint256 stakedDuration = withdrawTimestamp - tokenInfo.stakeTimestamp;
        uint256 rewardAmount = calculateReward(tokenInfo.rateOnStake, stakedDuration, tokenInfo.stakeDays);

        // Apply penalty if less than the staking period
        if (stakedDuration < tokenInfo.stakeDays * 1 days) {
            rewardAmount = (rewardAmount * (100 - PENALTY_PERCENT)) / 100;
        }

        rewardToken.transfer(msg.sender, rewardAmount);
        nftToken.transferFrom(address(this), msg.sender, tokenInfo.tokenId);
        
        delete stakedTokens[stakeId];
    }

    // Check the staked NFT
    function checkStakedNFT(uint256 stakeId) external view returns (StakedToken memory) {
        return stakedTokens[stakeId];
    }

    // Calculate the current daily rate based on deflation
    function getCurrentRate() public view returns (uint256) {
        uint256 daysSinceStart = (block.timestamp - startTimestamp) / 1 days;
        uint256 currentRate = rewardPerDay * deflationRatePerDay**daysSinceStart / DEF_MULT**daysSinceStart;
        return currentRate > rewardPerDay / 1000 ? currentRate : rewardPerDay / 1000;
    }

    // Helper function to calculate the reward based on staking period
    function calculateReward(uint256 rateOnStake, uint256 stakedDurationInSeconds, uint256 stakeDays) internal view returns (uint256) {
        uint256 stakingPeriodInSeconds = stakeDays * 1 days;
        uint256 actualStakedPeriod = stakedDurationInSeconds < stakingPeriodInSeconds ? stakedDurationInSeconds : stakingPeriodInSeconds;
        uint256 totalReward = (actualStakedPeriod / 1 days) * rateOnStake;
        return totalReward;
    }
}
//<RewardCalc/>