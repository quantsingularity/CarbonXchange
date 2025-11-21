const CarbonCreditToken = artifacts.require("CarbonCreditToken");
const Marketplace = artifacts.require("Marketplace");

module.exports = async function (deployer) {
  await deployer.deploy(CarbonCreditToken);
  const token = await CarbonCreditToken.deployed();
  await deployer.deploy(Marketplace, token.address);
};
