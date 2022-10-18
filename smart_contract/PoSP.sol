// SPDX-License-Identifier: MIT
pragma solidity = 0.8.7;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Counters.sol";

contract PoSP is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    address private owner;
    
    struct PoSPStruct {
        uint id;
        address user;
        address lab;
        string title;
        string message;
        string date;
        string tokenName;
        string symbol;
        address smartcontract;
    }

    event createPoSP (
        address _user,
        address _lab,
        uint _id
    );

    mapping (address => mapping(address => PoSPStruct)) PoSPList;

    constructor() ERC721("Proof Of Stack", "PoSP") {
        owner = msg.sender;
        _tokenIds.increment();
    }

    function mintPOSP(
        PoSPStruct memory PoSPToken
        ) public {
        require(
            msg.sender == owner,
            "You cannot cal this function"
        );
        require(
            PoSPList[PoSPToken.lab][PoSPToken.user].id == 0,
            "Yo have now a token participation"
        );
        uint256 newItemId = _tokenIds.current();
        PoSPToken.id = newItemId;
        PoSPToken.tokenName = name();
        PoSPToken.symbol = symbol();
        PoSPToken.smartcontract = address(this);
        PoSPList[PoSPToken.lab][PoSPToken.user] = PoSPToken;
        _mint(PoSPToken.user, newItemId);
        _tokenIds.increment();
    }

    function getPoSP(address _lab, address _user) public view returns(PoSPStruct memory){
        return PoSPList[_lab][_user];
    }

}