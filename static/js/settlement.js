// 結算頁面 JavaScript

let userId = null;
let groupId = null;
let userName = null;
let settlementData = null;

/**
 * 初始化結算頁面
 */
async function initSettlementPage(liffId) {
  try {
    showLoading('初始化中...');

    const initialized = await initializeLIFF(liffId);
    if (!initialized) {
      // 正在導向登入，不繼續執行
      return;
    }

    // 取得使用者資訊
    const profile = await liff.getProfile();
    userId = profile.userId;
    userName = profile.displayName;

    // 取得群組 ID (從 URL path 或 window 變數)
    groupId = window.GROUP_ID || extractGroupIdFromPath();

    if (!groupId) {
      showAlert('缺少群組資訊', 'error');
      setTimeout(() => {
        window.location.href = '/liff/full/groups';
      }, 2000);
      return;
    }

    // 載入結算資訊
    await loadSettlement();

    // 綁定事件
    bindEvents();

    hideLoading();
  } catch (error) {
    console.error('初始化失敗:', error);
    showAlert('初始化失敗: ' + error.message, 'error');
    hideLoading();
  }
}

/**
 * 從 URL 路徑提取群組 ID
 */
function extractGroupIdFromPath() {
  const pathMatch = window.location.pathname.match(/\/groups\/([^\/]+)/);
  return pathMatch ? pathMatch[1] : null;
}

/**
 * 載入結算資訊
 */
async function loadSettlement() {
  try {
    const response = await apiRequest(`/api/groups/${groupId}/settlement`, {
      method: 'GET'
    });

    if (response.success) {
      settlementData = response;
      displaySettlement(response);
    } else {
      throw new Error(response.error || '載入結算資訊失敗');
    }
  } catch (error) {
    console.error('載入結算資訊失敗:', error);
    showAlert('載入結算資訊失敗', 'error');
  }
}

/**
 * 顯示結算資訊
 */
function displaySettlement(data) {
  // 更新帳目數量
  $('#expenseCount').text(data.expense_count || 0);

  if (!data.has_expenses) {
    // 沒有未結算的帳目
    $('#emptyBalanceState').removeClass('hidden');
    $('#emptyActionSection').removeClass('hidden');
    return;
  }

  // 顯示收支平衡
  displayBalances(data.balances);

  // 顯示還款計畫
  if (data.payment_plans && data.payment_plans.length > 0) {
    displayPaymentPlans(data.payment_plans);
    $('#paymentSection').removeClass('hidden');
  }

  // 顯示操作按鈕
  $('#actionSection').removeClass('hidden');
}

/**
 * 顯示收支平衡列表
 */
function displayBalances(balances) {
  const $balancesList = $('#balancesList');
  const $emptyState = $('#emptyBalanceState');

  if (!balances || Object.keys(balances).length === 0) {
    $emptyState.removeClass('hidden');
    return;
  }

  $emptyState.addClass('hidden');

  // 轉換為陣列並排序（應收在前）
  const balancesArray = Object.entries(balances).map(([userId, data]) => ({
    userId,
    userName: data.user_name,
    netAmount: data.net_amount
  })).sort((a, b) => b.netAmount - a.netAmount);

  const balancesHTML = balancesArray.map(balance => {
    const isPositive = balance.netAmount > 0.01;
    const isNegative = balance.netAmount < -0.01;
    const amount = Math.abs(balance.netAmount);

    let statusClass = 'neutral';
    let statusText = '已平衡';
    let amountText = '$0';

    if (isPositive) {
      statusClass = 'positive';
      statusText = '應收';
      amountText = `+$${amount}`;
    } else if (isNegative) {
      statusClass = 'negative';
      statusText = '應付';
      amountText = `-$${amount}`;
    }

    return `
            <div class="balance-item ${statusClass}">
                <div class="balance-user">
                    <span class="user-name">${escapeHtml(balance.userName)}</span>
                    <span class="balance-status">${statusText}</span>
                </div>
                <span class="balance-amount">${amountText}</span>
            </div>
        `;
  }).join('');

  $balancesList.html(balancesHTML);
}

/**
 * 顯示還款計畫列表
 */
function displayPaymentPlans(plans) {
  const $plansList = $('#paymentPlansList');

  const plansHTML = plans.map((plan, index) => {
    return `
      <div class="payment-item">
        <div class="payment-number">${index + 1}</div>
        <div class="payment-content">
          <div class="payment-from-to">
            <span class="payment-from">${escapeHtml(plan.from_user_name)}</span>
            <span class="payment-arrow">→</span>
            <span class="payment-to">${escapeHtml(plan.to_user_name)}</span>
          </div>
          <div class="payment-amount">$${plan.amount}</div>
        </div>
      </div>
    `;
  }).join('');

  $plansList.html(plansHTML);
}

/**
 * 清帳
 */
async function clearSettlement() {
  const confirmed = await showConfirm(
    '確定要清帳嗎？\n所有未結算的帳目將被標記為已結算。',
    {
      confirmText: '確認清帳',
      cancelText: '取消',
      type: 'warning'
    }
  );

  if (!confirmed) {
    return;
  }

  try {
    showLoading('清帳中...');

    const response = await apiRequest(`/api/groups/${groupId}/settlement/clear`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        user_name: userName
      })
    });

    if (response.success) {
      // 嘗試發送結算結果 Flex Message 到聊天室
      const context = liff.getContext();
      const canSendMessage = response.flexBubble && liff.isInClient() && context && context.type !== 'none';

      if (canSendMessage) {
        try {
          const flexMessage = {
            type: 'flex',
            altText: '結算報告',
            contents: response.flexBubble
          };
          await liff.sendMessages([flexMessage]);
        } catch (flexError) {
          console.error('發送結算 Flex 失敗:', flexError);
          // 失敗時不阻止後續流程
        }
      }

      hideLoading();
      showAlert(`已成功清帳 ${response.expense_count} 筆帳目`, 'success');

      // 2秒後返回群組詳情頁並顯示已結算頁籤
      setTimeout(() => {
        window.location.href = `/liff/full/groups/${groupId}?filter=settled`;
      }, 2000);
    } else {
      hideLoading();
      throw new Error(response.error || '清帳失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('清帳失敗:', error);
    showAlert('清帳失敗: ' + error.message, 'error');
  }
}

/**
 * 綁定事件
 */
function bindEvents() {
  // 清帳按鈕
  $('#clearBtn').on('click', clearSettlement);
}
