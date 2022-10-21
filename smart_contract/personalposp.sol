// SPDX-License-Identifier: MIT
pragma solidity = 0.8.7;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

//hay que modificar el metodo mint para 
contract ERC721URIStorageTokenFactory {
    function createToken(string memory _name, string memory _symbol) public returns (ERC721) {
        return new ERC721(_name, _symbol);
    }

    function _mint(address SMposp, address _lab, address _user)public {
        //necesitará un require y un owner logicamente
        ERC721 contract_address =  ERC721(SMposp);
        contract_address._mint(_user, 1);
    }
}