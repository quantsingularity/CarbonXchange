const { expect } = require("chai");
const { ethers } = require("hardhat");

// Helper function to convert Ether to Wei
const toWei = (value) => ethers.parseEther(value.toString());
const fromWei = (value) => ethers.formatEther(value);

describe("CarbonCreditMarketplace", function () {
  let CarbonCreditToken;
  let carbonCreditToken;
  let CarbonCreditMarketplace;
  let marketplace;
  let owner;
  let seller;
  let buyer;
  let addrs;

  const LISTING_FEE = toWei(0.01); // Example listing fee

  // Deploy contracts and set up initial state
  beforeEach(async function () {
    [owner, seller, buyer, ...addrs] = await ethers.getSigners();

    // 1. Deploy CarbonCreditToken
    CarbonCreditToken = await ethers.getContractFactory("CarbonCreditToken");
    carbonCreditToken = await CarbonCreditToken.deploy(toWei(1000000));
    await carbonCreditToken.waitForDeployment();

    // 2. Deploy CarbonCreditMarketplace
    CarbonCreditMarketplace = await ethers.getContractFactory(
      "CarbonCreditMarketplace",
    );
    marketplace = await CarbonCreditMarketplace.deploy(
      await carbonCreditToken.getAddress(),
      LISTING_FEE,
    );
    await marketplace.waitForDeployment();

    // 3. Transfer some CCT to the seller for listing
    await carbonCreditToken.transfer(seller.address, toWei(1000));

    // 4. Approve the Marketplace contract to spend seller's CCT
    await carbonCreditToken
      .connect(seller)
      .approve(await marketplace.getAddress(), toWei(1000));
  });

  describe("Deployment and Configuration", function () {
    it("Should set the correct token address", async function () {
      expect(await marketplace.carbonCreditToken()).to.equal(
        await carbonCreditToken.getAddress(),
      );
    });

    it("Should set the correct listing fee", async function () {
      expect(await marketplace.listingFee()).to.equal(LISTING_FEE);
    });
  });

  describe("Listing Credits", function () {
    const creditAmount = toWei(100);
    const pricePerCredit = toWei(1); // 1 ETH per CCT

    it("Should allow a seller to list credits", async function () {
      const initialOwnerEthBalance = await ethers.provider.getBalance(
        owner.address,
      );

      // List credits, sending the listing fee in ETH
      await expect(
        marketplace
          .connect(seller)
          .listCredits(creditAmount, pricePerCredit, { value: LISTING_FEE }),
      )
        .to.emit(marketplace, "CreditListed")
        .withArgs(seller.address, 1, creditAmount, pricePerCredit);

      // Check that the listing fee was paid to the owner (simplified check)
      const finalOwnerEthBalance = await ethers.provider.getBalance(
        owner.address,
      );
      expect(finalOwnerEthBalance).to.be.closeTo(
        initialOwnerEthBalance + LISTING_FEE,
        toWei(0.001),
      );

      // Check that the CCT were transferred to the marketplace
      expect(
        await carbonCreditToken.balanceOf(await marketplace.getAddress()),
      ).to.equal(creditAmount);

      // Check the listing details
      const listing = await marketplace.listings(1);
      expect(listing.seller).to.equal(seller.address);
      expect(listing.amount).to.equal(creditAmount);
      expect(listing.pricePerCredit).to.equal(pricePerCredit);
      expect(listing.active).to.be.true;
    });

    it("Should fail if the listing fee is not paid", async function () {
      await expect(
        marketplace
          .connect(seller)
          .listCredits(creditAmount, pricePerCredit, { value: toWei(0) }),
      ).to.be.revertedWith("Marketplace: Listing fee not paid");
    });

    it("Should fail if the seller has not approved the marketplace", async function () {
      // Reset approval to 0
      await carbonCreditToken
        .connect(seller)
        .approve(await marketplace.getAddress(), toWei(0));

      await expect(
        marketplace
          .connect(seller)
          .listCredits(creditAmount, pricePerCredit, { value: LISTING_FEE }),
      ).to.be.revertedWith("ERC20: insufficient allowance");
    });
  });

  describe("Buying Credits", function () {
    const creditAmount = toWei(100);
    const pricePerCredit = toWei(1); // 1 ETH per CCT
    const totalPrice = toWei(100); // 100 CCT * 1 ETH/CCT

    beforeEach(async function () {
      // Seller lists credits
      await marketplace
        .connect(seller)
        .listCredits(creditAmount, pricePerCredit, { value: LISTING_FEE });
    });

    it("Should allow a buyer to purchase credits", async function () {
      const listingId = 1;
      const purchaseAmount = toWei(50);
      const purchasePrice = toWei(50); // 50 CCT * 1 ETH/CCT

      const initialSellerEthBalance = await ethers.provider.getBalance(
        seller.address,
      );
      const initialBuyerCCTBalance = await carbonCreditToken.balanceOf(
        buyer.address,
      );

      // Buyer purchases credits, sending ETH
      await expect(
        marketplace
          .connect(buyer)
          .buyCredits(listingId, purchaseAmount, { value: purchasePrice }),
      )
        .to.emit(marketplace, "CreditSold")
        .withArgs(listingId, buyer.address, purchaseAmount, purchasePrice);

      // Check CCT transfer to buyer
      expect(await carbonCreditToken.balanceOf(buyer.address)).to.equal(
        initialBuyerCCTBalance + purchaseAmount,
      );

      // Check ETH transfer to seller (minus gas)
      const finalSellerEthBalance = await ethers.provider.getBalance(
        seller.address,
      );
      expect(finalSellerEthBalance).to.be.closeTo(
        initialSellerEthBalance + purchasePrice,
        toWei(0.001),
      );

      // Check remaining listing amount
      const listing = await marketplace.listings(listingId);
      expect(listing.amount).to.equal(creditAmount - purchaseAmount);
      expect(listing.active).to.be.true;
    });

    it("Should close the listing if the full amount is purchased", async function () {
      const listingId = 1;
      const purchaseAmount = creditAmount;

      await marketplace
        .connect(buyer)
        .buyCredits(listingId, purchaseAmount, { value: totalPrice });

      const listing = await marketplace.listings(listingId);
      expect(listing.amount).to.equal(toWei(0));
      expect(listing.active).to.be.false;
    });

    it("Should fail if the sent ETH is insufficient", async function () {
      const listingId = 1;
      const purchaseAmount = toWei(10);
      const insufficientPrice = toWei(9); // Should be 10 ETH

      await expect(
        marketplace
          .connect(buyer)
          .buyCredits(listingId, purchaseAmount, { value: insufficientPrice }),
      ).to.be.revertedWith("Marketplace: Insufficient ETH sent");
    });

    it("Should fail if the purchase amount exceeds the listing amount", async function () {
      const listingId = 1;
      const excessiveAmount = toWei(101);
      const excessivePrice = toWei(101);

      await expect(
        marketplace
          .connect(buyer)
          .buyCredits(listingId, excessiveAmount, { value: excessivePrice }),
      ).to.be.revertedWith("Marketplace: Purchase amount exceeds listing amount");
    });
  });

  describe("Cancelling Listings", function () {
    const creditAmount = toWei(100);
    const pricePerCredit = toWei(1);

    beforeEach(async function () {
      // Seller lists credits
      await marketplace
        .connect(seller)
        .listCredits(creditAmount, pricePerCredit, { value: LISTING_FEE });
    });

    it("Should allow the seller to cancel their own listing", async function () {
      const listingId = 1;
      const initialMarketplaceCCTBalance = await carbonCreditToken.balanceOf(
        await marketplace.getAddress(),
      );
      const initialSellerCCTBalance = await carbonCreditToken.balanceOf(
        seller.address,
      );

      await expect(marketplace.connect(seller).cancelListing(listingId))
        .to.emit(marketplace, "CreditCancelled")
        .withArgs(listingId);

      // Check that the CCT were returned to the seller
      expect(await carbonCreditToken.balanceOf(seller.address)).to.equal(
        initialSellerCCTBalance + creditAmount,
      );
      expect(
        await carbonCreditToken.balanceOf(await marketplace.getAddress()),
      ).to.equal(initialMarketplaceCCTBalance - creditAmount);

      // Check that the listing is marked inactive
      const listing = await marketplace.listings(listingId);
      expect(listing.active).to.be.false;
    });

    it("Should fail if a non-seller tries to cancel the listing", async function () {
      const listingId = 1;
      await expect(
        marketplace.connect(buyer).cancelListing(listingId),
      ).to.be.revertedWith("Marketplace: Only seller can cancel listing");
    });

    it("Should fail if the listing is already inactive", async function () {
      const listingId = 1;
      // Cancel once
      await marketplace.connect(seller).cancelListing(listingId);
      // Try to cancel again
      await expect(
        marketplace.connect(seller).cancelListing(listingId),
      ).to.be.revertedWith("Marketplace: Listing is not active");
    });
  });
});
