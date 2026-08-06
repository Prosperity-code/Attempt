/**
 * 番茄钟 — Electron 主进程
 *
 * 职责：
 *   1. 创建一个无边框、透明背景、带圆角的窗口，加载渲染进程页面
 *   2. 创建系统托盘图标和右键菜单（显示/置顶/退出）
 *   3. 通过 IPC 接收渲染进程的请求并执行系统级操作（最小化、置顶、通知）
 *   4. 管理应用生命周期，关闭窗口时最小化到托盘而非真正退出
 */

// ===== 1. 导入依赖 =====
// BrowserWindow — 创建和管理窗口
// ipcMain        — 主进程端 IPC，接收渲染进程发来的消息
// Notification   — 系统原生通知
// Tray / Menu    — 系统托盘图标和右键菜单
// nativeImage    — 从原始像素数据创建图标（不需要外部图片文件）
const { app, BrowserWindow, ipcMain, Notification, Tray, Menu, nativeImage } = require('electron');
const path = require('path');

// ===== 2. 全局状态 =====
let mainWindow = null; // 主窗口实例，全局持有防止被 GC 回收
let tray       = null; // 系统托盘实例
let isQuitting = false; // 标记是否正在真正退出（用于区分"关闭窗口"和"退出应用"）

// ====================================================================
//                          主窗口
// ====================================================================
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 420,              // 窗口宽度（像素）
    height: 620,             // 窗口高度（像素）
    resizable: false,        // 禁止拖拽调整大小
    frame: false,            // 无边框 → 实现自定义标题栏（圆角、深色）
    transparent: true,       // 背景透明 → 配合 CSS 的 border-radius 实现圆角窗口
    backgroundColor: '#00000000', // RGBA 全透明，避免圆角外露出白色色块
    skipTaskbar: false,      // 仍然显示在任务栏
    webPreferences: {
      // preload 脚本：在渲染进程加载前执行，通过 contextBridge 暴露安全的 API
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,  // 开启上下文隔离 → 渲染进程无法直接访问 Node.js
      nodeIntegration: false,  // 关闭 Node 集成 → 安全性最佳实践
    },
  });

  // 加载渲染进程页面（就是那个漂亮番茄钟 UI）
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // 虽然 resizable: false 禁止了拖拽缩放，但双击标题栏仍可能触发最大化
  // 这里监听 maximize 事件，一旦发生立刻取消最大化，恢复原本大小
  mainWindow.on('maximize', () => mainWindow.unmaximize());

  /**
   * 核心设计：点 × 按钮 ≠ 退出应用
   *
   * 用户点关闭按钮时：
   *   → 如果 isQuitting = false（正常使用中）：拦截关闭，改为隐藏窗口
   *   → 如果 isQuitting = true（用户从托盘菜单点了"退出"）：允许关闭
   *
   * 这样做的目的是让番茄钟常驻后台，计时不中断，
   * 用户可以通过托盘图标重新打开窗口。
   */
  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault();       // 阻止默认的窗口销毁行为
      mainWindow.hide();        // 隐藏窗口，进程继续保持运行
    }
  });
}

// ====================================================================
//                         系统托盘
// ====================================================================
function createTray() {
  // 没有 .ico 文件？没关系，用代码逐像素画一个红色圆形当作番茄图标
  const icon = createTrayIcon();
  tray = new Tray(icon);

  // 构建托盘右键菜单
  const menu = Menu.buildFromTemplate([
    {
      label: '显示窗口',
      click: () => {
        mainWindow.show();     // 恢复被隐藏的窗口
        mainWindow.focus();    // 将窗口聚焦到最前面
      },
    },
    { type: 'separator' },     // 分隔线
    {
      label: '窗口置顶',        // 复选框菜单项，可打钩/取消
      type: 'checkbox',
      checked: false,
      click: (item) => {
        mainWindow.setAlwaysOnTop(item.checked); // 切换窗口置顶状态
      },
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        isQuitting = true;     // 标记为正在退出，跳过 close 事件的拦截
        app.quit();            // 触发应用退出流程
      },
    },
  ]);

  tray.setToolTip('🍅 番茄钟');           // 鼠标悬停提示
  tray.setContextMenu(menu);              // 绑定右键菜单
  // 双击托盘图标也能快速打开窗口
  tray.on('double-click', () => {
    mainWindow.show();
    mainWindow.focus();
  });
}

/**
 * 用代码动态生成托盘图标（32×32 像素的红色番茄圆）
 *
 * 原理：
 *  - 32×32 像素 × 4 通道（RGBA）= 4096 字节
 *  - 遍历每个像素，计算它到圆心的距离
 *  - 距离 <= 半径 → 红色（番茄主体）
 *  - 半径 < 距离 <= 半径+1.5 → 暗红色（一圈淡淡的描边）
 *  - 其他 → 全透明
 *  - 最终用 nativeImage.createFromBuffer 转成 Electron 可用的图标对象
 */
function createTrayIcon() {
  const size = 32;
  // Buffer.alloc: 分配 32×32×4 字节的缓冲区（每个像素 RGBA 4 字节）
  const buffer = Buffer.alloc(size * size * 4);
  const cx = size / 2, cy = size / 2 - 1, r = 12; // 圆心略偏上，视觉更好

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = x - cx, dy = y - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);               // 当前像素到圆心的距离
      const i = (y * size + x) * 4;                            // 这个像素在 buffer 中的起始索引

      if (dist <= r) {
        // 半径内 → 番茄红 (R=233, G=69, B=96, A=255 不透明)
        buffer[i] = 233; buffer[i + 1] = 69; buffer[i + 2] = 96; buffer[i + 3] = 255;
      } else if (dist <= r + 1.5) {
        // 半径边缘外 1.5 像素 → 暗红色半透明描边，让图标边缘更柔和
        buffer[i] = 160; buffer[i + 1] = 40; buffer[i + 2] = 60; buffer[i + 3] = 200;
      } else {
        // 其余区域全透明（背景不可见）
        buffer[i + 3] = 0;
      }
    }
  }
  // 把原始 RGBA 数据转成 Electron 的 nativeImage
  return nativeImage.createFromBuffer(buffer, { width: size, height: size });
}

// ====================================================================
//                       应用生命周期
// ====================================================================

// Electron 完成初始化后执行（比 DOMContentLoaded 更早，是应用级的 ready）
app.whenReady().then(() => {
  createWindow();  // 先创建主窗口
  createTray();    // 再创建托盘图标（顺序不重要，这里先窗口后托盘）

  // macOS 的特性：点 Dock 图标时，如果所有窗口都关闭了就重新创建一个
  // Windows/Linux 下这个事件一般不会触发（因为 window-all-closed 就退出）
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 所有窗口关闭时
app.on('window-all-closed', () => {
  // macOS 下应用即使在所有窗口关闭后也保持运行（菜单栏仍然可见）
  // Windows/Linux 下直接退出
  if (process.platform !== 'darwin') app.quit();
});

// app.quit() 被调用时 → 在真正退出前设置标记
// 确保 close 事件处理函数知道这是"真正退出"而非"只是关窗口"
app.on('before-quit', () => {
  isQuitting = true;
});

// ====================================================================
//                  IPC（进程间通信）处理器
// ====================================================================

/**
 * 渲染进程是沙箱环境（contextIsolation: true, nodeIntegration: false），
 * 无法直接调用 Node.js 或 Electron API。
 *
 * 渲染进程通过 preload.js 暴露的 electronAPI，用 ipcRenderer.send() 发消息，
 * 主进程在这里用 ipcMain.on() 接收并执行对应的系统操作。
 */

// 最小化窗口
ipcMain.on('window-minimize', () => mainWindow?.minimize());

// 切换窗口置顶（标题栏按钮触发）
ipcMain.on('window-toggle-top', (_e, enable) => mainWindow?.setAlwaysOnTop(enable));

// 发送系统通知（计时结束时触发）
ipcMain.on('notify', (_e, { title, body }) => {
  // 检查当前系统是否支持通知（部分 Linux 桌面环境可能不支持）
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
});

// 退出应用（托盘菜单或渲染进程调用）
ipcMain.on('quit-app', () => {
  isQuitting = true;
  app.quit();
});
