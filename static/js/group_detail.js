// 群組詳情頁面 JavaScript

let userId = null;
let groupId = null;
let groupData = null;
let allExpenses = [];
let allTodos = [];
let currentFeature = 'expense'; // 'expense' or 'todo'
let currentExpenseFilter = 'all';
let currentTodoFilter = 'all';

/**
 * 初始化群組詳情頁面
 */
async function initGroupDetailPage(liffId) {
  try {
    showLoading('初始化中...');

    const initialized = await initializeLIFF(liffId);
    if (!initialized) {
      return;
    }

    const profile = await liff.getProfile();
    userId = profile.userId;

    // 從 URL 路徑取得群組 ID
    groupId = window.GROUP_ID || extractGroupIdFromPath();

    if (!groupId) {
      showAlert('缺少群組資訊', 'error');
      setTimeout(() => {
        window.location.href = '/liff/full/groups';
      }, 2000);
      return;
    }

    // 從 URL 參數讀取 filter (支援清帳後跳轉到已結算頁籤)
    const urlParams = new URLSearchParams(window.location.search);
    const filterParam = urlParams.get('filter');
    if (filterParam && ['all', 'unsettled', 'settled'].includes(filterParam)) {
      currentExpenseFilter = filterParam;
    }

    // 從 URL 參數讀取功能 (支援從待辦按鈕開啟時直接顯示待辦)
    const featureParam = urlParams.get('feature');
    if (featureParam && ['expense', 'todo'].includes(featureParam)) {
      currentFeature = featureParam;
    }

    await Promise.all([
      loadGroupInfo(),
      loadExpenses(),
      loadTodos()
    ]);

    bindEvents();

    // 更新功能切換與篩選按鈕的 active 狀態
    updateFeatureTabs();
    updateExpenseFilterButtons();
    updateTodoFilterButtons();

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
 * 載入群組資訊
 */
async function loadGroupInfo() {
  try {
    const response = await apiRequest(`/api/groups/${groupId}`, {
      method: 'GET'
    });

    if (response.success) {
      groupData = response.group;

      // 檢查當前使用者是否為群組成員
      if (!groupData.members || !groupData.members.includes(userId)) {
        showAlert('您尚未加入此群組,即將跳轉到加入頁面...', 'warning');
        setTimeout(() => {
          // 跳轉到加入群組頁面,並帶入群組代碼
          window.location.href = `/liff/full/group/join?code=${groupData.group_code}`;
        }, 2000);
        return;
      }

      displayGroupInfo(response.group);
    } else {
      throw new Error(response.error || '載入群組資訊失敗');
    }
  } catch (error) {
    console.error('載入群組資訊失敗:', error);
    showAlert('載入群組資訊失敗', 'error');
  }
}

/**
 * 顯示群組資訊
 */
function displayGroupInfo(group) {
  $('#groupName').text(group.group_name);
  $('#groupCode').text(group.group_code);
  $('#memberCount').text(group.members ? group.members.length : 0);
}

/**
 * 載入帳目列表
 */
async function loadExpenses() {
  try {
    const response = await apiRequest(`/api/groups/${groupId}/expenses`, {
      method: 'GET'
    });

    if (response.success) {
      allExpenses = response.expenses || [];
      updateExpenseCount();
      filterAndDisplayExpenses();
    } else {
      throw new Error(response.error || '載入帳目失敗');
    }
  } catch (error) {
    console.error('載入帳目失敗:', error);
    showAlert('載入帳目失敗', 'error');
  }
}

/**
 * 更新帳目數量
 */
function updateExpenseCount() {
  $('#expenseCount').text(allExpenses.length);
}

/**
 * 篩選並顯示帳目
 */
function filterAndDisplayExpenses() {
  let filteredExpenses = allExpenses;

  if (currentExpenseFilter === 'unsettled') {
    filteredExpenses = allExpenses.filter(e => !e.is_settled);
  } else if (currentExpenseFilter === 'settled') {
    filteredExpenses = allExpenses.filter(e => e.is_settled);
  }

  displayExpenses(filteredExpenses);
}

/**
 * 更新記帳篩選按鈕的 active 狀態
 */
function updateExpenseFilterButtons() {
  $('.expense-filters .filter-btn').removeClass('active');
  $(`.expense-filters .filter-btn[data-filter="${currentExpenseFilter}"]`).addClass('active');
}

/**
 * 顯示帳目列表
 */
function displayExpenses(expenses) {
  const $expensesList = $('#expensesList');
  const $emptyState = $('#emptyState');

  if (!expenses || expenses.length === 0) {
    $expensesList.empty();
    $emptyState.removeClass('hidden');
    return;
  }

  $emptyState.addClass('hidden');

  const expensesHTML = expenses.map(expense => {
    const date = expense.created_at ? formatDate(expense.created_at) : '未知日期';
    const settledBadge = expense.is_settled ? '<span class="settled-badge">已結算</span>' : '';

    return `
            <div class="expense-item" data-expense-id="${expense.id}">
                <div class="expense-header">
                    <h4 class="expense-description">${escapeHtml(expense.description)}${settledBadge}</h4>
                    <span class="expense-amount">$${expense.amount}</span>
                </div>
                <div class="expense-info">
                    付款人：${escapeHtml(expense.payer_name)} |
                    分帳方式：${getSplitTypeText(expense.split_type)} |
                    分帳人數：${expense.splits ? expense.splits.length : 0} 人
                </div>
                <div class="expense-footer">
                    <span class="expense-date">${date}</span>
                    <div class="expense-actions">
                        <button class="btn-icon btn-edit" data-id="${expense.id}">編輯</button>
                        <button class="btn-icon btn-delete" data-id="${expense.id}">刪除</button>
                    </div>
                </div>
            </div>
        `;
  }).join('');

  $expensesList.html(expensesHTML);

  // 綁定編輯和刪除按鈕事件
  $('.btn-edit').on('click', function (e) {
    e.stopPropagation();
    const expenseId = $(this).data('id');
    editExpense(expenseId);
  });

  $('.btn-delete').on('click', function (e) {
    e.stopPropagation();
    const expenseId = $(this).data('id');
    deleteExpense(expenseId);
  });
}

/**
 * 取得分帳方式文字
 */
function getSplitTypeText(type) {
  const types = {
    'equal': '平均分攤',
    'custom': '自訂金額',
    'selected': '指定成員',
    'ratio': '比例分攤'
  };
  return types[type] || type;
}

/**
 * 編輯帳目
 */
function editExpense(expenseId) {
  window.location.href = `/liff/full/expenses/${expenseId}`;
}

/**
 * 刪除帳目
 */
async function deleteExpense(expenseId) {
  const confirmed = await showConfirm('確定要刪除這筆帳目嗎？', {
    confirmText: '刪除',
    cancelText: '取消',
    type: 'danger'
  });

  if (!confirmed) {
    return;
  }

  try {
    showLoading('刪除中...');

    const response = await apiRequest(`/api/expenses/${expenseId}`, {
      method: 'DELETE'
    });

    hideLoading();

    if (response.success) {
      // 檢查是否可以發送訊息到聊天室
      const context = liff.getContext();
      const canSendMessage = liff.isInClient() && context && context.type !== 'none';

      if (canSendMessage && response.flexBubble) {
        try {
          // 建構完整的 Flex Message
          const flexMessage = {
            type: "flex",
            altText: "帳目刪除通知",
            contents: response.flexBubble
          };

          // 發送訊息
          await liff.sendMessages([flexMessage]);
          console.log('已發送刪除通知');
        } catch (flexError) {
          console.error('發送刪除通知失敗:', flexError);
          // 忽略錯誤，繼續顯示刪除成功
        }
      }

      showAlert('帳目已刪除', 'success');
      await loadExpenses();
    } else {
      throw new Error(response.error || '刪除失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('刪除帳目失敗:', error);
    showAlert('刪除失敗: ' + error.message, 'error');
  }
}

/**
 * 刪除群組
 */
async function deleteGroup() {
  const confirmed = await showConfirm('確定要刪除這個群組嗎？', {
    confirmText: '刪除',
    cancelText: '取消',
    type: 'danger'
  });

  if (!confirmed) {
    return;
  }

  const doubleConfirmed = await showConfirm('刪除群組後，所有帳目和待辦事項都會永久消失，確定要繼續嗎？', {
    confirmText: '確定刪除',
    cancelText: '取消',
    type: 'danger'
  });

  if (!doubleConfirmed) {
    return;
  }

  try {
    showLoading('刪除中...');

    const response = await apiRequest(`/api/groups/${groupId}`, {
      method: 'DELETE'
    });

    hideLoading();

    if (response.success) {
      showAlert('群組已刪除', 'success', 1500);
      // 延遲後跳轉回群組列表
      setTimeout(() => {
        window.location.href = '/liff/full/groups';
      }, 1500);
    } else {
      throw new Error(response.error || '刪除失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('刪除群組失敗:', error);
    showAlert('刪除失敗: ' + error.message, 'error');
  }
}

/**
 * 綁定事件
 */
function bindEvents() {
  // 功能切換 Tab
  $('.tab-btn').on('click', function () {
    const feature = $(this).data('feature');
    switchFeature(feature);
  });

  // 刪除群組按鈕
  $('#deleteGroupBtn').on('click', deleteGroup);

  // 新增帳目按鈕
  $('#addExpenseBtn').on('click', function () {
    window.location.href = `/liff/full/groups/${groupId}/expense`;
  });

  // 結算按鈕
  $('#settlementBtn').on('click', function () {
    window.location.href = `/liff/full/groups/${groupId}/settlement`;
  });

  // 記帳篩選按鈕
  $('.expense-filters .filter-btn').on('click', function () {
    $('.expense-filters .filter-btn').removeClass('active');
    $(this).addClass('active');
    currentExpenseFilter = $(this).data('filter');
    filterAndDisplayExpenses();
  });

  // 新增待辦按鈕
  $('#addTodoBtn').on('click', function () {
    window.location.href = `/liff/full/groups/${groupId}/todo`;
  });

  // 待辦篩選按鈕
  $('.todo-filters .filter-btn').on('click', function () {
    $('.todo-filters .filter-btn').removeClass('active');
    $(this).addClass('active');
    currentTodoFilter = $(this).data('filter');
    filterAndDisplayTodos();
  });
}

/**
 * 功能切換
 */
function switchFeature(feature) {
  currentFeature = feature;

  // 更新 Tab 按鈕狀態
  $('.tab-btn').removeClass('active');
  $(`.tab-btn[data-feature="${feature}"]`).addClass('active');

  // 切換顯示區塊
  if (feature === 'expense') {
    $('#expenseSection').removeClass('hidden');
    $('#todoSection').addClass('hidden');
  } else if (feature === 'todo') {
    $('#expenseSection').addClass('hidden');
    $('#todoSection').removeClass('hidden');
  }
}

/**
 * 更新功能 Tab 的 active 狀態
 */
function updateFeatureTabs() {
  switchFeature(currentFeature);
}

/**
 * 載入待辦清單
 */
async function loadTodos() {
  try {
    const response = await apiRequest(`/api/groups/${groupId}/todos`, {
      method: 'GET'
    });

    if (response.success) {
      allTodos = response.todos || [];
      filterAndDisplayTodos();
    } else {
      throw new Error(response.error || '載入待辦清單失敗');
    }
  } catch (error) {
    console.error('載入待辦清單失敗:', error);
    showAlert('載入待辦清單失敗', 'error');
  }
}

/**
 * 篩選並顯示待辦清單
 */
function filterAndDisplayTodos() {
  let filteredTodos = allTodos;

  if (currentTodoFilter !== 'all') {
    filteredTodos = allTodos.filter(t => t.status === currentTodoFilter);
  }

  displayTodos(filteredTodos);
}

/**
 * 更新待辦篩選按鈕的 active 狀態
 */
function updateTodoFilterButtons() {
  $('.todo-filters .filter-btn').removeClass('active');
  $(`.todo-filters .filter-btn[data-filter="${currentTodoFilter}"]`).addClass('active');
}

/**
 * 顯示待辦清單
 */
function displayTodos(todos) {
  const $todosList = $('#todosList');
  const $emptyState = $('#todoEmptyState');

  if (!todos || todos.length === 0) {
    $todosList.empty();
    $emptyState.removeClass('hidden');
    return;
  }

  $emptyState.addClass('hidden');

  const todosHTML = todos.map(todo => {
    const date = todo.created_at ? formatDate(todo.created_at) : '未知日期';
    const statusText = getStatusText(todo.status);
    const statusClass = todo.status;
    const completedClass = todo.status === 'completed' ? 'completed' : '';
    const assignee = todo.assignee_name || '未指派';
    const category = todo.category || '未分類';

    return `
      <div class="todo-item ${completedClass}" data-todo-id="${todo.id}">
        <div class="todo-header">
          <h4 class="todo-title">${escapeHtml(todo.title)}</h4>
          <span class="status-badge ${statusClass}">${statusText}</span>
        </div>
        <div class="todo-info">
          ${todo.description ? escapeHtml(todo.description) + ' | ' : ''}
          負責人：${escapeHtml(assignee)} |
          類別：${escapeHtml(category)}
        </div>
        <div class="todo-footer">
          <span class="todo-date">${date}</span>
          <div class="todo-actions">
            ${todo.status !== 'completed' ? `<button class="btn-icon btn-complete" data-id="${todo.id}">完成</button>` : ''}
            <button class="btn-icon btn-edit" data-id="${todo.id}">編輯</button>
            <button class="btn-icon btn-delete" data-id="${todo.id}">刪除</button>
          </div>
        </div>
      </div>
    `;
  }).join('');

  $todosList.html(todosHTML);

  // 綁定完成按鈕
  $('.btn-complete').on('click', function (e) {
    e.stopPropagation();
    const todoId = $(this).data('id');
    completeTodo(todoId);
  });

  // 綁定編輯按鈕
  $('#todosList .btn-edit').on('click', function (e) {
    e.stopPropagation();
    const todoId = $(this).data('id');
    editTodo(todoId);
  });

  // 綁定刪除按鈕
  $('#todosList .btn-delete').on('click', function (e) {
    e.stopPropagation();
    const todoId = $(this).data('id');
    deleteTodo(todoId);
  });
}

/**
 * 取得狀態文字
 */
function getStatusText(status) {
  const statuses = {
    'pending': '待處理',
    'in_progress': '進行中',
    'completed': '已完成',
    'cancelled': '已取消'
  };
  return statuses[status] || status;
}

/**
 * 標記待辦為完成
 */
async function completeTodo(todoId) {
  try {
    showLoading('標記為完成...');

    const response = await apiRequest(`/api/todos/${todoId}/complete`, {
      method: 'PATCH'
    });

    hideLoading();

    if (response.success) {
      showAlert('已標記為完成', 'success');
      await loadTodos();
    } else {
      throw new Error(response.error || '操作失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('標記完成失敗:', error);
    showAlert('操作失敗: ' + error.message, 'error');
  }
}

/**
 * 編輯待辦
 */
function editTodo(todoId) {
  window.location.href = `/liff/full/groups/${groupId}/todo?id=${todoId}`;
}

/**
 * 刪除待辦
 */
async function deleteTodo(todoId) {
  const confirmed = await showConfirm('確定要刪除這個待辦事項嗎？', {
    confirmText: '刪除',
    cancelText: '取消',
    type: 'danger'
  });

  if (!confirmed) {
    return;
  }

  try {
    showLoading('刪除中...');

    const response = await apiRequest(`/api/todos/${todoId}`, {
      method: 'DELETE'
    });

    if (response.success) {
      // 嘗試發送 Flex Message（僅在 LIFF 內且有聊天室上下文時）
      const context = liff.getContext();
      const canSendMessage = response.flexBubble && liff.isInClient() && context && context.type !== 'none';

      if (canSendMessage) {
        try {
          showLoading('發送訊息中...');
          const flexMessage = {
            type: 'flex',
            altText: '待辦已刪除',
            contents: response.flexBubble
          };
          await liff.sendMessages([flexMessage]);
        } catch (flexError) {
          console.error('發送待辦刪除 Flex 失敗:', flexError);
        }
      }

      hideLoading();
      showAlert('待辦事項已刪除', 'success');
      await loadTodos();
    } else {
      hideLoading();
      throw new Error(response.error || '刪除失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('刪除待辦失敗:', error);
    showAlert('刪除失敗: ' + error.message, 'error');
  }
}

/**
 * 格式化日期
 */
function formatDate(timestamp) {
  if (!timestamp) return '未知日期';

  let date;
  if (timestamp.seconds) {
    date = new Date(timestamp.seconds * 1000);
  } else if (timestamp._seconds) {
    date = new Date(timestamp._seconds * 1000);
  } else {
    date = new Date(timestamp);
  }

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}/${month}/${day} ${hours}:${minutes}`;
}
