const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  minimize: () => ipcRenderer.send('window-minimize'),
  toggleTop: (on) => ipcRenderer.send('window-toggle-top', on),
  notify: (opts) => ipcRenderer.send('notify', opts),
  quit: () => ipcRenderer.send('quit-app'),
});
