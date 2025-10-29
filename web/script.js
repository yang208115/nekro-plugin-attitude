let BASE_URL = 'http://localhost:8021/plugins/yang208115.nekro_plugin_attitude';


// 更新BASE_URL函数
function updateBaseUrl() {
    const ipInput = document.getElementById('ip-input');
    const newHost = ipInput.value.trim();
    if (newHost) {
        // 检测输入是否为域名或IP地址
        // 如果包含字母或者包含点且不是纯IP格式，则认为是域名
        const isDomain = /^[a-zA-Z]/.test(newHost) || (newHost.includes('.') && !/^\d+\.\d+\.\d+\.\d+$/.test(newHost));

        if (isDomain) {
            // 域名访问，通常使用80端口
            BASE_URL = `http://${newHost}/plugins/yang208115.nekro_plugin_attitude`;
        } else {
            // IP地址访问，使用8021端口
            BASE_URL = `http://${newHost}:8021/plugins/yang208115.nekro_plugin_attitude`;
        }
        console.log('BASE_URL已更新为:', BASE_URL);
    }
}

// 检查URL参数，判断是否显示开发信息
const urlParams = new URLSearchParams(window.location.search);
const showDevInfo = urlParams.has('dev');

// 显示响应结果
function showResponse(elementId, data, isError = false) {
    // 如果不是开发模式，只处理数据更新，不显示响应UI
    if (!showDevInfo) {
        // 如果是获取用户或群组的响应，更新统计数据
        if (elementId === 'users-response' && !isError) {
            updateUserStats(data.data);
        } else if (elementId === 'groups-response' && !isError) {
            updateGroupStats(data.data);
        }
        return;
    }
    
    // 开发模式下显示完整响应
    const containerElementId = elementId + '-container';
    const containerElement = document.getElementById(containerElementId);
    const element = document.getElementById(elementId);
    
    containerElement.style.display = 'block';
    element.className = `response ${isError ? 'error' : 'success'}`;
    
    if (typeof data === 'object') {
        element.textContent = JSON.stringify(data, null, 2);
    } else {
        element.textContent = data;
    }
    
    // 如果是获取用户或群组的响应，更新统计数据
    if (elementId === 'users-response' && !isError) {
        updateUserStats(data.data);
    } else if (elementId === 'groups-response' && !isError) {
        updateGroupStats(data.data);
    }
}

// 更新用户统计数据
function updateUserStats(data) {
    if (!Array.isArray(data)) return;
    
    // 更新用户总数
    document.getElementById('user-count').textContent = data.length;           
    // 计算消极态度数 - 不再需要更新到页面，但保留计算逻辑以备将来使用
    let negativeCount = 0;
    
    data.forEach(user => {
        if (user.attitude) {
            const attitudeValue = parseFloat(user.attitude);
            if (!isNaN(attitudeValue)) {
                if (attitudeValue < 0) {
                    negativeCount++;
                }
            } else if (typeof user.attitude === 'string') {
                // 对于非数字态度值，根据关键词判断
                const attitude = user.attitude.toLowerCase();
                if (attitude.includes('bad') || attitude.includes('dislike') || 
                    attitude.includes('negative') || attitude.includes('angry')) {
                    negativeCount++;
                }
            }
        }
    });
    
    // 消极态度数卡片已被移除，不再更新
}

// 更新群组统计数据
function updateGroupStats(data) {
    if (!Array.isArray(data)) return;
    
    // 更新群组总数
    document.getElementById('group-count').textContent = data.length;
    
    // 计算消极态度数 - 不再需要更新到页面，但保留计算逻辑以备将来使用
    let negativeCount = 0;
    
    data.forEach(group => {
        if (group.attitude) {
            const attitudeValue = parseFloat(group.attitude);
            if (!isNaN(attitudeValue)) {
                if (attitudeValue < 0) {
                    negativeCount++;
                }
            } else if (typeof group.attitude === 'string') {
                // 对于非数字态度值，根据关键词判断
                const attitude = group.attitude.toLowerCase();
                if (attitude.includes('bad') || attitude.includes('dislike') || 
                    attitude.includes('negative') || attitude.includes('angry')) {
                    negativeCount++;
                }
            }
        }
    });
    
    // 消极态度数卡片已被移除，不再更新
}

// 获取所有用户态度
let allUsers = [];
let filteredUsers = [];
let currentUserPage = 1;
let usersPerPage = 10;
let userSortColumn = 0;
let userSortDirection = 'asc';

async function getAllUsers() {
    try {
        const response = await fetch(`${BASE_URL}/users`);
        const data = await response.json();
        
        if (response.ok) {
            showResponse('users-response', {
                status: response.status,
                data: data
            });
            
            // 保存所有用户数据
            allUsers = data;
            filteredUsers = [...allUsers];
            
            // 显示表格容器
            document.getElementById('users-table-container').style.display = 'block';
            
            // 更新表格和分页
            updateUsersTable();
        } else {
            showResponse('users-response', {
                status: response.status,
                error: data
            }, true);
        }
    } catch (error) {
        showResponse('users-response', `网络错误: ${error.message}`, true);
    }
}

// 更新用户表格
function updateUsersTable() {
    const tableBody = document.getElementById('users-table-body');
    tableBody.innerHTML = '';
    
    // 计算当前页的数据
    const startIndex = (currentUserPage - 1) * usersPerPage;
    const endIndex = Math.min(startIndex + usersPerPage, filteredUsers.length);
    const currentPageData = filteredUsers.slice(startIndex, endIndex);
    
    // 更新显示信息
    document.getElementById('users-showing-start').textContent = filteredUsers.length > 0 ? startIndex + 1 : 0;
    document.getElementById('users-showing-end').textContent = endIndex;
    document.getElementById('users-total-count').textContent = filteredUsers.length;
    document.getElementById('users-current-page').textContent = currentUserPage;
    document.getElementById('users-total-pages').textContent = Math.ceil(filteredUsers.length / usersPerPage) || 1;
    
    // 禁用/启用分页按钮
    document.getElementById('users-prev-page').disabled = currentUserPage === 1;
    document.getElementById('users-next-page').disabled = currentUserPage >= Math.ceil(filteredUsers.length / usersPerPage);
    
    // 填充表格数据
    currentPageData.forEach(user => {
        const row = document.createElement('tr');
        
        // 用户ID列 - 显示完整QQ号
        const idCell = document.createElement('td');
        // 如果user.id是user_开头的格式，提取后面的数字部分
        let displayId = user.user_id;
        if (typeof user.user_id === 'string' && user.user_id.startsWith('user_')) {
            displayId = user.user_id.substring(5); // 去掉'user_'前缀
        }
        idCell.textContent = displayId;
        row.appendChild(idCell);
        
        const nameCell = document.createElement('td');
        nameCell.textContent = user.username || ('用户_' + (typeof user.user_id === 'string' ? user.user_id.substring(0, 5) : user.user_id));
        row.appendChild(nameCell);
        
        // 称呼列
        const nicknameCell = document.createElement('td');
        nicknameCell.textContent = user.nickname || user.username || '无称呼';
        row.appendChild(nicknameCell);
        
        // 态度值列
        const attitudeCell = document.createElement('td');
        if (user.attitude === null || user.attitude === undefined) {
            attitudeCell.textContent = '无态度';
            attitudeCell.classList.add('text-muted');
        } else {
            attitudeCell.textContent = user.attitude;
            if (parseFloat(user.attitude) > 0) {
                attitudeCell.classList.add('text-success');
            } else if (parseFloat(user.attitude) < 0) {
                attitudeCell.classList.add('text-danger');
            }
        }
        row.appendChild(attitudeCell);
        
        // 关系列
        const relationCell = document.createElement('td');
        if (user.relationship) {
            relationCell.textContent = user.relationship;
            if (user.relationship.toLowerCase() === 'friend') {
                relationCell.classList.add('text-success');
            } else if (user.relationship.toLowerCase() === 'enemy') {
                relationCell.classList.add('text-danger');
            }
        } else {
            relationCell.textContent = '未知';
            relationCell.classList.add('text-muted');
        }
        row.appendChild(relationCell);
        
        // 其他信息列
        const infoCell = document.createElement('td');
        const infoText = document.createElement('small');
        infoText.classList.add('text-muted');
        if (user.other) {
            infoText.textContent = user.other;
        } else {
            infoText.textContent = '最后更新: ' + new Date().toLocaleString();
        }
        infoCell.appendChild(infoText);
        row.appendChild(infoCell);
        
        // 操作列
        const actionCell = document.createElement('td');
        const editBtn = document.createElement('button');
        editBtn.classList.add('btn', 'btn-sm', 'btn-primary', 'mr-2');
        editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
        editBtn.style.marginRight = '5px';
        editBtn.onclick = function() {
            document.getElementById('user-id').value = user.user_id;
            document.getElementById('user-attitude').value = user.attitude !== null ? user.attitude : '';
            document.getElementById('user-relationship').value = user.relationship || '';
            document.getElementById('user-other').value = user.other || '';
            document.getElementById('user-username').value = user.username || ''; // 新增
            document.getElementById('user-nickname').value = user.nickname || ''; // 新增
        };
        
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('btn', 'btn-sm', 'btn-danger');
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
        deleteBtn.onclick = function() {
            if (confirm('确定要删除此用户态度吗？')) {
                deleteUser(user.user_id);
            }
        };
        
        actionCell.appendChild(editBtn);
        actionCell.appendChild(deleteBtn);
        row.appendChild(actionCell);
        
        tableBody.appendChild(row);
    });
}

// 筛选用户表格
function filterUserTable() {
    const searchTerm = document.getElementById('user-search').value.toLowerCase();
    
    filteredUsers = allUsers.filter(user => {
        // 搜索条件 - 匹配QQ号、用户名、称呼或关系
        const matchesSearch = (typeof user.user_id === 'string' ? user.user_id.toLowerCase().includes(searchTerm) : String(user.user_id).toLowerCase().includes(searchTerm)) ||
                              (user.username && user.username.toLowerCase().includes(searchTerm)) ||
                              (user.nickname && user.nickname.toLowerCase().includes(searchTerm)) ||
                              (user.relationship && user.relationship.toLowerCase().includes(searchTerm));
        
        return matchesSearch;
    });
    
    // 重置到第一页并更新表格
    currentUserPage = 1;
    updateUsersTable();
}

// 排序用户表格
function sortUserTable(columnIndex) {
    if (userSortColumn === columnIndex) {
        // 如果点击的是当前排序列，则切换排序方向
        userSortDirection = userSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        // 如果点击的是新列，则设置为升序
        userSortColumn = columnIndex;
        userSortDirection = 'asc';
    }
    
    filteredUsers.sort((a, b) => {
        let valueA, valueB;
        
        if (columnIndex === 0) {
            // 按QQ号排序
            valueA = a.id;
            valueB = b.id;
        } else if (columnIndex === 1) {
            // 按用户名称排序
            valueA = a.username || ('用户_' + (typeof a.user_id === 'string' ? a.user_id.substring(0, 5) : a.user_id));
            valueB = b.username || ('用户_' + (typeof b.user_id === 'string' ? b.user_id.substring(0, 5) : b.user_id));
        } else if (columnIndex === 4) {
            // 按称呼排序
            valueA = a.nickname || a.username || '无称呼';
            valueB = b.nickname || b.username || '无称呼';
        } else if (columnIndex === 2) {
            // 按态度值排序，将null值视为最小
            valueA = a.attitude === null ? -Infinity : parseFloat(a.attitude);
            valueB = b.attitude === null ? -Infinity : parseFloat(b.attitude);
        } else if (columnIndex === 3) {
            // 按关系排序
            valueA = a.relationship || '';
            valueB = b.relationship || '';
        }
        
        // 根据排序方向比较
        if (userSortDirection === 'asc') {
            return valueA > valueB ? 1 : -1;
        } else {
            return valueA < valueB ? 1 : -1;
        }
    });
    
    updateUsersTable();
}

// 更改每页显示数量
function changeUsersPerPage() {
    usersPerPage = parseInt(document.getElementById('users-per-page').value);
    currentUserPage = 1; // 重置到第一页
    updateUsersTable();
}

// 上一页
function prevUsersPage() {
    if (currentUserPage > 1) {
        currentUserPage--;
        updateUsersTable();
    }
}

// 下一页
function nextUsersPage() {
    if (currentUserPage < Math.ceil(filteredUsers.length / usersPerPage)) {
        currentUserPage++;
        updateUsersTable();
    }
}

// 导出用户数据
function exportUserData() {
    // 创建JSON数据
    const jsonData = {
        version: "0.0.2",
        type: "users",
        data: filteredUsers.map(user => ({
            user_id: user.user_id,
            username: user.username || null,
            nickname: user.nickname || null,
            attitude: user.attitude === null ? null : user.attitude,
            relationship: user.relationship || null,
            other: user.other || null
        }))
    };
    
    // 将JSON对象转换为字符串
    const jsonString = JSON.stringify(jsonData, null, 2);
    
    // 创建下载链接并触发点击
    const blob = new Blob([jsonString], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "用户态度数据.json");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// 更新用户态度
async function updateUser() {
    const userId = document.getElementById('user-id').value;
    const attitudeValue = document.getElementById('user-attitude').value;
    
    if (!userId) {
        showResponse('user-update-response', '请输入QQ号', true);
        return;
    }
    
    // 处理态度值，如果为空则传入 null (后端会解析为 None)
    const attitude = attitudeValue.trim() === '' ? null : attitudeValue;
    const relationship = document.getElementById('user-relationship').value;
    const other = document.getElementById('user-other').value;
    const username = document.getElementById('user-username').value; // 新增
    const nickname = document.getElementById('user-nickname').value; // 新增
    
    const requestBody = {};
    if (attitude !== null) requestBody.attitude = attitude;
    requestBody.relationship = relationship;
    requestBody.other = other;
    requestBody.username = username;
    requestBody.nickname = nickname;

    
    try {
        const response = await fetch(`${BASE_URL}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResponse('user-update-response', {
                status: response.status,
                message: '用户态度更新成功',
                data: data
            });
            
            // 更新后刷新用户列表
            getAllUsers();
        } else {
            showResponse('user-update-response', {
                status: response.status,
                error: data
            }, true);
        }
    } catch (error) {
        showResponse('user-update-response', `网络错误: ${error.message}`, true);
    }
    showToast("更新完成", 3000);
}

// 获取所有群组态度
let allGroups = [];
let filteredGroups = [];
let currentGroupPage = 1;
let groupsPerPage = 10;
let groupSortColumn = 0;
let groupSortDirection = 'asc';

async function getAllGroups() {
    try {
        const response = await fetch(`${BASE_URL}/groups`);
        const data = await response.json();
        
        if (response.ok) {
            showResponse('groups-response', {
                status: response.status,
                data: data
            });
            
            // 保存所有群组数据
            allGroups = data;
            filteredGroups = [...allGroups];
            
            // 显示表格容器
            document.getElementById('groups-table-container').style.display = 'block';
            
            // 更新表格和分页
            updateGroupsTable();
        } else {
            showResponse('groups-response', {
                status: response.status,
                error: data
            }, true);
        }
    } catch (error) {
        showResponse('groups-response', `网络错误: ${error.message}`, true);
    }
}

// 更新群组表格
function updateGroupsTable() {
    const tableBody = document.getElementById('groups-table-body');
    tableBody.innerHTML = '';
    
    // 计算当前页的数据
    const startIndex = (currentGroupPage - 1) * groupsPerPage;
    const endIndex = Math.min(startIndex + groupsPerPage, filteredGroups.length);
    const currentPageData = filteredGroups.slice(startIndex, endIndex);
    
    // 更新显示信息
    document.getElementById('groups-showing-start').textContent = filteredGroups.length > 0 ? startIndex + 1 : 0;
    document.getElementById('groups-showing-end').textContent = endIndex;
    document.getElementById('groups-total-count').textContent = filteredGroups.length;
    document.getElementById('groups-current-page').textContent = currentGroupPage;
    document.getElementById('groups-total-pages').textContent = Math.ceil(filteredGroups.length / groupsPerPage) || 1;
    
    // 禁用/启用分页按钮
    document.getElementById('groups-prev-page').disabled = currentGroupPage === 1;
    document.getElementById('groups-next-page').disabled = currentGroupPage >= Math.ceil(filteredGroups.length / groupsPerPage);
    
    // 填充表格数据
    currentPageData.forEach(group => {
        const row = document.createElement('tr');
        
        // 群组ID列 - 显示纯数字群号
        const idCell = document.createElement('td');
        // 如果group.id是group_开头的格式，提取后面的数字部分
        let displayId = group.group_id;
        if (typeof group.group_id === 'string' && group.group_id.startsWith('group_')) {
            displayId = group.group_id.substring(6); // 去掉'group_'前缀
        }
        idCell.textContent = displayId;
        row.appendChild(idCell);
        
        // 群组名称列
        const nameCell = document.createElement('td');
        if (group.channel_name) {
            nameCell.textContent = group.channel_name;
        } else {
            // 如果没有名称，则使用ID的一部分或其他信息作为默认名称
            nameCell.textContent = 'group_' + (typeof group.group_id === 'string' ? group.group_id.substring(0, 5) : group.group_id);
            nameCell.classList.add('text-muted');
        }
        row.appendChild(nameCell);
        
        // 态度值列
        const attitudeCell = document.createElement('td');
        if (group.attitude === null || group.attitude === undefined) {
            attitudeCell.textContent = '无态度';
            attitudeCell.classList.add('text-muted');
        } else {
            attitudeCell.textContent = group.attitude;
            if (parseFloat(group.attitude) > 0) {
                attitudeCell.classList.add('text-success');
            } else if (parseFloat(group.attitude) < 0) {
                attitudeCell.classList.add('text-danger');
            }
        }
        row.appendChild(attitudeCell);
        
        // 其他信息列
        const infoCell = document.createElement('td');
        const infoText = document.createElement('small');
        infoText.classList.add('text-muted');
        if (group.other) {
            infoText.textContent = group.other;
        } else {
            infoText.textContent = '最后更新: ' + new Date().toLocaleString();
        }
        infoCell.appendChild(infoText);
        row.appendChild(infoCell);
        
        // 操作列
        const actionCell = document.createElement('td');
        const editBtn = document.createElement('button');
        editBtn.classList.add('btn', 'btn-sm', 'btn-primary', 'mr-2');
        editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
        editBtn.style.marginRight = '5px';
        editBtn.onclick = function() {
            document.getElementById('group-id').value = group.group_id;
            document.getElementById('group-attitude').value = group.attitude !== null ? group.attitude : '';
        };
        
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('btn', 'btn-sm', 'btn-danger');
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
        deleteBtn.onclick = function() {
            if (confirm('确定要删除此群组态度吗？')) {
                deleteGroup(group.group_id);
            }
        };
        
        actionCell.appendChild(editBtn);
        actionCell.appendChild(deleteBtn);
        row.appendChild(actionCell);
        
        tableBody.appendChild(row);
    });
}

// 筛选群组表格
function filterGroupTable() {
    const searchTerm = document.getElementById('group-search').value.toLowerCase();
    
    filteredGroups = allGroups.filter(group => {
        // 搜索条件 - 匹配群号或群组名称
        const groupName = group.channel_name || ('group_' + (typeof group.group_id === 'string' ? group.group_id.substring(0, 5) : group.group_id));
        
        // 处理群号搜索 - 如果group_id是group_开头的格式，提取后面的数字部分进行匹配
        let searchableGroupId = group.group_id;
        if (typeof group.group_id === 'string' && group.group_id.startsWith('group_')) {
            searchableGroupId = group.group_id.substring(6); // 去掉'group_'前缀
        }
        
        const matchesSearch = (typeof searchableGroupId === 'string' ? searchableGroupId.toLowerCase() : String(searchableGroupId).toLowerCase()).includes(searchTerm) ||
                                (typeof groupName === 'string' ? groupName.toLowerCase() : String(groupName).toLowerCase()).includes(searchTerm);
        
        return matchesSearch;
    });
    
    // 重置到第一页并更新表格
    currentGroupPage = 1;
    updateGroupsTable();
}

// 排序群组表格
function sortGroupTable(columnIndex) {
    if (groupSortColumn === columnIndex) {
        // 如果点击的是当前排序列，则切换排序方向
        groupSortDirection = groupSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        // 如果点击的是新列，则设置为升序
        groupSortColumn = columnIndex;
        groupSortDirection = 'asc';
    }
    
    filteredGroups.sort((a, b) => {
        let valueA, valueB;
        
        if (columnIndex === 0) {
            // 按群号排序
            valueA = a.group_id;
            valueB = b.group_id;
        } else if (columnIndex === 1) {
            // 按群组名称排序
            valueA = a.channel_name || ('group_' + (typeof a.group_id === 'string' ? a.group_id.substring(0, 5) : a.group_id));
            valueB = b.channel_name || ('group_' + (typeof b.group_id === 'string' ? b.group_id.substring(0, 5) : b.group_id));
        } else if (columnIndex === 2) {
            // 按态度值排序，将null值视为最小
            valueA = a.attitude === null ? -Infinity : parseFloat(a.attitude);
            valueB = b.attitude === null ? -Infinity : parseFloat(b.attitude);
        }
        
        // 根据排序方向比较
        if (groupSortDirection === 'asc') {
            return valueA > valueB ? 1 : -1;
        } else {
            return valueA < valueB ? 1 : -1;
        }
    });
    
    updateGroupsTable();
}

// 更改每页显示数量
function changeGroupsPerPage() {
    groupsPerPage = parseInt(document.getElementById('groups-per-page').value);
    currentGroupPage = 1; // 重置到第一页
    updateGroupsTable();
}

// 上一页
function prevGroupsPage() {
    if (currentGroupPage > 1) {
        currentGroupPage--;
        updateGroupsTable();
    }
}

// 下一页
function nextGroupsPage() {
    if (currentGroupPage < Math.ceil(filteredGroups.length / groupsPerPage)) {
        currentGroupPage++;
        updateGroupsTable();
    }
}

// 导出群组数据
function exportGroupData() {
    // 创建JSON数据
    const jsonData = {
        version: "0.0.2",
        type: "groups",
        data: filteredGroups.map(group => ({
            id: group.group_id,
            name: group.channel_name || ('group_' + (typeof group.group_id === 'string' ? group.group_id.substring(0, 5) : group.group_id)),
            attitude: group.attitude === null ? null : group.attitude,
            other: group.other || null
        }))
    };
    
    // 将JSON对象转换为字符串
    const jsonString = JSON.stringify(jsonData, null, 2);
    
    // 创建下载链接并触发点击
    const blob = new Blob([jsonString], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "群组态度数据.json");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// 更新群组态度
async function updateGroup() {
    const groupId = document.getElementById('group-id').value;
    const attitudeValue = document.getElementById('group-attitude').value;
    
    if (!groupId) {
        showResponse('group-update-response', '请输入群号', true);
        return;
    }
    
    // 处理态度值，如果为空则传入 null (后端会解析为 None)
    const attitude = attitudeValue.trim() === '' ? null : attitudeValue;
    const other = document.getElementById('group-other').value;
    
    const requestBody = {};
    if (attitude !== null) requestBody.attitude = attitude;
    if (other) requestBody.other = other;
    
    try {
        const response = await fetch(`${BASE_URL}/groups/${groupId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResponse('group-update-response', {
                status: response.status,
                message: '群组态度更新成功',
                data: data
            });
            
            // 更新后刷新群组列表
            getAllGroups();
        } else {
            showResponse('group-update-response', {
                status: response.status,
                error: data
            }, true);
        }
    } catch (error) {
        showResponse('group-update-response', `网络错误: ${error.message}`, true);
    }
}

// 删除用户态度
async function deleteUser(userId) {
    if (!userId) {
        alert('QQ号不能为空');
        return;
    }
    
    try {
        const response = await fetch(`${BASE_URL}/users/${userId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            alert(`删除成功: ${data.message}`);
            // 刷新用户列表
            getAllUsers();
        } else {
            alert(`删除失败: ${data.message || (data.detail ? data.detail : '未知错误')}`);
        }
    } catch (error) {
        alert(`删除失败: ${error.message}`);
    }
}

// 删除群组态度
async function deleteGroup(groupId) {
    if (!groupId) {
        alert('群号不能为空');
        return;
    }
    
    try {
        const response = await fetch(`${BASE_URL}/groups/${groupId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            alert(`删除成功: ${data.message}`);
            // 刷新群组列表
            getAllGroups();
        } else {
            alert(`删除失败: ${data.message || (data.detail ? data.detail : '未知错误')}`);
        }
    } catch (error) {
        alert(`删除失败: ${error.message}`);
    }
}

// 运行所有测试
async function runAllTests() {
    const containerElement = document.getElementById('batch-response-container');
    const element = document.getElementById('batch-response');
    
    // 只在开发模式下显示批量测试响应
    if (showDevInfo) {
        containerElement.style.display = 'block';
        element.className = 'response info';
        element.textContent = '正在运行批量测试...\n';
    }
    
    const tests = [
        { name: '获取所有用户', func: () => fetch(`${BASE_URL}/users`) },
        { name: '获取所有群组', func: () => fetch(`${BASE_URL}/groups`) },
        { name: '测试用户更新', func: () => fetch(`${BASE_URL}/users/test123`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ attitude: "0.5", relationship: 'friend', other: 'test user' })
        })},
        { name: '测试群组更新', func: () => fetch(`${BASE_URL}/groups/test456`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ attitude: "-0.5", other: 'test group' })
        })}
    ];
    
    let results = [];
    
    for (const test of tests) {
        try {
            const response = await test.func();
            const data = await response.json();
            results.push({
                test: test.name,
                status: response.status,
                success: response.ok,
                data: data
            });
        } catch (error) {
            results.push({
                test: test.name,
                status: 'ERROR',
                success: false,
                error: error.message
            });
        }
    }
    
    showResponse('batch-response', {
        message: '批量测试完成',
        results: results
    });
    
    // 刷新用户和群组列表
    getAllUsers();
    getAllGroups();
}

// 页面加载完成后执行
window.addEventListener('load', () => {
    // 从地址栏获取主机名并设置到IP输入框
    const ipInput = document.getElementById('ip-input');
    if (ipInput) {
        const urlParams = new URLSearchParams(window.location.search);
        const ip = urlParams.get('ip');
        if (ip) {
            ipInput.value = ip;
        } else {
            // 如果URL中没有指定IP，尝试从当前主机名获取
            const currentHostname = window.location.hostname;
            if (currentHostname && currentHostname !== 'localhost' && currentHostname !== '127.0.0.1') {
                ipInput.value = currentHostname;
            }
        }
        updateBaseUrl();
    }

    getAllUsers();
    getAllGroups();

    // 默认打开用户管理标签页
    document.getElementById('users-tab').style.display = 'block';

    // 添加刷新按钮事件
    const refreshButton = document.querySelector('.header .btn-primary');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            getAllUsers();
            getAllGroups();
        });
    }
});

// 标签页切换函数
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tab-button");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// 显示非侵入式消息提示
function showToast(message, duration = 3000) {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        Object.assign(toastContainer.style, {
            position: 'fixed',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: '1000',
            display: 'flex',
            flexDirection: 'column-reverse',
            alignItems: 'center'
        });
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;
    Object.assign(toast.style, {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '10px 20px',
        borderRadius: '5px',
        marginBottom: '10px',
        opacity: '0',
        transition: 'opacity 0.5s ease-in-out, transform 0.5s ease-in-out',
        transform: 'translateY(20px)',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
        textAlign: 'center'
    });
    toastContainer.appendChild(toast);

    // 强制回流以应用初始状态
    void toast.offsetWidth;

    // 渐入动画
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';

    setTimeout(() => {
        // 渐出动画
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.addEventListener('transitionend', () => {
            toast.remove();
            if (toastContainer.children.length === 0) {
                toastContainer.remove();
            }
        }, { once: true });
    }, duration);
}