// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Import necessary Chainlink contracts
import {ConfirmedOwner} from "@chainlink/contracts@1.2.0/src/v0.8/shared/access/ConfirmedOwner.sol";
import {VRFV2PlusWrapperConsumerBase} from "@chainlink/contracts@1.2.0/src/v0.8/vrf/dev/VRFV2PlusWrapperConsumerBase.sol";
import {VRFV2PlusClient} from "@chainlink/contracts@1.2.0/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";

contract Lottery2 is VRFV2PlusWrapperConsumerBase, ConfirmedOwner {
    address[] public players;
    address public winner;
    bool public isLotteryActive = false;
    uint256 public maxPlayers = 100;

    mapping(address => uint256) public deposits;

    uint32 public callbackGasLimit = 100000;
    uint16 public requestConfirmations = 3;
    uint32 public numWords = 1;

    address public linkAddress = 0x779877A7B0D9E8603169DdbD7836e478b4624789;
    address public wrapperAddress = 0x195f15F2d49d693cE265b4fB0fdDbE15b1850Cc1;

    uint256 public lastRequestId;
    mapping(uint256 => bool) public requestFulfilled;

    event PlayerJoined(address indexed player);
    event LotteryWinner(address indexed winner);
    event LotteryStarted();
    event LotteryEnded();

    constructor()
        ConfirmedOwner(msg.sender)
        VRFV2PlusWrapperConsumerBase(wrapperAddress)
    {}

    function startLottery() public onlyOwner {
        require(!isLotteryActive, "Lottery is already active");
        isLotteryActive = true;
        emit LotteryStarted();
    }

    function joinLottery() public payable {
        require(isLotteryActive, "Lottery is not active");
        require(players.length < maxPlayers, "Maximum number of players reached");
        require(msg.value == 0.1 ether, "Participation fee is 0.1 ETH");

        players.push(msg.sender);
        deposits[msg.sender] = msg.value;

        emit PlayerJoined(msg.sender);
    }

    function finishLottery() public onlyOwner {
        require(isLotteryActive, "Lottery is not active");
        require(players.length > 1, "At least two players are required");

        bytes memory extraArgs = VRFV2PlusClient._argsToBytes(
            VRFV2PlusClient.ExtraArgsV1({nativePayment: true})
        );
        (lastRequestId, ) = requestRandomnessPayInNative(
            callbackGasLimit,
            requestConfirmations,
            numWords,
            extraArgs
        );
    }

    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        require(isLotteryActive, "Lottery is not active or already finalized");
        require(players.length > 0, "No players in the lottery");
        require(!requestFulfilled[_requestId], "Request already fulfilled");

        requestFulfilled[_requestId] = true;
        uint256 winnerIndex = _randomWords[0] % players.length;
        winner = players[winnerIndex];

        payable(winner).transfer(address(this).balance);
        emit LotteryWinner(winner);

        resetLotteryState();
        emit LotteryEnded();
    }

    function resetLotteryState() private {
        for (uint256 i = 0; i < players.length; i++) {
            deposits[players[i]] = 0;
        }
        players = new address[](0);
        isLotteryActive = false;
    }

    function cancelLottery() public onlyOwner {
        require(!isLotteryActive, "Cannot cancel while lottery is active");

        for (uint256 i = 0; i < players.length; i++) {
            payable(players[i]).transfer(deposits[players[i]]);
            deposits[players[i]] = 0;
        }
        resetLotteryState();
    }

    function getPlayers() public view returns (address[] memory) {
        return players;
    }

}