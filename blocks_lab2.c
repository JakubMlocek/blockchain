#include <stdint.h>
#include <string.h>
#include <stdio.h>

struct block {
    uint16_t currentBlockHash;
    uint16_t prevBlockHash;
    uint16_t nonce;
    uint16_t blockNumber;
    char contentName[256];
} BLOCKS[1000];

int numberOfBlocks = 0;

void addBlock(char *dane){
    if(numberOfBlocks == 0)
    {
        BLOCKS[0].prevBlockHash = 0;
    }
    else
    {
        BLOCKS[numberOfBlocks].prevBlockHash = BLOCKS[numberOfBlocks - 1].currentBlockHash;
        BLOCKS[numberOfBlocks].blockNumber = numberOfBlocks + 1;
        strncpy(BLOCKS[numberOfBlocks].contentName,dane,256);
    }
    
    uint16_t hash=0, possibleValue = 0, *prevBlockHashPointer;
    
    //in that case hash is a sum of bajts in given block
    while ((hash & 15) != 15) 
    {
        hash = 0;
        BLOCKS[numberOfBlocks].nonce = possibleValue;
        prevBlockHashPointer = &BLOCKS[numberOfBlocks].prevBlockHash;
        for(int i = 0; i < 1 + 1 + 1 + 128; i++){ //consist of 128 2bajts for contentName and 1 + 1 + 1 for uint16_t piecies
            hash += *prevBlockHashPointer;
            prevBlockHashPointer++;
        }
        possibleValue++;
    }
    BLOCKS[numberOfBlocks].currentBlockHash = hash;
    numberOfBlocks++;
}

int main(){
    addBlock("1234");
    addBlock("labylaby");
    addBlock("opowiedzmiosobie");
    addBlock("aaaaaaaaaa");

    // Display the content and parameters for each created block
    for (int i = 0; i < 4; i++) {
        printf("Block %d:\n", BLOCKS[i].blockNumber);
        printf("  Content Name: %s\n", BLOCKS[i].contentName);
        printf("  Previous Hash: %u\n", BLOCKS[i].prevBlockHash);
        printf("  Current Hash: %u\n", BLOCKS[i].currentBlockHash);
        printf("  Nonce: %u\n\n", BLOCKS[i].nonce);
    }
    return 0;
}