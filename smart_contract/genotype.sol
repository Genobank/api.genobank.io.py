// SPDX-License-Identifier: GPL-3.0
pragma solidity = 0.8.9;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC1155/ERC1155.sol";

contract GenoType is ERC1155{
    address owner;
    uint counter;
    struct Biosample {
        string name;
        address owner;
        address laboratory;
        bool enable;
    }

    //Biosamples [] all_samples;
    mapping (address => Biosample) public biosamples;

    mapping (address => Biosample[]) public laboratoriesSamples;

    constructor (string memory _uri)ERC1155(_uri){
        owner = msg.sender;
    }

    function addGenotype(string memory _name, address _owner, address permittee) public {
        require (msg.sender == owner, "YO CANNOT CALL THIS FUNCTION");
        require (isStringEmpty(biosamples[_owner].name), "You already have a registered genotype");
        require (!isStringEmpty(_name), "You file name is empty");
        counter++;
        Biosample memory newSample = Biosample(
            _name,
            msg.sender,
            permittee,
            true
            );
        biosamples[_owner] = newSample;
        laboratoriesSamples[permittee].push(newSample);
        _mint(_owner, counter, 1, "");
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

    function disableGenotype(address _permittee, address _owner) public {
        require (msg.sender == owner || isPermittee(msg.sender), "YO CANNOT CALL THIS FUNCTION");
        if(msg.sender == owner){
            biosamples[_permittee].enable = false;
        }else{
            biosamples[msg.sender].enable = false;
        }
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
}
