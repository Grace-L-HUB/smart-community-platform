//index.js
const app = getApp()

Page({
  data: {
    // 用户信息
    userInfo: {
      name: '张先生',
      address: '幸福里小区 3栋2单元1001室',
      role: '业主'
    },
    // 公告列表
    announcements: [
      {
        id: '1',
        title: '关于小区电梯维护的通知',
        tag: '通知',
        time: '今天'
      },
      {
        id: '2',
        title: '社区消防安全知识讲座',
        tag: '活动',
        time: '昨天'
      }
    ],
    // 报修工单
    repairOrders: [
      {
        id: '1',
        desc: '客厅灯不亮',
        status: '待处理'
      }
    ]
  },
  
  onLoad: function() {
    // 初始化数据
    this.loadUserInfo();
    this.loadAnnouncements();
    this.loadRepairOrders();
  },
  
  // 加载用户信息
  loadUserInfo: function() {
    // 这里可以调用后端API获取用户信息
    // 暂时使用模拟数据
  },
  
  // 加载公告信息
  loadAnnouncements: function() {
    // 这里可以调用后端API获取公告列表
    // 暂时使用模拟数据
  },
  
  // 加载报修工单
  loadRepairOrders: function() {
    // 这里可以调用后端API获取报修工单
    // 暂时使用模拟数据
  },
  
  // 跳转到公告列表页
  goToAnnouncements: function() {
    wx.navigateTo({
      url: '/pages/announcements/index'
    })
  },
  
  // 跳转到报修页面
  goToRepair: function() {
    wx.navigateTo({
      url: '/pages/repair/index'
    })
  },
  
  // 跳转到缴费查询
  goToPayment: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },
  
  // 跳转到商户服务
  goToMerchants: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  }
})
