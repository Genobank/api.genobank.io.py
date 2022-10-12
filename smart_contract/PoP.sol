// SPDX-License-Identifier: MIT
pragma solidity = 0.8.7;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Counters.sol";


contract PoP is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    address private owner;
    
    struct PoPStruct {
        uint id;
        address user;
        address lab;
        string title;
        string message;
        string date;
    }
    event createPoP (address _user, address _lab, uint _id);
    mapping (address => mapping(address => PoPStruct)) PoPList;

    constructor() ERC721("Proof Of Participation", "PoP") {
        owner = msg.sender;
        _tokenIds.increment();
    }

    function mintParticipation(PoPStruct memory PoPToken) public {
        require(msg.sender == owner, "You cannot cal this function");
        require(PoPList[PoPToken.lab][PoPToken.user].id == 0, "Yo have now a token participation");
        uint256 newItemId = _tokenIds.current();
        PoPToken.id = newItemId;
        PoPList[PoPToken.lab][PoPToken.user] = PoPToken;
        _mint(PoPToken.user, newItemId);
        _tokenIds.increment();
    }

    function getPoP(address _lab, address _user) public view returns(PoPStruct memory){
        return PoPList[_lab][_user];
    }
}