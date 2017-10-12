const {app, BrowserWindow} = require('electron')
const path = require('path')
const url = require('url')

let win
let port = ''+5003

function createWindow () {
  // Create the browser window.
  win = new BrowserWindow({width: 800, height: 600})

  //Replace the index.html with the katana.py index URL 
  win.loadURL("http://localhost:"+port+"/katana");

  // win.loadURL(url.format({
  //   pathname: path.join(__dirname, 'index.html'),
  //   protocol: 'file:',
  //   slashes: true
  // }))
  // De-reference the window ...
  win.on('closed', () => {
    win = null
  })
}

app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (win === null) {
    createWindow()
  }
})

// add these to the end or middle of main.js

let pyProc = null
let pyPort = null


const createPyProc = () => {
  let script = path.join(__dirname, 'katana.py')
  console.log(script, port)
 // pyProc = require('child_process').spawn('/usr/bin/python', [script, port])
  pyProc = require('child_process').execFile('/usr/bin/python', [script, '-p', port], (error,stdout,stderr) => {
	  if (error) {
		  throw error;
	  }
  })
  //pyProc = require('child_process').exec(script) 
  if (pyProc != null) {
    console.log('child process success')
  }
}

const exitPyProc = () => {
  pyProc.kill()
  pyProc = null
  pyPort = null
}

app.on('ready', createPyProc)
app.on('will-quit', exitPyProc)
