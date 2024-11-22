// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

// Importacja interfejsu Chainlink VRF
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase {
    address public owner;
    address[] public players;
    address public winner;
    bool public isLotteryActive = false;
    uint256 public maxPlayers = 100;

    // Mapa graczy, którzy już uczestniczą
    mapping(address => bool) public hasParticipated;
    mapping(address => uint256) public deposits;

    // Chainlink VRF zmienne
    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;

    // Lock do ochrony przed reentrancy
    bool private locked = false;

    // Wydarzenia
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

    // Udział w loterii
    function joinLottery() public payable {
        require(!isLotteryActive, "Cannot join while lottery is active");
        require(players.length < maxPlayers, "Maximum number of players reached");
        require(!hasParticipated[msg.sender], "You already joined the lottery with this address");
        require(msg.value == 0.01 ether, "Participation fee is 0.01 ETH");

        players.push(msg.sender);
        hasParticipated[msg.sender] = true;
        deposits[msg.sender] = msg.value;

        emit PlayerJoined(msg.sender);
    }

    // Rozpoczęcie losowania
    function startLottery() public onlyOwner {
        require(!isLotteryActive, "Lottery is already active");
        require(players.length > 1, "At least two players are required");
        require(LINK.balanceOf(address(this)) >= fee, "Not enough LINK to request randomness");

        isLotteryActive = true;
        requestRandomness(keyHash, fee);
    }

    // Chainlink VRF callback
    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override noReentrant {
        require(isLotteryActive, "Lottery is not active or already finalized");
        require(players.length > 0, "No players in the lottery");

        randomResult = randomness;
        uint256 winnerIndex = randomness % players.length;
        winner = players[winnerIndex];

        // Wypłata nagrody
        payable(winner).transfer(address(this).balance);
        emit LotteryWinner(winner);

        // Resetowanie stanu loterii
        resetLotteryState();
    }

    // Resetowanie stanu loterii
    function resetLotteryState() private {
        for (uint256 i = 0; i < players.length; i++) {
            hasParticipated[players[i]] = false;
            deposits[players[i]] = 0;
        }
        players = new address ;
        isLotteryActive = false;
    }

    // Anulowanie loterii i zwrot wpłat
    function cancelLottery() public onlyOwner noReentrant {
        require(!isLotteryActive, "Cannot cancel while lottery is active");

        for (uint256 i = 0; i < players.length; i++) {
            payable(players[i]).transfer(deposits[players[i]]);
            deposits[players[i]] = 0;
        }
        resetLotteryState();
    }

    // Dodanie LINK do kontraktu
    function fundWithLink(uint256 amount) public onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        require(LINK.transferFrom(msg.sender, address(this), amount), "LINK transfer failed");
    }

    // Pobieranie listy graczy
    function getPlayers() public view returns (address[] memory) {
        return players;
    }

    // Awaryjne resetowanie loterii
    function emergencyReset() public onlyOwner {
        require(isLotteryActive, "Lottery is not active");
        resetLotteryState();
    }

    // Modyfikator tylko dla właściciela
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    // Modyfikator zapobiegający reentrancy
    modifier noReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
}