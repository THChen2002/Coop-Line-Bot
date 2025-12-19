// 基礎工具函數

/**
 * LIFF 初始化輔助函數
 * @param {string} liffId - LIFF ID
 * @param {boolean} showLoader - 是否顯示載入動畫
 * @returns {Promise<boolean>} LIFF 初始化是否成功
 */
async function initializeLIFF(liffId, showLoader = true) {
  // 顯示載入動畫
  if (showLoader) {
    showLoading('初始化中...');
  }

  try {
    await liff.init({ liffId: liffId });
    console.log('LIFF initialized successfully');

    // 檢查登入狀態（外部瀏覽器需要登入）
    if (!liff.isLoggedIn()) {
      console.log('User not logged in, redirecting to login...');
      if (showLoader) {
        showLoading('正在導向登入...');
      }
      liff.login({ redirectUri: window.location.href });
      return false;  // 登入後會重新導向回來
    }

    if (showLoader) {
      hideLoading();
    }
    return true;
  } catch (error) {
    console.error('LIFF initialization failed', error);
    if (showLoader) {
      hideLoading();
    }
    showAlert('LIFF 初始化失敗：' + error.message, 'error');
    return false;
  }
}

/**
 * 顯示載入動畫
 * @param {string} text - 載入文字（可選）
 */
function showLoading(text = '載入中...') {
  $('.loading-text').text(text);
  $('#loadingContainer').removeClass('hidden');
  $('#mainContent').addClass('hidden');
}

/**
 * 隱藏載入動畫
 */
function hideLoading() {
  $('#loadingContainer').addClass('hidden');
  $('#mainContent').removeClass('hidden');
}

/**
 * 顯示提示訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 (error, success, warning, info)
 * @param {number} duration - 顯示時長（毫秒），0 表示不自動關閉
 */
function showAlert(message, type = 'info', duration = 3000) {
  // 移除舊的提示（如果存在）
  $('.alert').remove();

  // 創建新提示
  const $alert = $('<div>')
    .addClass(`alert alert-${type}`)
    .text(message)
    .css({
      position: 'fixed',
      top: '20px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 9999,
      maxWidth: '90%',
      animation: 'slideDown 0.3s ease'
    });

  // 添加動畫樣式（如果還沒有）
  if (!$('#alertAnimationStyle').length) {
    $('<style id="alertAnimationStyle">')
      .text(`
              @keyframes slideDown {
                from {
                  opacity: 0;
                  transform: translateX(-50%) translateY(-20px);
                }
                to {
                  opacity: 1;
                  transform: translateX(-50%) translateY(0);
                }
              }
            `)
      .appendTo('head');
  }

  $('body').append($alert);

  // 自動關閉
  if (duration > 0) {
    setTimeout(() => {
      $alert.css('animation', 'slideDown 0.3s ease reverse');
      setTimeout(() => $alert.remove(), 300);
    }, duration);
  }

  return $alert;
}

/**
 * 顯示確認對話框
 * @param {string} message - 訊息內容
 * @param {Object} options - 選項
 * @param {string} options.confirmText - 確認按鈕文字
 * @param {string} options.cancelText - 取消按鈕文字
 * @param {string} options.type - 對話框類型 (warning, danger, info)
 * @returns {Promise<boolean>} 使用者是否確認
 */
function showConfirm(message, options = {}) {
  const {
    confirmText = '確認',
    cancelText = '取消',
    type = 'warning'
  } = options;

  return new Promise((resolve) => {
    // 移除舊的確認對話框（如果存在）
    $('.modal.confirm-dialog').remove();

    // 創建 modal 容器（使用統一的 modal 類別）
    const $overlay = $('<div>')
      .addClass('modal confirm-dialog')
      .css({
        animation: 'fadeIn 0.2s ease'
      });

    // 創建對話框內容（使用統一的 modal-content 類別）
    const $dialog = $('<div>')
      .addClass('modal-content')
      .css({
        animation: 'scaleIn 0.2s ease'
      });

    // 訊息文字
    const $message = $('<p>')
      .text(message)
      .css({
        margin: '0',
        fontSize: '16px',
        lineHeight: '1.5',
        color: 'var(--text-primary)',
        whiteSpace: 'pre-line',
        textAlign: 'center'
      });

    // 按鈕容器（使用統一的 modal-actions 類別）
    const $buttons = $('<div>')
      .addClass('modal-actions')
      .css({
        flexDirection: 'row',
        gap: 'var(--spacing-sm)'
      });

    // 取消按鈕
    const $cancelBtn = $('<button>')
      .text(cancelText)
      .addClass('btn btn-secondary')
      .css({
        flex: '1'
      })
      .on('click', () => {
        closeDialog(false);
      });

    // 確認按鈕
    const $confirmBtn = $('<button>')
      .text(confirmText)
      .addClass(type === 'danger' ? 'btn btn-danger' : 'btn btn-primary')
      .css({
        flex: '1'
      })
      .on('click', () => {
        closeDialog(true);
      });

    // 關閉對話框
    function closeDialog(result) {
      $overlay.css('animation', 'fadeIn 0.2s ease reverse');
      $dialog.css('animation', 'scaleIn 0.2s ease reverse');
      setTimeout(() => {
        $overlay.remove();
        resolve(result);
      }, 200);
    }

    // 組合元素
    $buttons.append($cancelBtn, $confirmBtn);
    $dialog.append($message, $buttons);
    $overlay.append($dialog);

    // 添加動畫樣式
    if (!$('#confirmAnimationStyle').length) {
      $('<style id="confirmAnimationStyle">')
        .text(`
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          @keyframes scaleIn {
            from {
              opacity: 0;
              transform: scale(0.9);
            }
            to {
              opacity: 1;
              transform: scale(1);
            }
          }
        `)
        .appendTo('head');
    }

    $('body').append($overlay);

    // 點擊遮罩關閉
    $overlay.on('click', (e) => {
      if (e.target === $overlay[0]) {
        closeDialog(false);
      }
    });
  });
}

/**
 * API 請求輔助函數
 * @param {string} url - API 端點
 * @param {Object} options - fetch 選項
 * @returns {Promise} API 回應
 */
async function apiRequest(url, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, mergedOptions);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * 取得 LIFF 使用者資訊
 * @returns {Promise<Object>} 使用者資訊
 */
async function getLIFFProfile() {
  try {
    if (!liff.isLoggedIn()) {
      liff.login({ redirectUri: window.location.href });
      return null;
    }

    const profile = await liff.getProfile();
    return profile;
  } catch (error) {
    console.error('Failed to get LIFF profile:', error);
    showAlert('無法取得使用者資訊', 'error');
    return null;
  }
}

/**
 * 關閉 LIFF 視窗
 */
function closeLIFF() {
  if (liff.isInClient()) {
    liff.closeWindow();
  } else {
    showAlert('請在 LINE 應用程式中開啟', 'warning');
  }
}

/**
 * 格式化日期
 * @param {Date|string} date - 日期物件或字串
 * @param {string} format - 格式 (default: 'YYYY-MM-DD HH:mm')
 * @returns {string} 格式化後的日期字串
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm') {
  const d = new Date(date);

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 格式化金額（加上千分位逗號）
 * @param {number} amount - 金額
 * @returns {string} 格式化後的金額字串
 */
function formatAmount(amount) {
  return new Intl.NumberFormat('zh-TW', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount);
}

/**
 * 驗證表單欄位
 * @param {HTMLFormElement} form - 表單元素
 * @returns {boolean} 驗證是否通過
 */
function validateForm(form) {
  const $inputs = $(form).find('input[required], select[required], textarea[required]');
  let isValid = true;

  $inputs.each(function () {
    const $input = $(this);
    if (!$input.val().trim()) {
      $input.addClass('error');
      isValid = false;
    } else {
      $input.removeClass('error');
    }
  });

  if (!isValid) {
    showAlert('請填寫所有必填欄位', 'warning');
  }

  return isValid;
}

/**
 * 防抖函數
 * @param {Function} func - 要執行的函數
 * @param {number} wait - 等待時間（毫秒）
 * @returns {Function} 防抖後的函數
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * 節流函數
 * @param {Function} func - 要執行的函數
 * @param {number} limit - 限制時間（毫秒）
 * @returns {Function} 節流後的函數
 */
function throttle(func, limit = 300) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * 跳脫 HTML 特殊字元（防止 XSS 攻擊）
 * @param {string} text - 要跳脫的文字
 * @returns {string} 跳脫後的文字
 */
function escapeHtml(text) {
  return $('<div>').text(text).html();
}

// 錯誤處理樣式
$(document).ready(function () {
  if (!$('#errorHandlingStyle').length) {
    $('<style id="errorHandlingStyle">')
      .text(`
        input.error, select.error, textarea.error {
            border-color: var(--danger-color) !important;
            animation: shake 0.3s;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
      `)
      .appendTo('head');
  }
});
