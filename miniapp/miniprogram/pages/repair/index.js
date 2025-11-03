// 报修页面JS
Page({
  data: {
    repairTypes: ['水管维修', '电路维修', '家电维修', '家具维修', '其他维修'],
    repairTypeIndex: 0,
    location: '',
    description: '',
    images: [],
    date: '',
    startDate: ''
  },

  onLoad: function() {
    // 设置最小可选日期为今天
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayStr = `${year}-${month}-${day}`;
    
    this.setData({
      startDate: todayStr
    });
  },

  // 报修类型选择
  bindTypeChange: function(e) {
    this.setData({
      repairTypeIndex: e.detail.value
    });
  },

  // 位置输入
  inputLocation: function(e) {
    this.setData({
      location: e.detail.value
    });
  },

  // 描述输入
  inputDescription: function(e) {
    this.setData({
      description: e.detail.value
    });
  },

  // 日期选择
  bindDateChange: function(e) {
    this.setData({
      date: e.detail.value
    });
  },

  // 上传照片
  uploadImage: function() {
    const that = this;
    wx.chooseMedia({
      count: 3 - that.data.images.length,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      maxDuration: 30,
      camera: 'back',
      success(res) {
        const tempFiles = res.tempFiles;
        const newImages = tempFiles.map(file => file.tempFilePath);
        
        that.setData({
          images: [...that.data.images, ...newImages]
        });
      }
    });
  },

  // 删除照片
  deleteImage: function(e) {
    const index = e.currentTarget.dataset.index;
    const images = this.data.images;
    images.splice(index, 1);
    
    this.setData({
      images: images
    });
  },

  // 提交报修
  submitRepair: function(e) {
    const { location, description, repairTypes, repairTypeIndex } = this.data;
    
    // 表单验证
    if (!location) {
      wx.showToast({
        title: '请填写报修位置',
        icon: 'none'
      });
      return;
    }
    
    if (!description) {
      wx.showToast({
        title: '请填写问题描述',
        icon: 'none'
      });
      return;
    }
    
    // 构造报修数据
    const repairData = {
      type: repairTypes[repairTypeIndex],
      location: location,
      description: description,
      images: this.data.images,
      appointmentDate: this.data.date,
      status: '待处理',
      createTime: new Date().toLocaleString('zh-CN')
    };
    
    // 模拟提交到服务器
    wx.showLoading({
      title: '提交中...',
    });
    
    // 模拟网络请求延迟
    setTimeout(() => {
      // 在实际项目中，这里应该调用API接口提交数据
      console.log('提交报修数据:', repairData);
      
      wx.hideLoading();
      wx.showToast({
        title: '报修提交成功',
        icon: 'success'
      });
      
      // 提交成功后返回上一页
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }, 1000);
  },

  // 返回上一页
  goBack: function() {
    wx.navigateBack();
  }
});