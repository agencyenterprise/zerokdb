pragma solidity ^0.8.0;

contract TableSequences {
    struct Sequence {
        uint256 id;
        string tableName;
        string cid;
    }

    mapping(uint256 => Sequence) private sequences;
    uint256 private nextId = 1;

    event SequenceCreated(uint256 id, string tableName, string cid);
    event SequenceUpdated(uint256 id, string newCid);

    function createSequence(string memory tableName, string memory cid) public returns (uint256) {
        uint256 currentId = nextId;
        sequences[currentId] = Sequence(currentId, tableName, cid);
        nextId++;
        emit SequenceCreated(currentId, tableName, cid);
        return currentId;
    }

    function updateSequenceCid(uint256 id, string memory newCid) public {
        require(sequences[id].id != 0, "Sequence does not exist.");
        sequences[id].cid = newCid;
        emit SequenceUpdated(id, newCid);
    }

    function getSequenceById(uint256 id) public view returns (uint256, string memory, string memory) {
        require(sequences[id].id != 0, "Sequence does not exist.");
        Sequence memory sequence = sequences[id];
        return (sequence.id, sequence.tableName, sequence.cid);
    }
}
