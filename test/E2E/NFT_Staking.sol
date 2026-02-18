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
//<Constructor/>

//<prompt:StakingFuncions>
// Please implement functions for nr 1,2,3,4 form the requirements
// {REQ}
//<prompt:StakingFuncions/>

//<StakingFuncions>
//<StakingFuncions/>

//<prompt:RewardCalc>
// Please implement the reward calculation view function and reward for the requirements:
// {REQ}
//<prompt:RewardCalc/>

//<RewardCalc>
//<RewardCalc/>