const gameBoard = document.getElementById('gameBoard');
const boardSize = 15;
let board = Array.from({ length: boardSize }, () => Array(boardSize).fill(null));
let currentPlayer = 'black';

function createBoard() {
    for (let i = 0; i < boardSize; i++) {
        for (let j = 0; j < boardSize; j++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.row = i;
            cell.dataset.col = j;
            cell.addEventListener('click', placeStone);
            gameBoard.appendChild(cell);
        }
    }
}

function placeStone(event) {
    const row = parseInt(event.target.dataset.row);
    const col = parseInt(event.target.dataset.col);
    if (board[row][col] !== null) return;

    const stone = document.createElement('div');
    stone.classList.add('stone', currentPlayer);
    event.target.appendChild(stone);
    board[row][col] = currentPlayer;

    if (checkWin(row, col)) {
        alert(`${currentPlayer.toUpperCase()} wins!`);
        resetGame();
        return;
    }

    currentPlayer = currentPlayer === 'black' ? 'white' : 'black';
}

function checkWin(row, col) {
    const directions = [
        [1, 0], // vertical
        [0, 1], // horizontal
        [1, 1], // diagonal down-right
        [1, -1] // diagonal down-left
    ];

    for (const [dx, dy] of directions) {
        let count = 1;
        for (let i = 1; i < 5; i++) {
            if (row + dx * i >= 0 && row + dx * i < boardSize &&
                col + dy * i >= 0 && col + dy * i < boardSize &&
                board[row + dx * i][col + dy * i] === currentPlayer) {
                count++;
            } else {
                break;
            }
        }
        for (let i = 1; i < 5; i++) {
            if (row - dx * i >= 0 && row - dx * i < boardSize &&
                col - dy * i >= 0 && col - dy * i < boardSize &&
                board[row - dx * i][col - dy * i] === currentPlayer) {
                count++;
            } else {
                break;
            }
        }
        if (count >= 5) return true;
    }
    return false;
}

function resetGame() {
    board = Array.from({ length: boardSize }, () => Array(boardSize).fill(null));
    gameBoard.innerHTML = '';
    createBoard();
    currentPlayer = 'black';
}

createBoard();