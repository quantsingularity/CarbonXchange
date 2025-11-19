const Marketplace = artifacts.require("Marketplace");

contract("Marketplace", (accounts) => {
  let marketplace;
  const [owner, buyer] = accounts;

  before(async () => {
    marketplace = await Marketplace.deployed();
  });

  it("should create new listings", async () => {
    await marketplace.createListing(100, 10, { from: owner });
    const listing = await marketplace.listings(0);
    assert.equal(listing.amount, 100, "Listing creation failed");
  });
});
