// 群組列表頁面 JavaScript

let userId = null;

/**
 * 初始化群組列表頁面
 */
async function initGroupsListPage(liffId) {
  try {
    showLoading('初始化中...');

    const initialized = await initializeLIFF(liffId);
    if (!initialized) {
      return;
    }

    const profile = await liff.getProfile();
    userId = profile.userId;

    await loadGroups();
    bindEvents();
    hideLoading();
  } catch (error) {
    console.error('初始化失敗:', error);
    showAlert('初始化失敗: ' + error.message, 'error');
    hideLoading();
  }
}

/**
 * 載入群組列表
 */
async function loadGroups() {
  try {
    const response = await apiRequest(`/api/groups?user_id=${userId}`, {
      method: 'GET'
    });

    if (response.success) {
      displayGroups(response.groups);
    } else {
      throw new Error(response.error || '載入群組列表失敗');
    }
  } catch (error) {
    console.error('載入群組列表失敗:', error);
    showAlert('載入群組列表失敗: ' + error.message, 'error');
  }
}

/**
 * 顯示群組列表
 */
function displayGroups(groups) {
  const $groupsList = $('#groupsList');
  const $emptyState = $('#emptyState');

  if (!groups || groups.length === 0) {
    $groupsList.empty();
    $emptyState.removeClass('hidden');
    return;
  }

  $emptyState.addClass('hidden');

  const groupsHTML = groups.map(group => {
    const isCreator = group.created_by === userId;
    const memberCount = group.members ? group.members.length : 0;

    return `
      <div class="group-item" data-group-id="${group.id}" data-group-code="${group.group_code}" data-group-name="${escapeHtml(group.group_name)}">
        <div class="group-header">
          <h3 class="group-name">
            ${escapeHtml(group.group_name)}
            ${isCreator ? '<span class="group-creator-badge">建立者</span>' : ''}
          </h3>
          <span class="group-code">${group.group_code}</span>
        </div>
        <div class="group-info">
          <div class="group-info-item">
            <span><i class="fas fa-users"></i></span>
            <span>${memberCount} 位成員</span>
          </div>
        </div>
        <div class="group-actions">
          <button class="btn-icon btn-share" data-group-id="${group.id}" title="分享邀請連結">
            <i class="fas fa-share-alt"></i> 分享
          </button>
        </div>
      </div>
    `;
  }).join('');

  $groupsList.html(groupsHTML);

  // 綁定點擊事件 - 打開群組詳情頁
  $('.group-item').on('click', function (e) {
    // 如果點擊的是分享按鈕，不觸發群組點擊
    if ($(e.target).hasClass('btn-share') || $(e.target).closest('.btn-share').length) {
      return;
    }
    const groupId = $(this).data('group-id');
    openGroupDetail(groupId);
  });

  // 綁定分享按鈕事件
  $('.btn-share').on('click', function (e) {
    e.stopPropagation();
    const $groupItem = $(this).closest('.group-item');
    const groupId = $groupItem.data('group-id');
    const groupCode = $groupItem.data('group-code');
    const groupName = $groupItem.data('group-name');
    shareGroupInvite(groupId, groupCode, groupName, {
      enableFallback: true
    });
  });
}

/**
 * 開啟群組詳情頁面
 */
function openGroupDetail(groupId) {
  window.location.href = `/liff/full/groups/${groupId}`;
}

/**
 * 綁定事件
 */
function bindEvents() {
  $('#createGroupBtn').on('click', function () {
    window.location.href = '/liff/full/group/create';
  });

  $('#joinGroupBtn').on('click', function () {
    window.location.href = '/liff/full/group/join';
  });
}

