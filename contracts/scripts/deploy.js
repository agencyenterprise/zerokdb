async function main() {
  const TableSequences = await ethers.getContractFactory("TableSequences");
  const tableSequences = await TableSequences.deploy();
  await tableSequences.deployed();
  console.log("TableSequences deployed to:", tableSequences.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
