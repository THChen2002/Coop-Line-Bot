// 記帳表單邏輯
let splitType = 'equal';
let groupId = '';
let expenseId = null; // 編輯模式的 expense ID

/**
 * 初始化記帳表單
 */
async function initExpenseForm(liffId) {
  const initialized = await initializeLIFF(liffId);

  if (initialized) {
    initializeForm();
  }
}

/**
 * 從 URL 路徑提取 expense_id
 */
function extractExpenseIdFromPath() {
  const pathMatch = window.location.pathname.match(/\/expenses\/([^\/]+)/);
  return pathMatch ? pathMatch[1] : null;
}

/**
 * 初始化表單（綁定事件）
 */
function initializeForm() {
  try {
    // 使用後端傳入的 group_id
    groupId = window.GROUP_ID;

    // 從 URL 路徑判斷是否為編輯模式並提取 expense_id
    const pathMatch = window.location.pathname.match(/\/expenses\/([^\/]+)(?:\/edit)?/);
    if (pathMatch) {
      expenseId = pathMatch[1];
      // 檢查 URL 是否包含 /edit
      const isEditMode = window.location.pathname.includes('/edit');
      if (isEditMode) {
        // 編輯模式：從 DOM 讀取當前 active 的分帳方式按鈕
        const $activeBtn = $('.split-type-btn.active');
        if ($activeBtn.length) {
          splitType = $activeBtn.data('type');
        }
      }
    }

    console.log('Group ID:', groupId);
    console.log('Expense ID:', expenseId);

    if (!groupId) {
      showAlert('此功能只能在群組中使用', 'error');
      return;
    }

    // 檢查是否有成員資料（由模板渲染）
    const $memberItems = $('#membersList .member-item');
    if ($memberItems.length === 0) {
      showAlert('群組中沒有成員資料，請確保群組成員有在 LINE 中發言過', 'warning');
      return;
    }

    // 如果是編輯模式且有預填資料，觸發分帳方式按鈕更新 UI
    if (expenseId && $('.split-type-btn.active').length) {
      $('.split-type-btn.active').click();
    }

    // 綁定成員列表的事件
    bindMemberEvents();
  } catch (err) {
    console.error('Initialize form error:', err);
    showAlert('初始化表單失敗: ' + err.message, 'error');
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
 * 綁定成員列表的事件
 */
function bindMemberEvents() {
  // 綁定 checkbox 變更事件
  $('#membersList input[type="checkbox"]').on('change', updateAllocation);

  // 綁定金額輸入事件
  $('#membersList .member-amount').on('input', updateAllocation);
}

/**
 * 切換分帳方式
 */
function setupSplitTypeButtons() {
  $('.split-type-btn').on('click', function () {
    $('.split-type-btn').removeClass('active');
    $(this).addClass('active');
    splitType = $(this).data('type');

    // 切換金額輸入框的啟用狀態
    const isEqual = splitType === 'equal';

    if (isEqual) {
      // 平均分帳：所有金額欄位 disabled
      $('.member-amount').prop('disabled', true).val('');
    } else {
      // 自訂金額：根據勾選狀態設定 disabled
      $('#membersList input[type="checkbox"]').each(function () {
        const $amountInput = $(`#amount_${$(this).val()}`);
        if ($(this).is(':checked')) {
          $amountInput.prop('disabled', false);
        } else {
          $amountInput.prop('disabled', true).val(0);
        }
      });
    }

    updateAllocation();
  });
}

/**
 * 更新分配金額
 */
function updateAllocation() {
  const totalAmount = parseFloat($('#amount').val()) || 0;
  const $checkedMembers = $('#membersList input[type="checkbox"]:checked');

  if (splitType === 'equal' && $checkedMembers.length > 0) {
    const count = $checkedMembers.length;

    // 四捨五入到整數元，避免小數點
    const totalInt = Math.round(totalAmount);
    const baseAmount = Math.floor(totalInt / count);
    const remainder = totalInt % count;

    // 分配：最後 remainder 個人多分 1 元
    let allocated = 0;
    $checkedMembers.each(function (index) {
      const amount = (index >= count - remainder) ? baseAmount + 1 : baseAmount;
      $(`#amount_${$(this).val()}`).val(amount);
      allocated += amount;
    });

    // 未勾選的成員金額歸零
    $('#membersList input[type="checkbox"]:not(:checked)').each(function () {
      $(`#amount_${$(this).val()}`).val(0);
    });

    // 檢查分配金額是否與總金額相符
    const $totalCheck = $('#totalCheck');
    const $allocatedAmount = $('#allocatedAmount');

    if (allocated !== totalAmount) {
      $totalCheck.show();
      $allocatedAmount.text(`NT$ ${formatAmount(allocated)}`);
      $allocatedAmount.addClass('over-budget');
    } else {
      $totalCheck.hide();
    }
  } else if (splitType === 'custom') {
    // 已勾選的成員：啟用金額欄位
    $checkedMembers.each(function () {
      $(`#amount_${$(this).val()}`).prop('disabled', false);
    });

    // 未勾選的成員：disabled 並歸零
    $('#membersList input[type="checkbox"]:not(:checked)').each(function () {
      $(`#amount_${$(this).val()}`).prop('disabled', true).val(0);
    });

    // 計算已分配金額
    let allocated = 0;
    $checkedMembers.each(function () {
      const amount = parseFloat($(`#amount_${$(this).val()}`).val()) || 0;
      allocated += amount;
    });

    const $totalCheck = $('#totalCheck');
    const $allocatedAmount = $('#allocatedAmount');

    $totalCheck.show();
    $allocatedAmount.text(`NT$ ${formatAmount(allocated)}`);

    // 檢查分配金額是否與總金額相符（不相等就顯示紅色）
    if (allocated !== totalAmount) {
      $allocatedAmount.addClass('over-budget');
    } else {
      $allocatedAmount.removeClass('over-budget');
    }
  }
}

/**
 * 處理表單提交
 */
async function handleExpenseSubmit(e) {
  e.preventDefault();

  const $form = $(e.target);
  if (!validateForm($form[0])) {
    return;
  }

  const description = $('#description').val();
  const amount = parseFloat($('#amount').val());
  const payerId = $('#payer').val();

  if (!payerId) {
    showAlert('請選擇付款人', 'warning');
    return;
  }

  const $checkedMembers = $('#membersList input[type="checkbox"]:checked');

  if ($checkedMembers.length === 0) {
    showAlert('請至少選擇一位分帳成員', 'warning');
    return;
  }

  // 收集分帳資料
  const splits = [];
  let totalAllocated = 0;

  $checkedMembers.each(function () {
    const memberId = $(this).val();
    const memberName = $(this).data('name');
    const splitAmount = parseFloat($(`#amount_${memberId}`).val()) || 0;

    splits.push({
      user_id: memberId,
      user_name: memberName,
      amount: splitAmount,
      is_paid: false
    });

    totalAllocated += splitAmount;
  });

  // 驗證總金額
  if (Math.abs(totalAllocated - amount) > 0.01) {
    showAlert(`分配金額 (${formatAmount(totalAllocated)}) 與總金額 (${formatAmount(amount)}) 不符`, 'error');
    return;
  }

  // 送出資料
  try {
    showLoading(expenseId ? '更新中...' : '處理中...');

    const payerName = $(`#payer option[value="${payerId}"]`).text();

    const expenseData = {
      payer_id: payerId,
      payer_name: payerName,
      amount: amount,
      description: description,
      split_type: splitType,
      splits: splits
    };

    let result;
    if (expenseId) {
      // 編輯模式：使用 PUT
      result = await apiRequest(`/api/expenses/${expenseId}`, {
        method: 'PUT',
        body: JSON.stringify(expenseData)
      });
    } else {
      // 新增模式：使用 POST
      expenseData.group_id = groupId;
      expenseData.created_by = payerId;
      result = await apiRequest(`/api/groups/${groupId}/expenses`, {
        method: 'POST',
        body: JSON.stringify(expenseData)
      });
    }

    if (result.success) {
      // 檢查是否可以發送訊息到聊天室
      // 條件：在 LINE 內建瀏覽器中，且有聊天室上下文（從群組/聊天室開啟）
      const context = liff.getContext();
      const canSendMessage = liff.isInClient() && context && context.type !== 'none';

      if (canSendMessage && result.flexBubble) {
        // 更新 loading 文字
        showLoading('發送訊息中...');

        try {
          const expense = result.expense;

          // 包裝成完整的 Flex Message
          const flexMessage = {
            type: 'flex',
            altText: `記帳成功：${expense.description} NT$ ${expense.amount.toLocaleString()}`,
            contents: result.flexBubble
          };

          // 使用 liff.sendMessages 發送訊息
          await liff.sendMessages([flexMessage]);
          hideLoading();
          showAlert(expenseId ? '更新成功！' : '記帳成功！', 'success', 1000);
        } catch (err) {
          console.error('發送訊息失敗:', err);
          // 即使發送失敗，也顯示成功
          hideLoading();
          showAlert(expenseId ? '更新成功！' : '記帳成功！', 'success', 1000);
        }
      } else {
        // 外部瀏覽器或沒有 flexBubble：直接顯示成功
        hideLoading();
        showAlert(expenseId ? '更新成功！' : '記帳成功！', 'success', 1000);
      }

      // 統一在這裡跳轉
      setTimeout(() => {
        window.location.href = `/liff/full/groups/${groupId}`;
      }, 1000);
    } else {
      hideLoading();
      showAlert(result.error || (expenseId ? '更新失敗' : '記帳失敗'), 'error');
    }
  } catch (err) {
    hideLoading();
    showAlert('送出失敗: ' + err.message, 'error');
  }
}

// 初始化
$(document).ready(function () {
  // 設置分帳方式按鈕
  setupSplitTypeButtons();

  // 監聽總金額變化
  $('#amount').on('input', debounce(updateAllocation, 300));

  // 監聽表單提交
  $('#expenseForm').on('submit', handleExpenseSubmit);
});
