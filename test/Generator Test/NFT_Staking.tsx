//<import>NFT_Staking_2.sol<import/>

//<context:ComponentReqs>
//The comoponent should use these libraries:
// Typescript, React, Tailwind (where nescessary), Chakra UI, Ethers.js
// The component should have 3 tabs, one for staking, one for unstaking and one for claiming rewards
//<context:ComponentReqs/>


/* <prompt:Main>
I want to write a React component for interacting with my contract.
I will provide you the contract code and you will write the component code.
{CODE}
{ComponentReqs}
{REQ}
<prompt:Main/> */

//<context:COMPONENT_CODE>
// <Main>
import React, { useState } from 'react';
import { ethers } from 'ethers';
import {
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Input,
  Button,
  useToast,
} from '@chakra-ui/react';
import { NFT_Staking_2 } from './types/NFT_Staking_2'; // Assume you have your contract type here

interface StakingComponentProps {
  contractAddress: string;
  nftAddress: string;
  rewardTokenAddress: string;
  signer: ethers.Signer;
}

const StakingComponent: React.FC<StakingComponentProps> = ({
  contractAddress,
  nftAddress,
  rewardTokenAddress,
  signer,
}) => {
  const [tokenId, setTokenId] = useState('');
  const [days, setDays] = useState('');
  const toast = useToast();

  const contract = new ethers.Contract(contractAddress, NFT_Staking_2.abi, signer);

  const handleStake = async () => {
    try {
      const tx = await contract.stake(tokenId, days);
      await tx.wait();
      toast({ title: 'Staking successful', status: 'success' });
    } catch (error) {
      toast({ title: 'Staking failed', description: error.message, status: 'error' });
    }
  };

  const handleUnstake = async () => {
    try {
      const tx = await contract.withdraw(tokenId);
      await tx.wait();
      toast({ title: 'Unstaking successful', status: 'success' });
    } catch (error) {
      toast({ title: 'Unstaking failed', description: error.message, status: 'error' });
    }
  };

  const handleClaimRewards = async () => {
    // As there's no separate claim function in the contract, unstaking will also claim the rewards
    alert('To claim rewards, please unstake your NFT.');
  };

  return (
    <Tabs isFitted variant="enclosed">
      <TabList mb="1em">
        <Tab>Stake</Tab>
        <Tab>Unstake</Tab>
        <Tab>Claim Rewards</Tab>
      </TabList>
      <TabPanels>
        <TabPanel>
          <Input
            placeholder="NFT Token ID"
            value={tokenId}
            onChange={(e) => setTokenId(e.target.value)}
          />
          <Input
            placeholder="Number of days (7 - 300)"
            value={days}
            onChange={(e) => setDays(e.target.value)}
            mt={4}
          />
          <Button colorScheme="blue" onClick={handleStake} mt={4}>
            Stake NFT
          </Button>
        </TabPanel>
        <TabPanel>
          <Input
            placeholder="NFT Token ID"
            value={tokenId}
            onChange={(e) => setTokenId(e.target.value)}
          />
          <Button colorScheme="red" onClick={handleUnstake} mt={4}>
            Unstake NFT
          </Button>
        </TabPanel>
        <TabPanel>
          <Button colorScheme="green" onClick={handleClaimRewards} mt={4}>
            Claim Rewards
          </Button>
        </TabPanel>
      </TabPanels>
    </Tabs>
  );
};

export default StakingComponent;
// <Main/>
//<context:COMPONENT_CODE/>