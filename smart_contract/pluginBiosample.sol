// SPDX-License-Identifier: GPL-3.0
pragma solidity = 0.8.9;

import "./Genotype.sol";
contract plugin{
    address payable address_genotype;

    GenoType genotipo; 

    constructor (address payable _genotype,address _smaddress){
        address_genotype = _genotype;
        genotipo = GenoType(_smaddress);
    }

    function getGebnotypesByPermittee(address permittee) public view returns(GenoType.Biosample memory){
        return genotipo.biosamples[permittee];
    }
}