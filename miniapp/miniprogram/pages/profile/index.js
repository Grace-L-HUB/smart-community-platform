// 个人中心页面JS
Page({
  data: {
    userInfo: {
      name: '张先生',
      role: '业主',
      community: '幸福里社区',
      building: '1栋',
      room: '101室',
      avatar: ''
    },
    orderCount: 3
  },

  onLoad: function() {
    // 加载用户信息
    this.loadUserInfo();
    // 加载报修订单数量
    this.loadOrderCount();
  },

  // 加载用户信息
  loadUserInfo: function() {
    // 在实际项目中，这里应该从本地存储或服务器获取用户信息
    const userInfo = wx.getStorageSync('userInfo') || this.data.userInfo;
    this.setData({
      userInfo: userInfo
    });
  },

  // 加载订单数量
  loadOrderCount: function() {
    // 在实际项目中，这里应该从服务器获取订单数量
    // 模拟数据
    this.setData({
      orderCount: 3
    });
  },

  // 跳转到用户信息详情页
  goToUserInfo: function() {
    wx.navigateTo({
      url: '/pages/userInfo/index'
    });
  },

  // 跳转到我的报修页面
  goToOrders: function() {
    wx.navigateTo({
      url: '/pages/myOrders/index'
    });
  },

  // 跳转到缴费记录页面
  goToPayment: function() {
    wx.navigateTo({
      url: '/pages/payment/index'
    });
  },

  // 跳转到物业服务页面
  goToServices: function() {
    wx.navigateTo({
      url: '/pages/services/index'
    });
  },

  // 跳转到意见反馈页面
  goToFeedback: function() {
    wx.navigateTo({
      url: '/pages/feedback/index'
    });
  },

  // 跳转到设置页面
  goToSettings: function() {
    wx.navigateTo({
      url: '/pages/settings/index'
    });
  },

  // 跳转到关于我们页面
  goToAbout: function() {
    wx.navigateTo({
      url: '/pages/about/index'
    });
  },

  // 退出登录
  logout: function() {
    const that = this;
    wx.showModal({
      title: '确认退出',
      content: '您确定要退出登录吗？',
      success(res) {
        if (res.confirm) {
          // 清除用户信息
          wx.removeStorageSync('userInfo');
          wx.removeStorageSync('token');
          
          // 显示退出成功提示
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
          
          // 跳转到登录页面（实际项目中应该跳转到登录页）
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/index/index'
            });
            // 重置用户信息
            that.setData({
              userInfo: {
                name: '未登录',
                role: '',
                community: '',
                building: '',
                room: '',
                avatar: ''
              },
              orderCount: 0
            });
          }, 1500);
        }
      }
    });
  }
});