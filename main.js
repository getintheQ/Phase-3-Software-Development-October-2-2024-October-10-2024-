const { app, BrowserWindow } = require('electron');
const path = require('path');

// Handle creating/removing shortcuts on Windows when installing/uninstalling
if (require('electron-squirrel-startup')) {
  app.quit();
}

function createWindow() {
  // Create the browser window with Raspberry Pi 7-inch dimensions
  // Screen Dimensions: 194mm x 110mm x 20mm
  // Converted to pixels (approximately)
  const mainWindow = new BrowserWindow({
    width: 800,  // Slightly wider for window controls
    height: 480, // Standard 7-inch Raspberry Pi display height
    minWidth: 800,
    minHeight: 480,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    frame: true,  // Enable window frame for controls
    resizable: true,  // Allow resizing
    backgroundColor: '#f5f5f5'
  });

  // Load the index.html file
  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));
  
  // Set the window to be centered
  mainWindow.center();

  // Optional: Open DevTools in development
  // mainWindow.webContents.openDevTools();
}

// Create window when app is ready
app.whenReady().then(createWindow);

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});