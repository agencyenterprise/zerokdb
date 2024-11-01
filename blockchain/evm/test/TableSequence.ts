import {
  time,
  loadFixture,
} from "@nomicfoundation/hardhat-toolbox/network-helpers";
import { anyValue } from "@nomicfoundation/hardhat-chai-matchers/withArgs";
import { expect } from "chai";
import hre from "hardhat";

describe("TableSequence", function () {
  async function deployTableSequenceFixture() {
    // Contracts are deployed using the first signer/account by default
    const [owner, otherAccount] = await hre.ethers.getSigners();

    const TableSequence = await hre.ethers.getContractFactory("TableSequence");
    const tableSequence = await TableSequence.deploy();

    return { tableSequence, owner, otherAccount };
  }

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { tableSequence, owner } = await loadFixture(deployTableSequenceFixture);

      expect(await tableSequence.owner()).to.equal(owner.address);
    });
  });

  describe("createSequence", function () {
    it("Should create a new sequence", async function () {
      const { tableSequence } = await loadFixture(deployTableSequenceFixture);
      
      const tableName = "test_table";
      const cid = "QmTest123";

      await expect(tableSequence.createSequence(tableName, cid))
        .to.emit(tableSequence, "SequenceCreatedEvent")
        .withArgs(1, tableName, cid);

      const [id, name, storedCid] = await tableSequence.getSequenceByTableName(tableName);
      expect(id).to.equal(1);
      expect(name).to.equal(tableName);
      expect(storedCid).to.equal(cid);
    });

    it("Should revert when called by non-owner", async function () {
      const { tableSequence, otherAccount } = await loadFixture(deployTableSequenceFixture);
      
      await expect(
        tableSequence.connect(otherAccount).createSequence("test_table", "QmTest123")
      ).to.be.revertedWithCustomError(
        tableSequence,
        "OwnableUnauthorizedAccount"
      ).withArgs(otherAccount.address);
    });
  });

  describe("updateSequenceCid", function () {
    it("Should update sequence CID", async function () {
      const { tableSequence } = await loadFixture(deployTableSequenceFixture);
      
      // First create a sequence
      const tableName = "test_table";
      const initialCid = "QmTest123";
      await tableSequence.createSequence(tableName, initialCid);

      // Update the CID
      const newCid = "QmTest456";
      await expect(tableSequence.updateSequenceCid(1, newCid))
        .to.emit(tableSequence, "SequenceUpdatedEvent")
        .withArgs(1, newCid);

      // Verify the update
      const [id, name, storedCid] = await tableSequence.getSequenceByTableName(tableName);
      expect(storedCid).to.equal(newCid);
    });

    it("Should revert when updating non-existent sequence", async function () {
      const { tableSequence } = await loadFixture(deployTableSequenceFixture);
      
      await expect(
        tableSequence.updateSequenceCid(999, "QmTest123")
      ).to.be.revertedWithCustomError(
        tableSequence,
        "SequenceNotExist"
      );
    });

    it("Should revert when called by non-owner", async function () {
      const { tableSequence, otherAccount } = await loadFixture(deployTableSequenceFixture);
      
      await expect(
        tableSequence.connect(otherAccount).updateSequenceCid(1, "QmTest123")
      ).to.be.revertedWithCustomError(
        tableSequence,
        "OwnableUnauthorizedAccount"
      ).withArgs(otherAccount.address);
    });
  });

  describe("getSequenceByTableName", function () {
    it("Should return correct sequence data", async function () {
      const { tableSequence } = await loadFixture(deployTableSequenceFixture);
      
      // First create a sequence
      const tableName = "test_table";
      const cid = "QmTest123";
      await tableSequence.createSequence(tableName, cid);

      const [id, name, storedCid] = await tableSequence.getSequenceByTableName(tableName);
      expect(id).to.equal(1);
      expect(name).to.equal(tableName);
      expect(storedCid).to.equal(cid);
    });

    it("Should revert when sequence does not exist", async function () {
      const { tableSequence } = await loadFixture(deployTableSequenceFixture);
      
      await expect(
        tableSequence.getSequenceByTableName("non_existent_table")
      ).to.be.revertedWithCustomError(
        tableSequence,
        "SequenceNotExist"
      );
    });
  });
});
