// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

import "@openzeppelin/contracts/access/Ownable.sol";

contract TableSequence is Ownable {
    error SequenceNotExist();

    struct Sequence {
        uint256 id;
        string tableName;
        string cid;
    }

    mapping(uint256 => Sequence) private sequences;
    uint256 private nextId;

    event SequenceCreatedEvent(
        uint256 indexed id,
        string tableName,
        string cid
    );

    event SequenceUpdatedEvent(
        uint256 indexed id,
        string newCid
    );

    constructor() Ownable(msg.sender) {
        nextId = 1;
    }

    function createSequence(
        string calldata tableName,
        string calldata cid
    ) external onlyOwner {        
        uint256 id = nextId;

        sequences[id] = Sequence({
            id: id,
            tableName: tableName,
            cid: cid
        });

        nextId = id + 1;

        emit SequenceCreatedEvent(id, tableName, cid);
    }

    function updateSequenceCid(
        uint256 id,
        string calldata newCid
    ) external onlyOwner {
        if (sequences[id].id == 0) revert SequenceNotExist();

        sequences[id].cid = newCid;
        
        emit SequenceUpdatedEvent(id, newCid);
    }

    function getSequenceByTableName(string calldata tableName) 
        external 
        view 
        returns (uint256, string memory, string memory) 
    {
        for (uint256 i = 1; i < nextId; i++) {
            if (sequences[i].id != 0 && 
                keccak256(bytes(sequences[i].tableName)) == keccak256(bytes(tableName))) {
                return (
                    sequences[i].id,
                    sequences[i].tableName,
                    sequences[i].cid
                );
            }
        }

        revert SequenceNotExist();
    }
}
