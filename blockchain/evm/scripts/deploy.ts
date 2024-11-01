import hre from "hardhat";

async function main() {
  console.log("Deploying...");
  const TableSequence = await hre.ethers.getContractFactory("TableSequence");
  const tableSequence = await TableSequence.deploy();

  console.log("Contract deployed at:", await tableSequence.getAddress());
}

main().catch((error) => {
  console.log(error);
  process.exitCode = 1;
});
