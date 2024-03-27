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

//<prompt:MAIN>
// I want a second admin function.
// I want an admin function to allow me to change the reward reduction.
// {REQ}
// {CODE}
//<prompt:MAIN/>

//<context:CODE>
//<MAIN>
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NFT_Staking_2 is ReentrancyGuard, Ownable {
    IERC721 public immutable nftToken;
    IERC20 public immutable rewardToken;
    
    struct Stake {
        uint256 tokenId;
        uint256 stakedAt;
        uint256 stakesTill;
        uint256 currentRewardRate;
    }
    
    uint256 public constant DAY_IN_SECONDS = 86400;
    uint256 public constant MAX_STAKING_DAYS = 300;
    uint256 public constant MIN_STAKING_DAYS = 7;
    uint256 public constant REWARD_REDUCTION_PER_DAY = 1; // (0.1% in basis points)
    uint256 public constant PENALTY_RATE = 30;
    uint256 public constant MINIMUM_REWARD_RATE = 100; // (0.1% of the original value in basis points)
    uint256 public startDate;
    uint256 public dailyReward;

    mapping(address => Stake) public stakes;
    mapping(uint256 => address) public tokenToStaker;

    event Staked(address indexed user, uint256 tokenId, uint256 duration);
    event Unstaked(address indexed user, uint256 tokenId);
    event RewardClaimed(address indexed user, uint256 tokenId, uint256 reward);
    event DailyRewardChanged(uint256 newDailyReward);

    constructor(IERC721 _nftToken, IERC20 _rewardToken, uint256 _dailyReward) {
        nftToken = _nftToken;
        rewardToken = _rewardToken;
        dailyReward = _dailyReward;
        startDate = block.timestamp;
    }

    function stake(uint256 _tokenId, uint256 _days) external {
        require(_days >= MIN_STAKING_DAYS && _days <= MAX_STAKING_DAYS, "Invalid staking days");
        require(nftToken.ownerOf(_tokenId) == msg.sender, "You must own the token to stake it");

        nftToken.transferFrom(msg.sender, address(this), _tokenId);
        
        uint256 rewardRate = getDailyRewardRate();
        
        stakes[msg.sender] = Stake({
            tokenId: _tokenId,
            stakedAt: block.timestamp,
            stakesTill: block.timestamp + (_days * DAY_IN_SECONDS),
            currentRewardRate: rewardRate
        });
        
        tokenToStaker[_tokenId] = msg.sender;
        emit Staked(msg.sender, _tokenId, _days);
    }

    function withdraw(uint256 _tokenId) external nonReentrant {
        require(tokenToStaker[_tokenId] == msg.sender, "You are not the staker of this token");
        Stake memory userStake = stakes[msg.sender];
        require(userStake.tokenId == _tokenId, "Token not staked by user");
        
        nftToken.transferFrom(address(this), msg.sender, _tokenId);
        delete tokenToStaker[_tokenId];
        delete stakes[msg.sender];
        
        uint256 reward = calculateReward(userStake);
        require(rewardToken.transfer(msg.sender, reward), "Reward transfer failed");
        
        emit Unstaked(msg.sender, _tokenId);
        emit RewardClaimed(msg.sender, _tokenId, reward);
    }
    
    function checkStakedNFT(uint256 _tokenId) external view returns (Stake memory) {
        address staker = tokenToStaker[_tokenId];
        return stakes[staker];
    }

    function calculateReward(Stake memory userStake) internal view returns (uint256) {
        uint256 timeStaked = block.timestamp > userStake.stakesTill ? userStake.stakesTill : block.timestamp;
        uint256 stakingDuration = timeStaked - userStake.stakedAt;
        uint256 daysStaked = stakingDuration / DAY_IN_SECONDS;
        uint256 reward = daysStaked * userStake.currentRewardRate;
        
        if(block.timestamp < userStake.stakesTill) {
            // Apply penalty for early withdrawal
            reward = (reward * (100 - PENALTY_RATE)) / 100;
        }
        
        return reward;
    }
    
    function getDailyRewardRate() public view returns (uint256) {
        uint256 daysSinceStart = (block.timestamp - startDate) / DAY_IN_SECONDS;
        uint256 reduction = daysSinceStart * REWARD_REDUCTION_PER_DAY;
        
        uint256 dailyRate = dailyReward - (dailyReward * reduction / 10000);
        if (dailyRate < (dailyReward * MINIMUM_REWARD_RATE / 10000)) {
            dailyRate = dailyReward * MINIMUM_REWARD_RATE / 10000;
        }
        
        return dailyRate;
    }

    // Function to allow the owner to change the daily reward
    function setDailyReward(uint256 _newDailyReward) public onlyOwner {
        require(_newDailyReward > 0, "Daily reward must be greater than 0");
        dailyReward = _newDailyReward;
        emit DailyRewardChanged(_newDailyReward);
    }
    // Function to allow the owner to change the reward reduction rate
    function setRewardReduction(uint256 _newRewardReduction) public onlyOwner {
        require(_newRewardReduction >= 0 && _newRewardReduction <= 100, "Invalid reward reduction rate");
        // Update the reduction rate. We use require to ensure the reward reduction is within acceptable bounds to avoid unintentional high reduction rates
        REWARD_REDUCTION_PER_DAY = _newRewardReduction;
    }
    
}
//<MAIN/>
//<context:CODE/>