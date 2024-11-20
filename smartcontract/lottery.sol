// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

// Importacja interfejsu Chainlink VRF
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase {
    address public owner;
    address[] public players;
    address public winner;

    // Chainlink VRF zmienne
    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;

    event PlayerJoined(address indexed player);
    event LotteryWinner(address indexed winner);

    // Konstruktor
    constructor(address vrfCoordinator, address linkToken, bytes32 _keyHash, uint256 _fee)
        VRFConsumerBase(vrfCoordinator, linkToken)
    {
        owner = msg.sender;
        keyHash = _keyHash;
        fee = _fee;
    }

    // Udział w loterii (płatność za uczestnictwo)
    function joinLottery() public payable {
        require(msg.value == 0.01 ether, "Participation fee is 0.01 ETH");
        players.push(msg.sender);
        emit PlayerJoined(msg.sender);
    }

    // Rozpoczęcie losowania - wywołanie Chainlink VRF
    function startLottery() public onlyOwner {
        require(players.length > 1, "At least two players are required");
        require(LINK.balanceOf(address(this)) >= fee, "Not enough LINK to request randomness");

        requestRandomness(keyHash, fee);
    }

    // Funkcja wywoływana przez Chainlink po wygenerowaniu losowej liczby
    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override {
        randomResult = randomness;
        uint256 winnerIndex = randomness % players.length;
        winner = players[winnerIndex];

        // Wypłata nagrody zwycięzcy
        payable(winner).transfer(address(this).balance);
        emit LotteryWinner(winner);

        // Resetowanie stanu loterii
        delete players;
    }

    // Pobieranie listy graczy
    function getPlayers() public view returns (address[] memory) {
        return players;
    }

    // Modyfikator tylko dla właściciela
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
}