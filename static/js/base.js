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
