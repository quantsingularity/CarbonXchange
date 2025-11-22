const { expect } = require('chai');
const { ethers } = require('hardhat');

// Helper function to convert Ether to Wei
const toWei = (value) => ethers.parseEther(value.toString());

describe('CarbonCreditToken', function () {
    let CarbonCreditToken;
    let carbonCreditToken;
    let owner;
    let addr1;
    let addr2;
    let addrs;

    // Deploy the contract before each test
    beforeEach(async function () {
        // Get the signers (accounts)
        [owner, addr1, addr2, ...addrs] = await ethers.getSigners();

        // Deploy the CarbonCreditToken contract
        CarbonCreditToken = await ethers.getContractFactory('CarbonCreditToken');
        carbonCreditToken = await CarbonCreditToken.deploy(toWei(1000000)); // Initial supply of 1,000,000 tokens
        await carbonCreditToken.waitForDeployment();
    });

    describe('Deployment', function () {
        it('Should set the correct name and symbol', async function () {
            expect(await carbonCreditToken.name()).to.equal('Carbon Credit Token');
            expect(await carbonCreditToken.symbol()).to.equal('CCT');
        });

        it('Should assign the total supply to the owner', async function () {
            const ownerBalance = await carbonCreditToken.balanceOf(owner.address);
            expect(await carbonCreditToken.totalSupply()).to.equal(ownerBalance);
            expect(ownerBalance).to.equal(toWei(1000000));
        });
    });

    describe('Transactions', function () {
        it('Should transfer tokens between accounts', async function () {
            // Transfer 50 tokens from owner to addr1
            await expect(carbonCreditToken.transfer(addr1.address, toWei(50)))
                .to.emit(carbonCreditToken, 'Transfer')
                .withArgs(owner.address, addr1.address, toWei(50));

            // Check balances
            const ownerBalance = await carbonCreditToken.balanceOf(owner.address);
            const addr1Balance = await carbonCreditToken.balanceOf(addr1.address);

            expect(ownerBalance).to.equal(toWei(999950));
            expect(addr1Balance).to.equal(toWei(50));
        });

        it('Should fail if sender doesn’t have enough tokens', async function () {
            const initialOwnerBalance = await carbonCreditToken.balanceOf(owner.address);

            // Try to send more than the owner's balance from addr1 (who has 0)
            await expect(
                carbonCreditToken.connect(addr1).transfer(owner.address, toWei(1)),
            ).to.be.revertedWithCustomError(carbonCreditToken, 'ERC20InsufficientBalance');

            // Owner's balance should not change
            expect(await carbonCreditToken.balanceOf(owner.address)).to.equal(initialOwnerBalance);
        });
    });

    describe('Minting and Burning (Carbon Credit Specific)', function () {
        it('Should allow the owner to mint new tokens', async function () {
            const mintAmount = toWei(100);
            const initialSupply = await carbonCreditToken.totalSupply();

            await expect(carbonCreditToken.mint(addr1.address, mintAmount))
                .to.emit(carbonCreditToken, 'Transfer')
                .withArgs(ethers.ZeroAddress, addr1.address, mintAmount);

            // Check new supply and balance
            expect(await carbonCreditToken.totalSupply()).to.equal(initialSupply + mintAmount);
            expect(await carbonCreditToken.balanceOf(addr1.address)).to.equal(mintAmount);
        });

        it('Should prevent non-owners from minting tokens', async function () {
            const mintAmount = toWei(100);
            // Assuming the contract uses Ownable or similar access control
            await expect(
                carbonCreditToken.connect(addr1).mint(addr1.address, mintAmount),
            ).to.be.revertedWith('Ownable: caller is not the owner');
        });

        it('Should allow burning of tokens', async function () {
            // First, transfer tokens to addr1
            await carbonCreditToken.transfer(addr1.address, toWei(50));
            const initialBalance = await carbonCreditToken.balanceOf(addr1.address);
            const burnAmount = toWei(10);

            // Burn tokens from addr1's account
            await expect(carbonCreditToken.connect(addr1).burn(burnAmount))
                .to.emit(carbonCreditToken, 'Transfer')
                .withArgs(addr1.address, ethers.ZeroAddress, burnAmount);

            // Check balance and total supply
            expect(await carbonCreditToken.balanceOf(addr1.address)).to.equal(
                initialBalance - burnAmount,
            );
            expect(await carbonCreditToken.totalSupply()).to.equal(toWei(1000000) - burnAmount);
        });
    });
});
