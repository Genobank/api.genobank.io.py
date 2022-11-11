// SPDX-License-Identifier: MIT
pragma solidity = 0.8.7;

import "./.deps/github/OpenZeppelin/openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "./.deps/github/OpenZeppelin/openzeppelin-contracts/contracts/utils/Counters.sol";
import "./.deps/github/OpenZeppelin/openzeppelin-contracts/contracts/access/Ownable.sol";


contract PoSP is ERC721URIStorage, Ownable{
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    
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
    mapping (address => PoSPStruct[]) labTokens;

    constructor(string memory name_, string memory symbol_) ERC721(name_, symbol_) {
    }

    function mintPOSP(
        PoSPStruct memory PoSPToken
        ) public onlyOwner{
        require(
            PoSPList[PoSPToken.lab][PoSPToken.user].id == 0,
            "Yo have now a token participation"
        );
        _tokenIds.increment();
        uint256 pospId = _tokenIds.current();
        PoSPToken.id = pospId;
        PoSPToken.tokenName = name();
        PoSPToken.symbol = symbol();
        PoSPToken.smartcontract = address(this);
        PoSPList[PoSPToken.lab][PoSPToken.user] = PoSPToken;
        labTokens[PoSPToken.lab].push(PoSPToken);
        _mint(PoSPToken.user, pospId);
        emit createPoSP(PoSPToken.user, PoSPToken.lab, pospId);
    }

    function getPoSP(address _lab, address _user) public view returns(PoSPStruct memory){
        return PoSPList[_lab][_user];
    }

    function getCurrentId()public view returns(uint256){
        return _tokenIds.current();
    }

    function getPosPlist(address _lab) public view returns(PoSPStruct[] memory){
        return labTokens[_lab];
    }
}