// 加入群組頁面 JavaScript

let userId = null;
let userProfile = null;
let groupData = null;

/**
 * 初始化加入群組頁面
 */
async function initGroupJoinPage(liffId) {
  try {
    showLoading('初始化中...');

    const initialized = await initializeLIFF(liffId);
    if (!initialized) {
      return;
    }

    const profile = await liff.getProfile();
    userId = profile.userId;
    userProfile = profile;

    // 如果有預設群組代碼，自動查詢
    if (window.INITIAL_GROUP_CODE) {
      await verifyGroupCode(window.INITIAL_GROUP_CODE);
    }

    bindEvents();
    hideLoading();
  } catch (error) {
    console.error('初始化失敗:', error);
    showAlert('初始化失敗: ' + error.message, 'error');
    hideLoading();
  }
}

/**
 * 綁定事件
 */
function bindEvents() {
  $('#joinGroupForm').on('submit', handleSubmit);

  $('#cancelBtn').on('click', function () {
    window.location.href = '/liff/full/groups';
  });

  // 群組代碼輸入監聽
  $('#groupCode').on('input', function () {
    const value = $(this).val().toUpperCase();
    $(this).val(value);

    if (value.length === 6) {
      verifyGroupCode(value);
    } else {
      hideGroupPreview();
    }
  });
}

/**
 * 驗證群組代碼（使用 GET 查詢，不加入）
 */
async function verifyGroupCode(code) {
  try {
    const response = await apiRequest(`/api/groups/${code}?by=code&user_id=${userId}`, {
      method: 'GET'
    });

    if (response.success) {
      groupData = response.group;
      groupData.is_member = response.is_member;
      showGroupPreview(response.group, response.is_member);
    } else {
      hideGroupPreview();
      showAlert(response.error, 'warning');
    }
  } catch (error) {
    hideGroupPreview();
    console.error('驗證群組代碼失敗:', error);
  }
}

/**
 * 顯示群組預覽
 */
function showGroupPreview(group, isMember = false) {
  $('#previewGroupName').text(group.group_name);
  $('#previewMemberCount').text(group.members ? group.members.length : 0);
  $('#groupPreview').removeClass('hidden');

  // 根據是否已是成員更新按鈕文字
  const $submitBtn = $('#joinGroupForm button[type="submit"]');
  if ($submitBtn.length) {
    $submitBtn.text(isMember ? '進入群組' : '加入群組');
  }
}

/**
 * 隱藏群組預覽
 */
function hideGroupPreview() {
  $('#groupPreview').addClass('hidden');
  groupData = null;
}

/**
 * 處理表單提交
 */
async function handleSubmit(e) {
  e.preventDefault();

  const groupCode = $('#groupCode').val().trim().toUpperCase();

  if (!groupCode || groupCode.length !== 6) {
    showAlert('請輸入正確的 6 位數群組代碼', 'warning');
    return;
  }

  // 如果已經是成員，直接跳轉
  if (groupData && groupData.is_member) {
    window.location.href = `/liff/full/groups/${groupData.id}`;
    return;
  }

  try {
    showLoading('加入群組中...');

    const response = await apiRequest('/api/groups/join', {
      method: 'POST',
      body: JSON.stringify({
        group_code: groupCode,
        user_id: userId,
        display_name: userProfile.displayName,
        picture_url: userProfile.pictureUrl || ''
      })
    });

    hideLoading();

    if (response.success) {
      const message = response.already_member ? '您已是群組成員' : '成功加入群組！';
      showAlert(message, 'success');
      setTimeout(() => {
        window.location.href = `/liff/full/groups/${response.group.id}`;
      }, 1000);
    } else {
      throw new Error(response.error || '加入群組失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('加入群組失敗:', error);
    showAlert(error.message, 'error');
  }
}
