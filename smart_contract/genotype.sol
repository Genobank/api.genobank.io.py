// SPDX-License-Identifier: MIT
pragma solidity = 0.8.9;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC1155/ERC1155.sol";

contract GenoType is ERC1155{
    address owner;
    uint counter;
    struct Biosample {
        string name;
        address owner;
        uint tokenId;
        address laboratory;
        bool enable;
    }

    event Transferconsent (address _user, address _permittee, uint _tokenId);

    //Biosamples [] all_samples;
    mapping (address => Biosample) public biosamples;

    mapping (address => Biosample[]) public laboratoriesSamples;

    constructor (string memory _uri)ERC1155(_uri){
        owner = msg.sender;
    }

    function addGenotype(string memory _name, address _owner, address _permittee) public {
        require (msg.sender == owner, "YO CANNOT CALL THIS FUNCTION");
        require (isStringEmpty(biosamples[_owner].name), "You already have a registered genotype");
        require (!isStringEmpty(_name), "You file name is empty");
        counter++;
        Biosample memory newSample = Biosample(
            _name,
            _owner,
            counter,
            _permittee,
            true
            );
        biosamples[_owner] = newSample;
        laboratoriesSamples[_permittee].push(newSample);
        bytes memory bPermittee = toBytes(_permittee);
        bytes memory bOwner = toBytes(_owner);
        _mint(_owner, counter, 1, bPermittee);
        _mint(_permittee, counter, 1, bOwner);

        emit Transferconsent(_owner, _permittee, counter);
    }
    
    function getMyGenotype() public view returns (Biosample memory){
        return biosamples[msg.sender];
    }

    function getGenoetype (address _owner) public view returns (Biosample memory){
        return biosamples[_owner];
    }

    function getGebnotypesByPermittee(address _permittee) public view returns(Biosample[] memory){
        return laboratoriesSamples[_permittee];
    }

    function burnToken (address _owner, address _permittee) public {
        require (msg.sender == owner || isPermittee(msg.sender), "YO CANNOT CALL THIS FUNCTION");
        require (biosamples[_owner].enable, "You no longer have this object");
        uint _idtoken = biosamples[_owner].tokenId;
        
        
        _burn(_owner, _idtoken, 1);
        _burn(_permittee, _idtoken, 1);
        biosamples[_owner].enable = false;
    }


    function check_genotype_status(address _owner) public view returns(bool){
        return biosamples[_owner].enable;
    }

    function isPermittee(address _someone) public view returns(bool){
        bool ispermittee = false;
        if (laboratoriesSamples[_someone].length != 0){
            if (!isStringEmpty(laboratoriesSamples[_someone][0].name)){
                ispermittee = true;
            }
        }
        return ispermittee;
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

    
    function toBytes(address a) public pure returns (bytes memory b){
        assembly {
            let m := mload(0x40)
            a := and(a, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
            mstore(add(m, 20), xor(0x140000000000000000000000000000000000000000, a))
            mstore(0x40, add(m, 52))
            b := m
        }
    }
}