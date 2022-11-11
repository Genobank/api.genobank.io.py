// SPDX-License-Identifier: MIT
pragma solidity = 0.8.7;
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Counters.sol";
// import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";

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
        _tokenIds.increment();
    }

    function mintPOSP(
        PoSPStruct memory PoSPToken
        ) public onlyOwner{
        require(
            PoSPList[PoSPToken.lab][PoSPToken.user].id == 0,
            "Yo have now a token participation"
        );
        uint256 pospId = _tokenIds.current();
        PoSPToken.id = pospId;
        PoSPToken.tokenName = name();
        PoSPToken.symbol = symbol();
        PoSPToken.smartcontract = address(this);
        PoSPList[PoSPToken.lab][PoSPToken.user] = PoSPToken;
        labTokens[PoSPToken.lab].push(PoSPToken);
        _mint(PoSPToken.user, pospId);
        _tokenIds.increment();
        emit createPoSP(PoSPToken.user, PoSPToken.lab, pospId);
    }

    function getPoSP(address _lab, address _user) public view returns(PoSPStruct memory){
        return PoSPList[_lab][_user];
    }

    function getPosPlist(address _lab) public view returns(PoSPStruct[] memory){
        return labTokens[_lab];
    }
}

contract POSPTokenFactory is Ownable{
    struct Token{
        string name;
        string symbol;
        address lab_emmiter;
        PoSP sm_address;
    }
    event tokenCreationEvent(
        address emmiter_address,
        PoSP sm_address
    );

    mapping (address => Token) contracts;
    mapping (address => PoSP[]) userTokens;
    
    function createToken(string memory _name, string memory _symbol, address _lab) public onlyOwner returns (PoSP) {
        if (isStringEmpty(_name)){
            _name = "Proof OF Stake Protocol";  
        }
        if (isStringEmpty(_symbol)){
            _symbol = "POSP";
        }
        PoSP sm_posp_token = new PoSP(_name, _symbol);

        Token memory tknstruct = Token({
            name:_name,
            symbol:_symbol,
            lab_emmiter:_lab,
            sm_address: sm_posp_token
        });

        contracts[_lab] = tknstruct;
        emit tokenCreationEvent(_lab, sm_posp_token);
        return sm_posp_token;
    }

    function mintInstancePOSP(PoSP _token_contract_address, PoSP.PoSPStruct memory PoSPToken)public onlyOwner{
        _token_contract_address.mintPOSP(PoSPToken);
        userTokens[PoSPToken.user].push(_token_contract_address);
    }

    function getTokensByUsers(address _user) public view returns(PoSP[] memory _allUserTokens){
        return userTokens[_user];
    }

    function transferInstancePOSPOwner(address _newSMOwner, PoSP _token_contract_address ) public onlyOwner{
        _token_contract_address.transferOwnership(_newSMOwner);
    }
    //this name is wromg we are getting the sm address, and no the laboratiory asdres
    //suggested name getTokenSmartContractAddress()
    function getTokenSmartContractAddress(address _lab) public view returns(Token memory){
        return contracts[_lab];
    }

    function isStringEmpty(string memory value) internal pure returns(bool){
        bytes1 space = ' ';
        bytes memory str = bytes(value);
        bool _isEmpty = true;
        for (uint i=0; i<str.length; i++){
            if(str[i] != space){
                _isEmpty = false;
            }
        }
        return _isEmpty;
    }
}