// SPDX-License-Identifier: GPL-3.0
pragma solidity = 0.8.9;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC1155/ERC1155.sol";

contract GenoType is ERC1155{
    address owner;
    uint counter;
    struct Biosample{
        string name;
        address owner;
    }
    mapping (address => Biosample) biosamples;

    constructor (string memory _uri)ERC1155(_uri){
        owner = msg.sender;
    }

    function addGenoetype(string memory _name, address _owner) public {
        require (msg.sender == owner, "YO CANNOT CALL THIS FUNCTION");
        counter++;
        Biosample memory newSample = Biosample(_name, msg.sender);
        biosamples[_owner] = newSample;
        _mint(_owner, counter, 1, "");
    }
    

    function getMyGenotype() public view returns (Biosample memory){
        return biosamples[msg.sender];
    }

    function getGenoetype (address _owner) public view returns (Biosample memory){
        return biosamples[_owner];
    }

    
}