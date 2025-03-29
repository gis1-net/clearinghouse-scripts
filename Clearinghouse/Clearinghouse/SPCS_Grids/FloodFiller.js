
export const CELL_STATE = {
  HOLE: -1,
  EXTERIOR: 0,
  FILL: 1
}

export class FloodFiller {
  _initialGrid = []
  _grid = []
  _visited = []
  _holes = []
  _queue = []

  constructor(grid) {
    this._initialGrid = grid
    this._grid = grid
  }

  printGrid() {
    const printValue = {
      [CELL_STATE.HOLE]: 'O',
      [CELL_STATE.EXTERIOR]: ' ',
      [CELL_STATE.FILL]: 'X'
    }

    for (let x = 0; x < this._grid.length; x++) {
      for (let y = 0; y < this._grid[x].length; y++) {
        process.stdout.write(printValue(this._grid[x][y]) + ' ')
      }
      process.stdout.write('\n')
    }
  }

  findHoles() {
    //Trace top and bottom edge
    for (let x = 0; x < this._grid.length; x++) {
      this._queue.push([x, 0, undefined])
      this._queue.push([x, this._grid[this._grid.length - 1].length - 1, undefined])
    }

    //Trace left and right edge
    for (let y = 1; y < this._grid[this._grid.length - 1].length - 1; y++) {
      this._queue.push([0, y, undefined])
      this._queue.push([this._grid.length - 1, y, undefined])
    }

    while (this._queue.length > 0) {
      const args = this._queue.shift()
      this._fill(args[0], args[1], args[2])
    }

    for (let x = 1; x < this._grid.length - 1; x++) {
      for (let y = 1; y < this._grid[x].length - 1; y++) {
        if (!this._visited[x]) {
          this._visited[x] = []
        }
        if (!this._visited[x][y] && this._grid[x][y] === undefined) {
          this._queue.push([x, y, undefined])

          while (this._queue.length > 0) {
            const args = this._queue.shift()
            this._fill(args[0], args[1], args[2])
          }
        }
      }
    }

    return this._holes
  }

  _fill(x, y, state) {
    console.log('Filling', x, y)
    //Check if cell is out of bounds
    if (x < 0 || x >= this._grid.length || y < 0 || y >= this._grid[x].length) {
      return
    }

    //Check if cell has been visited
    if (!this._visited[x]) {
      this._visited[x] = []
    }
    if (this._visited[x][y]) {
      return
    }

    //Mark cell as visited
    this._visited[x][y] = true
    
    //Check if cell has a value already
    if (this._grid[x][y] !== undefined) {
      return
    }

    //Determine desired state for cell
    let desiredState = state
    if (desiredState === undefined) {
      if (x === 0 || y === 0 || x === this._grid.length - 1 || y === this._grid[x].length - 1) {
        desiredState = CELL_STATE.EXTERIOR
      } else {
        desiredState = CELL_STATE.HOLE
      }
    }
    
    //Set cell state
    this._grid[x][y] = desiredState

    //Add holes to list
    if (desiredState === CELL_STATE.HOLE) {
      this._holes.push([x, y])
    }

    //Recursively check neighbors
    this._queue.push([x - 1, y, desiredState])
    this._queue.push([x + 1, y, desiredState])
    this._queue.push([x, y - 1, desiredState])
    this._queue.push([x, y + 1, desiredState])
  }
}