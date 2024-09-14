let expect;

before(async () => {
  const chai = await import("chai");
  const chaiAsPromised = await import("chai-as-promised");
  const chaiEthers = await import("chai-ethers");
  chai.use(chaiAsPromised.default);
  chai.use(chaiEthers.default);
  expect = chai.expect;
});

describe("TableSequences", function () {
  let TableSequences;
  let tableSequences;
  let owner;

  beforeEach(async function () {
    TableSequences = await ethers.getContractFactory("TableSequences");
    [owner] = await ethers.getSigners();
    tableSequences = await TableSequences.deploy();
    await tableSequences.deployed();
  });

  it("should create a new sequence", async function () {
    const tx = await tableSequences.createSequence("TestTable", "CID123");
    const receipt = await tx.wait();

    expect(receipt.events.length).to.equal(1);
    const event = receipt.events[0];
    expect(event.event).to.equal("SequenceCreated");
    console.log(event.args.id.toNumber())
    expect(event.args.id.toNumber()).to.equal(1);
    expect(event.args.tableName).to.equal("TestTable");
    expect(event.args.cid).to.equal("CID123");

    const sequence = await tableSequences.getSequenceById(1);
    expect(sequence[0].toNumber()).to.equal(1);
    expect(sequence[1]).to.equal("TestTable");
    expect(sequence[2]).to.equal("CID123");
  });

  it("should update the CID of an existing sequence", async function () {
    await tableSequences.createSequence("TestTable", "CID123");
    const tx = await tableSequences.updateSequenceCid(1, "CID456");
    const receipt = await tx.wait();

    expect(receipt.events.length).to.equal(1);
    const event = receipt.events[0];
    expect(event.event).to.equal("SequenceUpdated");
    expect(event.args.id.toNumber()).to.equal(1);
    expect(event.args.newCid).to.equal("CID456");

    const sequence = await tableSequences.getSequenceById(1);
    expect(sequence[2]).to.equal("CID456");
  });

  it("should revert when updating a non-existent sequence", async function () {
    await expect(
      tableSequences.updateSequenceCid(999, "CID456")
    ).to.be.revertedWith("Sequence does not exist.");
  });

  it("should revert when getting a non-existent sequence", async function () {
    await expect(tableSequences.getSequenceById(999)).to.be.revertedWith(
      "Sequence does not exist."
    );
  });
});
